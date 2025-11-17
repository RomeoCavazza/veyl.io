import json
import logging
from datetime import datetime
from typing import Optional, Callable, Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from auth_unified.auth_endpoints import get_optional_user
from db.base import get_db
from db.models import Post, Platform, User, OAuthAccount
from services.tiktok_client import call_tiktok
from services.post_utils import parse_timestamp, ensure_platform, upsert_post, load_post_payload

router = APIRouter(prefix="/api/v1/tiktok", tags=["tiktok"])
logger = logging.getLogger(__name__)


def _get_post_share_url(post: Post, api_payload: dict) -> Optional[str]:
    """Construit l'URL de partage TikTok depuis api_payload ou external_id"""
    if api_payload:
        share_url = api_payload.get("share_url") or api_payload.get("permalink") or api_payload.get("url")
        if share_url:
            return share_url
    
    if post.external_id:
        if post.external_id.startswith('http'):
            return post.external_id
        else:
            return f"https://www.tiktok.com/@{(post.author or 'user')}/video/{post.external_id}"
    
    return None


def _get_tiktok_token(db: Session, current_user: Optional[User]) -> str:
    """Récupère le token TikTok depuis OAuthAccount pour l'utilisateur courant"""
    if current_user:
        oauth_account = (
            db.query(OAuthAccount)
            .filter(
                OAuthAccount.user_id == current_user.id,
                OAuthAccount.provider == "tiktok",
            )
            .first()
        )
        if oauth_account and oauth_account.access_token:
            return oauth_account.access_token
    
    # Fallback: chercher n'importe quel token TikTok (pour tests/public access)
    oauth_account = (
        db.query(OAuthAccount)
        .filter(
            OAuthAccount.provider == "tiktok",
            OAuthAccount.access_token.isnot(None),
        )
        .first()
    )
    if oauth_account and oauth_account.access_token:
        logger.warning("Using fallback TikTok token (no user-specific token found)")
        return oauth_account.access_token
    
    raise HTTPException(
        status_code=401,
        detail="TikTok access token not found. Please connect your TikTok account via OAuth.",
    )


def _handle_api_error(e: Exception, context: str = ""):
    """Gère les erreurs API et log le fallback DB"""
    if isinstance(e, HTTPException):
        if e.status_code in (401, 403):
            logger.warning(f"API auth failed ({e.status_code}), falling back to DB {context}")
        elif e.status_code == 404:
            logger.info(f"API returned 0 results, falling back to DB {context}")
        else:
            logger.warning(f"API error ({e.status_code}), falling back to DB: {e.detail} {context}")
    else:
        logger.exception(f"API error, falling back to DB {context}: {e}")


def _build_api_response(data: Any, source: str, **meta) -> Dict:
    """Construit une réponse API standardisée"""
    response = {
        "status": "success",
        "http_status": 200,
        "data": data,
        "meta": {
            "fetched_at": datetime.utcnow().isoformat(),
            "source": source,
            **meta
        },
    }
    return response




