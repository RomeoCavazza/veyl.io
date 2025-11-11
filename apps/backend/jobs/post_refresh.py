"""
Job utilitaire pour rafraîchir les posts d'un projet :
- Récupère chaque post lié (créateurs du projet)
- Appelle l'oEmbed Instagram pour enrichir media_url / payload / métriques
- (Optionnel) propage vers Meilisearch / Supabase si les variables sont configurées

Usage CLI :
    python -m apps.backend.jobs.post_refresh --project PROJECT_UUID --limit 20
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from datetime import datetime
from typing import Iterable, List, Optional, Set, Dict, Any
from uuid import UUID
import re

import requests
from sqlalchemy.orm import Session

from core.config import settings
from db.base import SessionLocal
from db.models import (
    Post,
    ProjectCreator,
    PostHashtag,
    Hashtag,
    Platform,
    Project,
    ProjectHashtag,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


GRAPH_BASE_URL = "https://graph.facebook.com/v21.0/instagram_oembed"
GRAPH_MEDIA_URL = "https://graph.facebook.com/v21.0"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE")


def _ensure_permalink(post: Post) -> Optional[str]:
    """Déduire le permalink Instagram à partir du post."""
    if post.media_url and post.media_url.startswith("http"):
        return post.media_url
    external = post.external_id or post.id
    if not external:
        return None
    if external.startswith("http"):
        return external
    # Reconstruire le permalink standard
    slug = external.strip().strip("/")
    if not slug:
        return None
    return f"https://www.instagram.com/p/{slug}/"


HASHTAG_PATTERN = re.compile(r"#([\w\d_]+)", re.UNICODE)


def _ensure_platform(session: Session, name: str) -> Platform:
    platform = (
        session.query(Platform)
        .filter(Platform.name == name.lower())
        .first()
    )
    if not platform:
        platform = Platform(name=name.lower())
        session.add(platform)
        session.flush()
    return platform


def _upsert_post_hashtags(
    session: Session,
    post: Post,
    caption: Optional[str],
    platform_name: str,
) -> None:
    if not caption:
        return

    hashtags: Set[str] = set(
        match.group(1).lower()
        for match in HASHTAG_PATTERN.finditer(caption)
    )
    if not hashtags:
        return

    platform = _ensure_platform(session, platform_name)
    for tag in hashtags:
        hashtag = (
            session.query(Hashtag)
            .filter(Hashtag.name == tag)
            .first()
        )
        if not hashtag:
            hashtag = Hashtag(
                name=tag,
                platform_id=platform.id,
            )
            session.add(hashtag)
            session.flush()

        existing_link = (
            session.query(PostHashtag)
            .filter(
                PostHashtag.post_id == post.id,
                PostHashtag.hashtag_id == hashtag.id,
            )
            .first()
        )
        if not existing_link:
            session.add(
                PostHashtag(
                    post_id=post.id,
                    hashtag_id=hashtag.id,
                )
            )


def fetch_oembed(permalink: str) -> Optional[dict]:
    if not settings.IG_ACCESS_TOKEN:
        logger.error("IG_ACCESS_TOKEN manquant : impossible d'appeler l'oEmbed.")
        return None
    try:
        resp = requests.get(
            GRAPH_BASE_URL,
            params={
                "url": permalink,
                "access_token": settings.IG_ACCESS_TOKEN,
                "maxwidth": 540,
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        logger.error("oEmbed error [%s]: %s", permalink, exc)
        return None


def fetch_media_details(media_id: Optional[str]) -> Optional[dict]:
    if not media_id:
        return None
    if not settings.IG_ACCESS_TOKEN:
        return None
    try:
        resp = requests.get(
            f"{GRAPH_MEDIA_URL}/{media_id}",
            params={
                "fields": "like_count,comments_count,timestamp,permalink,media_url,thumbnail_url,media_type,caption",
                "access_token": settings.IG_ACCESS_TOKEN,
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        logger.warning("Graph media fetch failed for %s: %s", media_id, exc)
        return None


def push_meilisearch(records: List[dict]) -> None:
    if not records:
        return
    if not settings.MEILI_MASTER_KEY:
        logger.warning("MEILI_MASTER_KEY absent → skip Meilisearch push.")
        return
    try:
        resp = requests.post(
            f"{settings.MEILI_HOST}/indexes/{settings.MEILI_INDEX}/documents?primaryKey=id",
            headers={
                "X-Meili-API-Key": settings.MEILI_MASTER_KEY,
                "Content-Type": "application/json",
            },
            data=json.dumps(records),
            timeout=15,
        )
        resp.raise_for_status()
        logger.info("Meilisearch push: %s", resp.json())
    except requests.RequestException as exc:
        logger.error("Meilisearch push failed: %s", exc)


def push_supabase(records: List[dict]) -> None:
    if not records:
        return
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE:
        logger.warning("SUPABASE_URL / SUPABASE_SERVICE_ROLE absents → skip Supabase push.")
        return
    try:
        resp = requests.post(
            f"{SUPABASE_URL.rstrip('/')}/rest/v1/posts_vector",
            headers={
                "apikey": SUPABASE_SERVICE_ROLE,
                "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE}",
                "Content-Type": "application/json",
            },
            data=json.dumps(records),
            timeout=15,
        )
        resp.raise_for_status()
        logger.info("Supabase push: %s", resp.text)
    except requests.RequestException as exc:
        logger.error("Supabase push failed: %s", exc)


def _iter_project_posts(session: Session, project_id: Optional[str], limit: int) -> Iterable[Post]:
    if not project_id:
        return (
            session.query(Post)
            .order_by(Post.fetched_at.desc().nullslast(), Post.posted_at.desc().nullslast())
            .limit(limit)
            .all()
        )

    creator_usernames = [
        row.creator_username
        for row in session.query(ProjectCreator)
        .filter(ProjectCreator.project_id == project_id)
        .all()
    ]
    hashtag_ids = [
        row.hashtag_id
        for row in session.query(ProjectHashtag)
        .filter(ProjectHashtag.project_id == project_id)
        .all()
    ]

    post_ids: Set[str] = set()
    if creator_usernames:
        for (post_id,) in (
            session.query(Post.id)
            .filter(Post.author.in_(creator_usernames))
            .order_by(Post.fetched_at.desc().nullslast(), Post.posted_at.desc().nullslast())
            .limit(limit * 2)
        ):
            post_ids.add(post_id)

    if hashtag_ids:
        for (post_id,) in (
            session.query(PostHashtag.post_id)
            .filter(PostHashtag.hashtag_id.in_(hashtag_ids))
            .limit(limit * 2)
        ):
            post_ids.add(post_id)

    if not post_ids:
        logger.warning("Aucun contenu associé au projet %s.", project_id)
        return []

    return (
        session.query(Post)
        .filter(Post.id.in_(post_ids))
        .order_by(Post.fetched_at.desc().nullslast(), Post.posted_at.desc().nullslast())
        .limit(limit)
        .all()
    )


def refresh_posts(project_id: Optional[str], limit: int = 20) -> None:
    session = SessionLocal()
    try:
        posts = list(_iter_project_posts(session, project_id, limit))
        if not posts:
            logger.info("Aucun post à rafraîchir.")
            return

        logger.info("Rafraîchissement de %s posts…", len(posts))
        meili_records: List[dict] = []
        supabase_records: List[dict] = []

        for post in posts:
            permalink = _ensure_permalink(post)
            if not permalink:
                logger.warning("Impossible de déterminer le permalink pour %s", post.id)
                continue

            payload = fetch_oembed(permalink)
            if not payload:
                continue

            media_id = payload.get("media_id")
            media_details = fetch_media_details(media_id)

            thumbnail = (
                (media_details or {}).get("media_url")
                or (media_details or {}).get("thumbnail_url")
                or payload.get("thumbnail_url")
            )
            author_name = payload.get("author_name") or post.author
            caption = (
                (media_details or {}).get("caption")
                or payload.get("title")
                or post.caption
            )

            if thumbnail:
                post.media_url = thumbnail
            post.caption = caption
            post.author = author_name
            combined_payload: Dict[str, Any] = dict(payload)
            if media_details:
                combined_payload["media_details"] = media_details
            post.api_payload = json.dumps(combined_payload)
            post.fetched_at = datetime.utcnow()

            platform_name = (payload.get("provider_name") or "instagram").lower()
            _upsert_post_hashtags(
                session=session,
                post=post,
                caption=caption,
                platform_name=platform_name,
            )

            # Mettre à jour quelques métriques si disponibles
            metrics = {
                "like_count": (media_details or {}).get("like_count"),
                "comment_count": (media_details or {}).get("comments_count"),
            }
            metrics_clean = {k: v for k, v in metrics.items() if v is not None}
            post.metrics = json.dumps(metrics_clean) if metrics_clean else None

            timestamp = (media_details or {}).get("timestamp")
            if timestamp:
                try:
                    post.posted_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                except ValueError:
                    logger.debug("Timestamp invalide pour %s: %s", post.id, timestamp)

            meili_records.append(
                {
                    "id": post.id,
                    "author": post.author,
                    "caption": post.caption,
                    "platform": "instagram",
                    "media_url": post.media_url,
                    "permalink": (media_details or {}).get("permalink") or permalink,
                    "posted_at": post.posted_at.isoformat() if post.posted_at else None,
                    "like_count": metrics_clean.get("like_count") if metrics_clean else None,
                    "comment_count": metrics_clean.get("comment_count") if metrics_clean else None,
                }
            )
            supabase_records.append(
                {
                    "id": post.id,
                    "provider": "instagram",
                    "url": (media_details or {}).get("permalink") or permalink,
                    "creator": post.author,
                    "title": post.caption,
                    "thumbnail": post.media_url,
                    "last_fetch_at": datetime.utcnow().isoformat(),
                    "like_count": metrics_clean.get("like_count") if metrics_clean else None,
                    "comment_count": metrics_clean.get("comment_count") if metrics_clean else None,
                }
            )

        if project_id:
            _update_project_metrics(session, project_id)

        session.commit()
        logger.info("Posts mis à jour en base.")

        push_meilisearch(meili_records)
        push_supabase(supabase_records)

    finally:
        session.close()


def _update_project_metrics(session: Session, project_id: str) -> None:
    try:
        project_uuid = UUID(str(project_id))
    except ValueError:
        logger.warning("Project ID invalide: %s", project_id)
        return

    project = session.query(Project).filter(Project.id == project_uuid).first()
    if not project:
        logger.warning("Projet introuvable pour mise à jour: %s", project_id)
        return

    creators = (
        session.query(ProjectCreator)
        .filter(ProjectCreator.project_id == project.id)
        .all()
    )
    hashtag_links = (
        session.query(ProjectHashtag)
        .filter(ProjectHashtag.project_id == project.id)
        .all()
    )

    author_usernames = [link.creator_username for link in creators if link.creator_username]
    hashtag_ids = [link.hashtag_id for link in hashtag_links]

    post_ids: Set[str] = set()
    if author_usernames:
        for (post_id,) in session.query(Post.id).filter(Post.author.in_(author_usernames)):
            post_ids.add(post_id)
    if hashtag_ids:
        for (post_id,) in (
            session.query(PostHashtag.post_id)
            .filter(PostHashtag.hashtag_id.in_(hashtag_ids))
        ):
            post_ids.add(post_id)

    project.creators_count = len(creators)
    project.posts_count = len(post_ids)
    project.last_run_at = datetime.utcnow()

    scope_parts: List[str] = []
    platform_names: Set[str] = set()
    for creator in creators:
        if creator.creator_username:
            scope_parts.append(f"@{creator.creator_username}")
        if creator.platform and creator.platform.name:
            platform_names.add(creator.platform.name)
    for link in hashtag_links:
        if link.hashtag and link.hashtag.name:
            scope_parts.append(f"#{link.hashtag.name}")
        if link.hashtag and link.hashtag.platform and link.hashtag.platform.name:
            platform_names.add(link.hashtag.platform.name)

    if len(hashtag_links) and project.creators_count:
        project.scope_type = "both"
    elif len(hashtag_links):
        project.scope_type = "hashtags"
    elif project.creators_count:
        project.scope_type = "creators"
    else:
        project.scope_type = None

    project.scope_query = ", ".join(scope_parts) if scope_parts else None
    project.platforms = json.dumps(sorted(platform_names)) if platform_names else json.dumps([])
    session.add(project)
    logger.info("Projet %s mis à jour: %s posts suivis.", project_id, project.posts_count)


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh Instagram posts via oEmbed.")
    parser.add_argument("--project", help="UUID du projet (sinon tous les posts)", default=None)
    parser.add_argument("--limit", type=int, default=20, help="Nombre max de posts à rafraîchir")
    args = parser.parse_args()

    refresh_posts(project_id=args.project, limit=args.limit)


if __name__ == "__main__":
    main()

