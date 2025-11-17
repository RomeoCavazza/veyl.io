import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from auth_unified.auth_endpoints import get_optional_user
from core.config import settings
from db.base import get_db
from db.models import Post, Platform, User, Hashtag, PostHashtag
from services.meta_client import call_meta
from services.post_utils import parse_timestamp, ensure_platform, upsert_post, normalize_hashtag, load_post_payload

router = APIRouter(prefix="/api/v1/meta", tags=["meta"])
logger = logging.getLogger(__name__)


@router.get("/oembed")
async def get_oembed(
    url: str = Query(..., description="URL publique IG/FB à embarquer"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Récupère les données oEmbed pour un post Instagram.
    Prouve l'intégration Meta oEmbed API pour App Review.
    """
    try:
        oembed_data = await call_meta(
            method="GET",
            endpoint="v21.0/instagram_oembed",
            params={"url": url},
        )
        return oembed_data
    except Exception as e:
        logger.error(f"Error fetching oEmbed for {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching oEmbed: {e}")


@router.get("/ig-public")
async def get_instagram_public_content(
    tag: str = Query(..., min_length=1, description="Hashtag to search (without #)"),
    user_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Récupère du contenu public Instagram via hashtag.
    Prouve l'intégration Instagram Public Content Access pour App Review.
    
    STRATÉGIE: 1. Essayer Meta API d'abord → 2. Fallback DB si échec
    """
    # 1️⃣ ESSAYER META API D'ABORD (même si IG_USER_ID manquant, on essaie)
    # Le token peut contenir l'info nécessaire
    try:
        ig_user_id = user_id or settings.IG_USER_ID
        if not ig_user_id:
            logger.warning("IG_USER_ID not found, but trying API anyway (token may contain info)")
            # Essayer quand même avec "me" ou le user_id du token
            ig_user_id = "me"
        
        logger.info(f"Trying Meta API for hashtag: #{tag} (user_id: {ig_user_id})")
        search = await call_meta(
            method="GET",
            endpoint="v21.0/ig_hashtag_search",
            params={"user_id": ig_user_id, "q": tag},
        )
        data = search.get("data", [])
        if not data:
            logger.warning(f"Hashtag #{tag} not found in Meta API, falling back to DB")
            raise Exception(f"Hashtag {tag} not found in Meta API")  # Raise generic exception to trigger fallback

        hashtag_id = data[0]["id"]
        media = await call_meta(
            method="GET",
            endpoint=f"v21.0/{hashtag_id}/recent_media",
            params={
                "user_id": ig_user_id,
                "fields": "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count",
                "limit": limit,
            },
        )

        posts = media.get("data", [])
        logger.info(f"API returned {len(posts)} posts from Meta API")
        
        # Si l'API retourne 0 posts, faire le fallback DB
        if not posts:
            logger.warning(f"Meta API returned 0 posts for #{tag}, falling back to DB")
            raise Exception(f"No posts returned from Meta API for #{tag}")  # Trigger fallback
        
        # Stocker les posts dans la DB
        results = []
        for item in posts:
            defaults = {
                "author": None,
                "caption": item.get("caption", ""),
                "media_url": item.get("media_url"),
                "posted_at": parse_timestamp(item.get("timestamp")),
                "metrics": json.dumps({
                    "likes": item.get("like_count", 0),
                    "comments": item.get("comments_count", 0),
                }),
            }
            post = upsert_post(
                db, "instagram", item["id"], item, "meta_ig_public_api", defaults
            )
            results.append({
                "id": post.id,
                "caption": post.caption,
                "media_url": post.media_url,
                "permalink": item.get("permalink"),
                "like_count": item.get("like_count", 0),
                "comments_count": item.get("comments_count", 0),
                "timestamp": item.get("timestamp"),
            })
        
        db.commit()
        return {"data": results, "source": "meta_api"}
    except HTTPException as http_exc:
        # Si c'est une erreur 404 (hashtag non trouvé), faire le fallback DB
        if http_exc.status_code == 404:
            logger.warning(f"Meta API returned 404 for #{tag}, falling back to DB")
        else:
            # Pour les autres erreurs HTTP (401, 403, 500, etc.), relancer l'exception
            raise
    except Exception as e:
        logger.exception(f"API failed for #{tag}, falling back to DB: {e}")
    
    # 2️⃣ FALLBACK: CHARGER DEPUIS DB
    logger.info("Loading from database (fallback)...")
    platform = db.query(Platform).filter(Platform.name == "instagram").first()
    if not platform:
        raise HTTPException(status_code=404, detail="Instagram platform not found in database")
    
    # Rechercher les posts contenant le hashtag
    normalized_tag = normalize_hashtag(tag)
    posts = (
        db.query(Post)
        .filter(
            Post.platform_id == platform.id,
            or_(
                Post.caption.ilike(f"%#{normalized_tag}%"),
                Post.caption.ilike(f"%{normalized_tag}%"),
            ),
        )
        .order_by(Post.posted_at.desc().nullslast())
        .limit(limit)
        .all()
    )
    
    if not posts:
        # Si ni l'API ni la DB n'ont retourné de résultats, renvoyer une liste vide au lieu d'une erreur 500
        # C'est normal qu'il n'y ait pas toujours de résultats, ce n'est pas une erreur serveur
        logger.info(f"No posts found for hashtag #{tag} in database (fallback)")
        return {"data": [], "source": "database_fallback"}
    
    results = []
    for post in posts:
        payload_data = load_post_payload(post)
        metrics = payload_data["metrics"]
        results.append({
            "id": post.id,
            "caption": post.caption,
            "media_url": post.media_url,
            "like_count": metrics.get("likes", 0),
            "comments_count": metrics.get("comments", 0),
            "timestamp": post.posted_at.isoformat() if post.posted_at else None,
        })
    
    return {"data": results, "source": "database_fallback"}


@router.get("/ig-hashtag")
async def get_instagram_hashtag_media(
    tag: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Alias pour /ig-public (compatibilité)"""
    return await get_instagram_public_content(tag=tag, limit=limit, db=db, current_user=current_user)


@router.get("/page-public")
async def get_page_public_posts(
    page_id: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Récupère les posts publics d'une page Facebook.
    Prouve l'intégration Facebook Public Content Access pour App Review.
    """
    try:
        posts = await call_meta(
            method="GET",
            endpoint=f"v21.0/{page_id}/posts",
            params={
                "fields": "id,message,created_time,permalink_url,reactions.summary(true),comments.summary(true)",
                "limit": limit,
            },
        )
        return posts
    except Exception as e:
        logger.error(f"Error fetching page posts for {page_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching page posts: {e}")


@router.get("/insights")
async def get_insights(
    resource_id: str = Query(..., description="IG Business ID ou Page ID"),
    metrics: str = Query(..., description="Liste metrics Graph API"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Récupère les insights (métriques) pour un compte Instagram Business ou une page Facebook.
    Prouve l'intégration Insights API pour App Review.
    """
    try:
        insights = await call_meta(
            method="GET",
            endpoint=f"v21.0/{resource_id}/insights",
            params={"metric": metrics},
        )
        return insights
    except Exception as e:
        logger.error(f"Error fetching insights for {resource_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching insights: {e}")


@router.post("/link-posts-to-hashtag")
def link_posts_to_hashtag(
    hashtag_name: str = Query(..., description="Nom du hashtag (sans #)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Lie automatiquement les posts contenant un hashtag à ce hashtag dans la DB.
    Utilisé pour créer les liens PostHashtag manquants.
    """
    from services.post_utils import search_posts_by_hashtag
    
    normalized_name = normalize_hashtag(hashtag_name)
    if not normalized_name:
        raise HTTPException(status_code=400, detail="Hashtag name required")
    
    # Chercher ou créer le hashtag
    hashtag = db.query(Hashtag).filter(Hashtag.name == normalized_name).first()
    if not hashtag:
        platform = ensure_platform(db, "instagram")
        hashtag = Hashtag(name=normalized_name, platform_id=platform.id)
        db.add(hashtag)
        db.flush()
    
    # Rechercher les posts contenant ce hashtag
    posts = search_posts_by_hashtag(db, normalized_name, limit=100)
    
    linked_count = 0
    for post in posts:
        # Vérifier si le lien existe déjà
        existing_link = (
            db.query(PostHashtag)
            .filter(
                PostHashtag.post_id == post.id,
                PostHashtag.hashtag_id == hashtag.id
            )
            .first()
        )
        if not existing_link:
            post_hashtag_link = PostHashtag(
                post_id=post.id,
                hashtag_id=hashtag.id
            )
            db.add(post_hashtag_link)
            linked_count += 1
    
    db.commit()
    logger.info(f"Linked {linked_count} posts to hashtag #{normalized_name}")
    
    return {
        "hashtag": normalized_name,
        "hashtag_id": hashtag.id,
        "linked_posts": linked_count,
        "total_posts_found": len(posts)
    }