@router.get("/profile")
async def get_tiktok_profile(
    user_id: Optional[str] = Query(None, description="TikTok user ID (open_id or union_id)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Récupère le profil TikTok d'un utilisateur.
    Utilise les scopes: user.info.basic, user.info.profile
    
    STRATÉGIE: 1. Essayer API TikTok d'abord → 2. Fallback DB si échec
    """
    tiktok_platform = ensure_platform(db, "tiktok")
    
    # 1️⃣ ESSAYER L'API TIKTOK D'ABORD
    try:
        access_token = _get_tiktok_token(db, current_user)
        if not user_id:
            user_id = "me"
        
        fields = "open_id,union_id,avatar_url,display_name,profile_web_link,profile_deep_link,bio_description,is_verified"
        logger.info("Trying TikTok API first (user/info)...")
        response = await call_tiktok(
            method="GET",
            endpoint="user/info/",
            params={"fields": fields},
            access_token=access_token,
        )
        
        user_data = response.get("data", {}).get("user", {})
        if user_data:
            # Stocker le profil dans Post pour traçabilité
            if user_data.get("open_id") or user_data.get("union_id"):
                external_id = user_data.get("open_id") or user_data.get("union_id")
                defaults = {
                    "author": user_data.get("display_name"),
                    "caption": f"TikTok profile: {user_data.get('bio_description', '')}",
                    "media_url": user_data.get("avatar_url"),
                    "fetched_at": datetime.utcnow(),
                }
                upsert_post(
                    db=db,
                    platform_name="tiktok",
                    external_id=f"profile:{external_id}",
                    payload=user_data,
                    source="tiktok_profile_api",
                    defaults=defaults,
                )
                db.commit()
            
            return _build_api_response(user_data, "tiktok_profile_api")
        else:
            logger.warning("API returned empty profile, falling back to DB")
            raise HTTPException(status_code=404, detail="Profile not found")
            
    except Exception as e:
        _handle_api_error(e, "(profile)")
    
    # 2️⃣ FALLBACK: CHARGER DEPUIS DB
    logger.info("Loading profile from database (fallback)...")
    external_id_pattern = f"profile:%{user_id}%" if user_id and user_id != "me" else "profile:%"
    posts = (
        db.query(Post)
        .filter(
            Post.platform_id == tiktok_platform.id,
            Post.external_id.like(external_id_pattern),
            Post.source == "tiktok_profile_api"
        )
        .order_by(Post.fetched_at.desc().nullslast())
        .limit(1)
        .all()
    )
    
    if not posts:
        raise HTTPException(status_code=404, detail="TikTok profile not found in database")
    
    post = posts[0]
    payload_data = _load_post_payload(post)
    api_payload = payload_data["api_payload"]
    
    user_data = {
        "open_id": api_payload.get("open_id"),
        "union_id": api_payload.get("union_id"),
        "display_name": post.author or api_payload.get("display_name"),
        "avatar_url": post.media_url or api_payload.get("avatar_url"),
        "bio_description": api_payload.get("bio_description"),
        "is_verified": api_payload.get("is_verified", False),
    }
    
    return _build_api_response(user_data, "database_fallback")


@router.get("/stats")
async def get_tiktok_stats(
    user_id: Optional[str] = Query(None, description="TikTok user ID (open_id or union_id)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Récupère les statistiques TikTok d'un utilisateur.
    Utilise le scope: user.info.stats
    
    STRATÉGIE: 1. Essayer API TikTok d'abord → 2. Fallback DB si échec
    """
    tiktok_platform = ensure_platform(db, "tiktok")
    
    # 1️⃣ ESSAYER L'API TIKTOK D'ABORD
    try:
        access_token = _get_tiktok_token(db, current_user)
        if not user_id:
            user_id = "me"
        
        fields = "open_id,follower_count,following_count,likes_count,video_count"
        logger.info("Trying TikTok API first (user/info for stats)...")
        response = await call_tiktok(
            method="GET",
            endpoint="user/info/",
            params={"fields": fields},
            access_token=access_token,
        )
        
        user_data = response.get("data", {}).get("user", {})
        if user_data:
            # Stocker les stats dans Post pour analytics
            if user_data.get("open_id") or user_data.get("union_id"):
                external_id = user_data.get("open_id") or user_data.get("union_id")
                metrics = {
                    "follower_count": user_data.get("follower_count"),
                    "following_count": user_data.get("following_count"),
                    "likes_count": user_data.get("likes_count"),
                    "video_count": user_data.get("video_count"),
                }
                defaults = {
                    "author": user_data.get("display_name") or f"TikTok User {external_id[:8]}",
                    "caption": f"TikTok stats for {external_id}",
                    "metrics": json.dumps(metrics),
                    "fetched_at": datetime.utcnow(),
                }
                upsert_post(
                    db=db,
                    platform_name="tiktok",
                    external_id=f"stats:{external_id}",
                    payload=user_data,
                    source="tiktok_stats_api",
                    defaults=defaults,
                )
                db.commit()
            
            return _build_api_response(user_data, "tiktok_stats_api")
        else:
            logger.warning("API returned empty stats, falling back to DB")
            raise HTTPException(status_code=404, detail="Stats not found")
            
    except Exception as e:
        _handle_api_error(e, "(stats)")
    
    # 2️⃣ FALLBACK: CHARGER DEPUIS DB
    logger.info("Loading stats from database (fallback)...")
    external_id_pattern = f"stats:%{user_id}%" if user_id and user_id != "me" else "stats:%"
    posts = (
        db.query(Post)
        .filter(
            Post.platform_id == tiktok_platform.id,
            Post.external_id.like(external_id_pattern),
            Post.source == "tiktok_stats_api"
        )
        .order_by(Post.fetched_at.desc().nullslast())
        .limit(1)
        .all()
    )
    
    if not posts:
        raise HTTPException(status_code=404, detail="TikTok stats not found in database")
    
    post = posts[0]
    payload_data = load_post_payload(post)
    api_payload = payload_data["api_payload"]
    metrics = payload_data["metrics"]
    
    user_data = {
        "open_id": api_payload.get("open_id"),
        "union_id": api_payload.get("union_id"),
        "follower_count": metrics.get("follower_count") or api_payload.get("follower_count"),
        "following_count": metrics.get("following_count") or api_payload.get("following_count"),
        "likes_count": metrics.get("likes_count") or api_payload.get("likes_count"),
        "video_count": metrics.get("video_count") or api_payload.get("video_count"),
    }
    
    return _build_api_response(user_data, "database_fallback")


@router.get("/videos")
async def get_tiktok_videos(
    query: Optional[str] = Query(None, description="Search query (hashtag or keyword)"),
    limit: int = Query(10, ge=1, le=50, description="Number of videos to fetch"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Récupère les vidéos TikTok publiques d'un utilisateur ou par recherche.
    Utilise le scope: video.list
    
    STRATÉGIE: 1. Essayer API TikTok d'abord → 2. Fallback DB si échec
    """
    tiktok_platform = ensure_platform(db, "tiktok")
    
    # 1️⃣ ESSAYER L'API TIKTOK D'ABORD
    try:
        access_token = _get_tiktok_token(db, current_user)
        logger.info("Trying TikTok API first (video/list)...")
        params: dict = {"max_count": limit}
        if cursor:
            params["cursor"] = cursor
        
        response = await call_tiktok(
            method="GET",
            endpoint="video/list/",
            params=params,
            access_token=access_token,
        )
        
        videos = response.get("data", {}).get("videos", [])
        
        # Si query fourni, filtrer les vidéos par query dans leur caption
        if query:
            query_lower = query.lower().replace('#', '')
            videos = [
                v for v in videos
                if query_lower in (v.get("title") or "").lower() 
                or query_lower in (v.get("video_description") or "").lower()
            ]
            logger.info(f"Filtered {len(videos)} videos matching query: {query}")
        
        if videos:
            # Stocker chaque vidéo dans Post
            for video in videos:
                video_id = video.get("id")
                if not video_id:
                    continue
                
                metrics = {
                    "like_count": video.get("like_count"),
                    "comment_count": video.get("comment_count"),
                    "share_count": video.get("share_count"),
                    "view_count": video.get("view_count"),
                }
                
                defaults = {
                    "author": video.get("creator_username") or video.get("creator_display_name"),
                    "caption": video.get("title") or video.get("video_description"),
                    "media_url": video.get("cover_image_url") or video.get("thumbnail_url"),
                    "permalink": video.get("share_url") or f"https://www.tiktok.com/@{(video.get('creator_username') or 'user')}/video/{video_id}",
                    "posted_at": parse_timestamp(video.get("create_time")),
                    "metrics": json.dumps(metrics),
                    "fetched_at": datetime.utcnow(),
                }
                
                upsert_post(
                    db=db,
                    platform_name="tiktok",
                    external_id=str(video_id),
                    payload=video,
                    source="tiktok_video_list_api",
                    defaults=defaults,
                )
            
            db.commit()
            
            return _build_api_response(
                videos,
                "tiktok_video_list_api",
                count=len(videos),
                cursor=response.get("data", {}).get("cursor"),
                has_more=response.get("data", {}).get("has_more", False),
            )
        else:
            if query:
                logger.info(f"API returned 0 videos matching query '{query}', falling back to DB")
            else:
                logger.info("API returned 0 videos, falling back to DB")
            raise HTTPException(status_code=404, detail="No videos found")
        
    except Exception as e:
        _handle_api_error(e, "(videos)")
    
    # 2️⃣ FALLBACK: CHARGER DEPUIS DB
    logger.info("Loading from database (fallback)...")
    if query:
        posts = (
            db.query(Post)
            .filter(
                Post.platform_id == tiktok_platform.id,
                or_(
                    Post.caption.ilike(f'%{query}%'),
                    Post.caption.ilike(f'%#{query}%'),
                )
            )
            .order_by(Post.posted_at.desc().nullslast(), Post.fetched_at.desc().nullslast())
            .limit(limit)
            .all()
        )
    else:
        posts = (
            db.query(Post)
            .filter(Post.platform_id == tiktok_platform.id)
            .order_by(Post.fetched_at.desc().nullslast())
            .limit(limit)
            .all()
        )
    
    # Convertir Post en format API
    videos = []
    for post in posts:
        payload_data = load_post_payload(post)
        api_payload = payload_data["api_payload"]
        metrics = payload_data["metrics"]
        
        cover_image = (
            post.media_url 
            or api_payload.get("cover_image_url") 
            or api_payload.get("thumbnail_url")
        )
        
        videos.append({
            "id": post.id,
            "creator_username": post.author,
            "title": post.caption,
            "video_description": post.caption,
            "cover_image_url": cover_image,
            "thumbnail_url": cover_image,
            "share_url": _get_post_share_url(post, api_payload),
            "create_time": post.posted_at.isoformat() if post.posted_at else None,
            "like_count": metrics.get("like_count", 0),
            "comment_count": metrics.get("comment_count", 0),
            "share_count": metrics.get("share_count", 0),
            "view_count": metrics.get("view_count", 0),
        })
    
    return _build_api_response(
        videos,
        "database_fallback",
        count=len(videos),
        cursor=None,
        has_more=False,
    )
