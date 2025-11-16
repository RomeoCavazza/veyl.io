import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from auth_unified.auth_endpoints import get_optional_user
from db.base import get_db
from db.models import Post, Platform, User, OAuthAccount, Hashtag, PostHashtag
from services.tiktok_client import call_tiktok

router = APIRouter(prefix="/api/v1/tiktok", tags=["tiktok"])
logger = logging.getLogger(__name__)


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    """Parse TikTok timestamp format (ISO 8601)"""
    if not value:
        return None
    ts = value.replace("Z", "+00:00")
    if ts.endswith("+0000"):
        ts = ts[:-5] + "+00:00"
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def _ensure_platform(db: Session, name: str) -> Platform:
    """Ensure platform exists in database"""
    platform = db.query(Platform).filter(Platform.name == name).first()
    if not platform:
        platform = Platform(name=name)
        db.add(platform)
        db.flush()
    return platform


def _upsert_post(
    db: Session,
    platform_name: str,
    external_id: str,
    payload: dict,
    source: str,
    defaults: dict,
) -> Post:
    """Upsert a post in the database (same pattern as meta_routes.py)"""
    platform = _ensure_platform(db, platform_name)
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


def _get_tiktok_token(db: Session, current_user: Optional[User]) -> str:
    """
    Récupère le token TikTok depuis OAuthAccount pour l'utilisateur courant.
    Si current_user est None, essaie de trouver un token global (fallback).
    """
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


