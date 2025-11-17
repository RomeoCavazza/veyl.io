# services/post_utils.py
# Utilitaires partagés pour la gestion des posts

import json
import logging
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from db.models import Post, Platform

logger = logging.getLogger(__name__)


def parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    """Parse timestamp ISO 8601 (utilisé par Meta et TikTok)"""
    if not value:
        return None
    ts = value.replace("Z", "+00:00")
    if ts.endswith("+0000"):
        ts = ts[:-5] + "+00:00"
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def ensure_platform(db: Session, name: str) -> Platform:
    """S'assurer qu'une plateforme existe dans la DB, la créer si nécessaire"""
    platform = db.query(Platform).filter(Platform.name == name).first()
    if not platform:
        platform = Platform(name=name)
        db.add(platform)
        db.flush()
    return platform


def upsert_post(
    db: Session,
    platform_name: str,
    external_id: str,
    payload: dict,
    source: str,
    defaults: dict,
) -> Post:
    """Upsert un post dans la DB (pattern commun Meta/TikTok)"""
    platform = ensure_platform(db, platform_name)
    post = (
        db.query(Post)
        .filter(or_(Post.id == external_id, Post.external_id == external_id))
        .first()
    )

    if not post:
        post = Post(
            id=external_id,
            external_id=external_id,
            platform_id=platform.id,
            source=source,
        )
        db.add(post)

    post.platform_id = platform.id
    post.external_id = external_id
    post.source = source
    for key, value in defaults.items():
        if value is not None:
            setattr(post, key, value)

    post.api_payload = json.dumps(payload)
    post.last_fetch_at = datetime.utcnow()
    return post


def search_posts_by_hashtag(
    db: Session,
    hashtag_name: str,
    limit: int = 100,
    platform_ids: Optional[List[int]] = None,
) -> list[Post]:
    """
    Recherche les posts contenant un hashtag (dans caption OU colonne hashtags).
    Utilisé par _attach_hashtag, link_posts_to_project_hashtag et _collect_project_posts.
    
    Args:
        db: Session SQLAlchemy
        hashtag_name: Nom du hashtag (avec ou sans #)
        limit: Nombre maximum de posts à retourner
        platform_ids: Liste optionnelle d'IDs de plateformes pour filtrer les résultats
    """
    normalized_name = normalize_hashtag(hashtag_name)
    if not normalized_name:
        return []
    
    logger.debug(f"Searching posts with #{normalized_name} (caption + hashtags array)...")
    
    # Patterns de recherche flexibles
    search_patterns = [
        f'%#{normalized_name}%',
        f'%#{normalized_name.lower()}%',
        f'%#{normalized_name.upper()}%',
        f'%{normalized_name}%',
    ]
    
    # Recherche dans caption
    caption_filter = or_(*[Post.caption.ilike(pattern) for pattern in search_patterns])
    
    # Recherche dans colonne hashtags (ArrayType)
    hashtag_variants = [
        normalized_name, normalized_name.lower(), normalized_name.upper(),
        f'#{normalized_name}', f'#{normalized_name.lower()}', f'#{normalized_name.upper()}',
    ]
    
    hashtags_filters = []
    for variant in hashtag_variants:
        hashtags_filters.append(
            and_(
                Post.hashtags.isnot(None),
                func.array_to_string(Post.hashtags, ',').ilike(f'%{variant}%')
            )
        )
    
    # Combiner les deux recherches
    if hashtags_filters:
        hashtags_filter = or_(*hashtags_filters)
        combined_filter = or_(caption_filter, hashtags_filter)
    else:
        combined_filter = caption_filter
    
    query = (
        db.query(Post)
        .filter(combined_filter)
    )
    
    # Filtrer par plateforme si spécifié
    if platform_ids:
        query = query.filter(Post.platform_id.in_(platform_ids))
    
    posts = (
        query
        .order_by(Post.posted_at.desc().nullslast(), Post.fetched_at.desc().nullslast())
        .limit(limit)
        .all()
    )
    
    logger.info(f"Found {len(posts)} posts matching #{normalized_name}")
    return posts


def normalize_hashtag(value: str) -> str:
    """Normalise un hashtag (retire #, trim, lowercase)"""
    return value.strip().lstrip("#").lower()


def normalize_creator(value: str) -> str:
    """Normalise un nom de créateur (retire @, trim, lowercase)"""
    return value.strip().lstrip("@").lower()


def load_post_payload(post: Post) -> Dict[str, dict]:
    """
    Charge et parse api_payload et metrics depuis un Post.
    Retourne un dict avec 'api_payload' et 'metrics'.
    """
    api_payload = {}
    metrics = {}
    try:
        if post.api_payload:
            api_payload = json.loads(post.api_payload)
        if post.metrics:
            metrics = json.loads(post.metrics)
    except (TypeError, ValueError):
        pass
    return {"api_payload": api_payload, "metrics": metrics}

