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
from typing import Iterable, List, Optional

import requests
from sqlalchemy.orm import Session

from core.config import settings
from db.base import SessionLocal
from db.models import Post, ProjectCreator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


GRAPH_BASE_URL = "https://graph.facebook.com/v21.0/instagram_oembed"

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
    query = session.query(Post)
    if project_id:
        creator_usernames = [
            row.creator_username
            for row in session.query(ProjectCreator)
            .filter(ProjectCreator.project_id == project_id)
            .all()
        ]
        if not creator_usernames:
            logger.warning("Aucun créateur lié au projet %s.", project_id)
            return []
        query = query.filter(Post.author.in_(creator_usernames))

    return (
        query.order_by(Post.fetched_at.desc().nullslast(), Post.posted_at.desc().nullslast())
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

            thumbnail = payload.get("thumbnail_url")
            author_name = payload.get("author_name") or post.author
            caption = payload.get("title") or post.caption

            if thumbnail:
                post.media_url = thumbnail
            post.caption = caption
            post.author = author_name
            post.api_payload = json.dumps(payload)
            post.fetched_at = datetime.utcnow()

            # Mettre à jour quelques métriques si disponibles
            metrics = {
                "like_count": payload.get("like_count"),
                "comment_count": payload.get("comment_count"),
            }
            post.metrics = json.dumps({k: v for k, v in metrics.items() if v is not None})

            meili_records.append(
                {
                    "id": post.id,
                    "author": post.author,
                    "caption": post.caption,
                    "platform": "instagram",
                    "media_url": post.media_url,
                    "permalink": permalink,
                    "posted_at": post.posted_at.isoformat() if post.posted_at else None,
                }
            )
            supabase_records.append(
                {
                    "id": post.id,
                    "provider": "instagram",
                    "url": permalink,
                    "creator": post.author,
                    "title": post.caption,
                    "thumbnail": post.media_url,
                    "last_fetch_at": datetime.utcnow().isoformat(),
                }
            )

        session.commit()
        logger.info("Posts mis à jour en base.")

        push_meilisearch(meili_records)
        push_supabase(supabase_records)

    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh Instagram posts via oEmbed.")
    parser.add_argument("--project", help="UUID du projet (sinon tous les posts)", default=None)
    parser.add_argument("--limit", type=int, default=20, help="Nombre max de posts à rafraîchir")
    args = parser.parse_args()

    refresh_posts(project_id=args.project, limit=args.limit)


if __name__ == "__main__":
    main()