@router.get("/profile")
async def get_tiktok_profile(
    user_id: Optional[str] = Query(None, description="TikTok user ID (open_id or union_id)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Récupère le profil TikTok d'un utilisateur.
    Utilise les scopes: user.info.basic, user.info.profile
    """
    access_token = _get_tiktok_token(db, current_user)
    
    # Si user_id n'est pas fourni, récupérer le profil de l'utilisateur connecté
    if not user_id:
        # TikTok API nécessite un user_id, on doit le récupérer depuis le token
        # Pour l'instant, on utilise "me" si disponible, sinon on doit passer user_id
        user_id = "me"
    
    fields = "open_id,union_id,avatar_url,display_name,profile_web_link,profile_deep_link,bio_description,is_verified"
    
    try:
        response = await call_tiktok(
            method="GET",
            endpoint="user/info/",
            params={"fields": fields},
            access_token=access_token,
        )
        
        user_data = response.get("data", {}).get("user", {})
        
        # Stocker le profil dans Post pour traçabilité (optionnel)
        if user_data.get("open_id") or user_data.get("union_id"):
            external_id = user_data.get("open_id") or user_data.get("union_id")
            defaults = {
                "author": user_data.get("display_name"),
                "caption": f"TikTok profile: {user_data.get('bio_description', '')}",
                "media_url": user_data.get("avatar_url"),
                "fetched_at": datetime.utcnow(),
            }
            _upsert_post(
                db=db,
                platform_name="tiktok",
                external_id=f"profile:{external_id}",
                payload=user_data,
                source="tiktok_profile",
                defaults=defaults,
            )
            db.commit()
        
        return {
            "status": "success",
            "http_status": 200,
            "data": user_data,
            "meta": {
                "fetched_at": datetime.utcnow().isoformat(),
                "source": "tiktok_api",
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error fetching TikTok profile")
        raise HTTPException(status_code=500, detail=f"Failed to fetch TikTok profile: {str(e)}")


@router.get("/stats")
async def get_tiktok_stats(
    user_id: Optional[str] = Query(None, description="TikTok user ID (open_id or union_id)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Récupère les statistiques TikTok d'un utilisateur.
    Utilise le scope: user.info.stats
    """
    access_token = _get_tiktok_token(db, current_user)
    
    if not user_id:
        user_id = "me"
    
    fields = "open_id,follower_count,following_count,likes_count,video_count"
    
    try:
        response = await call_tiktok(
            method="GET",
            endpoint="user/info/",
            params={"fields": fields},
            access_token=access_token,
        )
        
        user_data = response.get("data", {}).get("user", {})
        
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
            _upsert_post(
                db=db,
                platform_name="tiktok",
                external_id=f"stats:{external_id}",
                payload=user_data,
                source="tiktok_stats",
                defaults=defaults,
            )
            db.commit()
        
        return {
            "status": "success",
            "http_status": 200,
            "data": user_data,
            "meta": {
                "fetched_at": datetime.utcnow().isoformat(),
                "source": "tiktok_api",
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error fetching TikTok stats")
        raise HTTPException(status_code=500, detail=f"Failed to fetch TikTok stats: {str(e)}")


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
    
    Note: TikTok API nécessite un user_id pour lister les vidéos d'un utilisateur.
    Pour la recherche par hashtag/keyword, on utilise l'endpoint approprié.
    """
    access_token = _get_tiktok_token(db, current_user)
    
    try:
        # TikTok API: video/list/ nécessite un user_id
        # Pour l'instant, on récupère les vidéos de l'utilisateur connecté
        # TODO: Ajouter support pour recherche par hashtag si TikTok API le permet
        
        params: dict = {
            "max_count": limit,
        }
        if cursor:
            params["cursor"] = cursor
        
        response = await call_tiktok(
            method="GET",
            endpoint="video/list/",
            params=params,
            access_token=access_token,
        )
        
        videos = response.get("data", {}).get("videos", [])
        
        # Stocker chaque vidéo dans Post
        stored_posts = []
        for video in videos:
            video_id = video.get("id")
            if not video_id:
                continue
            
            # TikTok video data structure
            # https://developers.tiktok.com/doc/tiktok-api-v2-video-list/
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
                "posted_at": _parse_timestamp(video.get("create_time")),
                "metrics": json.dumps(metrics),
                "fetched_at": datetime.utcnow(),
            }
            
            post = _upsert_post(
                db=db,
                platform_name="tiktok",
                external_id=str(video_id),
                payload=video,
                source="tiktok_videos",
                defaults=defaults,
            )
            stored_posts.append(post)
        
        db.commit()
        
        return {
            "status": "success",
            "http_status": 200,
            "data": videos,
            "meta": {
                "count": len(videos),
                "cursor": response.get("data", {}).get("cursor"),
                "has_more": response.get("data", {}).get("has_more", False),
                "fetched_at": datetime.utcnow().isoformat(),
                "source": "tiktok_video_list_api",
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error fetching TikTok videos")
        raise HTTPException(status_code=500, detail=f"Failed to fetch TikTok videos: {str(e)}")


@router.post("/seed-fashion-posts")
def seed_fashion_posts(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    🔗 Insère des posts TikTok de démo et les lie au hashtag "fashion".
    Utile pour préparer la démo App Review.
    """
    import re
    
    # Données des posts TikTok
    TIKTOK_POSTS = [
        {"creator": "styledbysash9", "url": "https://www.tiktok.com/@styledbysash9/video/7499036976218230038?q=fashion&t=1763320557566"},
        {"creator": "wisdm8", "url": "https://www.tiktok.com/@wisdm8/video/7404270216542244126?q=fashion&t=1763320699290"},
        {"creator": "yungalyy", "url": "https://www.tiktok.com/@yungalyy/video/7509573574215208214?q=fashion&t=1763320699290"},
        {"creator": "taymosesofficial", "url": "https://www.tiktok.com/@taymosesofficial/video/7552842920798276886?q=fashion&t=1763320699290"},
        {"creator": "reubsfits", "url": "https://www.tiktok.com/@reubsfits/video/7522860474103385366?q=fashion&t=1763320699290"},
        {"creator": "jameswuantin", "url": "https://www.tiktok.com/@jameswuantin/video/7568916711970180366?q=fashion&t=1763320870708"},
        {"creator": "prince_merlin9", "url": "https://www.tiktok.com/@prince_merlin9/video/7476098222260276498?q=fashion&t=1763320870708"},
        {"creator": "vinicci_", "url": "https://www.tiktok.com/@vinicci_/video/7525932445175155982?q=fashion&t=1763320870708"},
    ]
    
    def extract_video_id(url: str) -> str:
        match = re.search(r'/video/(\d+)', url)
        if match:
            return match.group(1)
        raise ValueError(f"Impossible d'extraire le video_id de l'URL: {url}")
    
    # 1. Assurer que la plateforme TikTok existe
    tiktok_platform = _ensure_platform(db, "tiktok")
    db.flush()
    
    # 2. Assurer que le hashtag "fashion" existe pour TikTok
    fashion_hashtag = (
        db.query(Hashtag)
        .filter(Hashtag.name == "fashion", Hashtag.platform_id == tiktok_platform.id)
        .first()
    )
    if not fashion_hashtag:
        fashion_hashtag = Hashtag(name="fashion", platform_id=tiktok_platform.id, last_scraped=datetime.utcnow())
        db.add(fashion_hashtag)
        db.flush()
        logger.info(f"✅ Créé hashtag: #fashion (platform: tiktok)")
    else:
        logger.info(f"✅ Hashtag existant: #fashion (ID: {fashion_hashtag.id})")
    
    # 3. Traiter chaque post
    created_posts = 0
    linked_posts = 0
    already_linked = 0
    
    for post_data in TIKTOK_POSTS:
        creator = post_data["creator"]
        url = post_data["url"]
        
        try:
            # Extraire le video_id
            video_id = extract_video_id(url)
            permalink = url.split('?')[0]  # URL sans query params
            
            # Créer ou mettre à jour le post
            post = (
                db.query(Post)
                .filter(Post.id == video_id)
                .first()
            )
            
            if not post:
                post = Post(
                    id=video_id,
                    external_id=video_id,
                    platform_id=tiktok_platform.id,
                    author=creator,
                    caption=f"TikTok video by @{creator} #fashion",
                    media_url=f"https://p16-sign-va.tiktokcdn.com/obj/tos-maliva-p-0068/placeholder.jpg",
                    posted_at=datetime.utcnow(),
                    fetched_at=datetime.utcnow(),
                    last_fetch_at=datetime.utcnow(),
                    source="tiktok_demo_seed",
                    metrics=json.dumps({"like_count": 0, "comment_count": 0, "view_count": 0}),
                    api_payload=json.dumps({
                        "id": video_id,
                        "creator": creator,
                        "share_url": permalink,
                        "url": permalink,
                        "permalink": permalink,
                    }),
                )
                db.add(post)
                db.flush()
                created_posts += 1
                logger.info(f"✅ Créé post: {video_id} (@{creator})")
            else:
                # Mettre à jour si nécessaire
                if not post.author:
                    post.author = creator
                # Mettre à jour api_payload avec l'URL si nécessaire
                try:
                    payload = json.loads(post.api_payload or "{}")
                    if not payload.get("share_url") and not payload.get("permalink"):
                        payload["share_url"] = permalink
                        payload["url"] = permalink
                        payload["permalink"] = permalink
                        post.api_payload = json.dumps(payload)
                except (TypeError, ValueError):
                    post.api_payload = json.dumps({"id": video_id, "creator": creator, "share_url": permalink, "url": permalink})
                logger.info(f"ℹ️  Post existant: {video_id} (@{creator})")
            
            # Lier le post au hashtag
            existing_link = (
                db.query(PostHashtag)
                .filter(
                    PostHashtag.post_id == post.id,
                    PostHashtag.hashtag_id == fashion_hashtag.id
                )
                .first()
            )
            
            if not existing_link:
                post_hashtag = PostHashtag(
                    post_id=post.id,
                    hashtag_id=fashion_hashtag.id
                )
                db.add(post_hashtag)
                linked_posts += 1
                logger.info(f"  🔗 Lié post {video_id} à #fashion")
            else:
                already_linked += 1
                logger.info(f"  ℹ️  Post {video_id} déjà lié à #fashion")
            
        except Exception as e:
            logger.error(f"❌ Erreur pour @{creator}: {e}")
            continue
    
    # Commit final
    db.commit()
    
    return {
        "status": "success",
        "message": f"Inserted {created_posts} posts, linked {linked_posts} to #fashion",
        "hashtag_id": fashion_hashtag.id,
        "hashtag_name": "fashion",
        "platform": "tiktok",
        "created_posts": created_posts,
        "linked_posts": linked_posts,
        "already_linked": already_linked,
        "total_processed": len(TIKTOK_POSTS)
    }

