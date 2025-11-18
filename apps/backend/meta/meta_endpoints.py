import json
import logging
import re
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


def _get_meta_token(db: Session, current_user: Optional[User]) -> str:
    """Récupère le token Meta/Instagram depuis OAuthAccount pour l'utilisateur courant, ou token système"""
    from db.models import OAuthAccount
    
    # 1. Essayer le token de l'utilisateur connecté (Instagram ou Facebook)
    if current_user:
        # Essayer Instagram d'abord
        oauth_account = (
            db.query(OAuthAccount)
            .filter(
                OAuthAccount.user_id == current_user.id,
                OAuthAccount.provider == "instagram",
            )
            .first()
        )
        if oauth_account and oauth_account.access_token:
            logger.info(f"Using Instagram OAuth token for user {current_user.id}")
            return oauth_account.access_token
        
        # Essayer Facebook (peut aussi accéder à Instagram)
        oauth_account = (
            db.query(OAuthAccount)
            .filter(
                OAuthAccount.user_id == current_user.id,
                OAuthAccount.provider == "facebook",
            )
            .first()
        )
        if oauth_account and oauth_account.access_token:
            logger.info(f"Using Facebook OAuth token for user {current_user.id}")
            return oauth_account.access_token
    
    # 2. Fallback: token système
    if settings.META_LONG_TOKEN:
        logger.info("Using system META_LONG_TOKEN")
        return settings.META_LONG_TOKEN
    if settings.IG_ACCESS_TOKEN:
        logger.info("Using system IG_ACCESS_TOKEN")
        return settings.IG_ACCESS_TOKEN
    
    raise HTTPException(
        status_code=500,
        detail="Meta access token not found. Please connect your Instagram/Facebook account via OAuth, or configure META_LONG_TOKEN/IG_ACCESS_TOKEN in environment variables."
    )


def _get_all_meta_tokens(db: Session, current_user: Optional[User]) -> list[tuple[str, str]]:
    """Récupère tous les tokens Meta disponibles dans l'ordre de priorité"""
    tokens = []
    
    # 1. Token système META_LONG_TOKEN (priorité 1)
    if settings.META_LONG_TOKEN:
        tokens.append(("system META_LONG_TOKEN", settings.META_LONG_TOKEN))
    
    # 2. Token système IG_ACCESS_TOKEN (priorité 2)
    if settings.IG_ACCESS_TOKEN:
        tokens.append(("system IG_ACCESS_TOKEN", settings.IG_ACCESS_TOKEN))
    
    # 3. Token utilisateur Instagram (priorité 3)
    if current_user:
        try:
            user_token = _get_meta_token(db, current_user)
            if user_token and user_token not in [t[1] for t in tokens]:
                tokens.append(("user OAuth", user_token))
        except:
            pass
    
    return tokens


def _extract_meta_error(meta_error: HTTPException) -> tuple[Optional[int], Optional[str]]:
    """Extrait le code et message d'erreur depuis une MetaAPIError"""
    error_code = None
    error_message = None
    
    if isinstance(meta_error.detail, dict) and "detail" in meta_error.detail:
        meta_error_detail = meta_error.detail.get("detail", {})
        if isinstance(meta_error_detail, dict) and "error" in meta_error_detail:
            error_info = meta_error_detail["error"]
            if isinstance(error_info, dict):
                error_code = error_info.get("code")
                error_message = error_info.get("message")
    
    return error_code, error_message


async def _fetch_oembed_with_tokens(url: str, tokens: list[tuple[str, str]], retry_transient: bool = True) -> dict:
    """
    Essaie de récupérer oEmbed avec une liste de tokens.
    
    Stratégie :
    1. Validation stricte de l'URL (rejette les IDs numériques)
    2. Essayer tous les tokens dans l'ordre de priorité
    3. Retry automatique (3x) pour les erreurs transitoires (code 2)
    4. Si un token fonctionne → retourner 200 OK
    5. Si tous échouent → retourner l'erreur appropriée :
       - Code 10 (permission) → 400 (erreur client)
       - Code 2 (transitoire) → 502 (erreur serveur Meta)
       - Autres → 400 (erreur client)
    """
    import asyncio
    
    cleaned_url = url.split('?')[0].split('#')[0].rstrip('/')
    
    # Validation basique du préfixe
    if not cleaned_url.startswith(('https://www.instagram.com/', 'https://instagram.com/')):
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "INVALID_URL",
                "message": "Invalid Instagram URL. URL must start with https://www.instagram.com/ or https://instagram.com/",
                "url": url
            }
        )
    
    # Validation stricte : extraire et vérifier le code du post
    match = re.search(r'/p/([^/]+)/?$', cleaned_url)
    if not match:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "INVALID_URL_FORMAT",
                "message": "Invalid Instagram post URL format. Expected: https://www.instagram.com/p/{SHORT_CODE}/",
                "url": url
            }
        )
    
    post_code = match.group(1)
    
    # CRITIQUE : Rejeter les IDs numériques (ne fonctionnent pas avec oEmbed)
    # C'est le seul check vraiment nécessaire - Meta API rejette les IDs numériques
    if post_code.isdigit():
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": "NUMERIC_ID_NOT_SUPPORTED",
                "message": f"Instagram numeric IDs are not supported by Meta oEmbed API. Please use the short code URL.",
                "url": url
            }
        )
    
    if not tokens:
        raise HTTPException(status_code=500, detail="No tokens available")
    
    logger.info(f"Fetching oEmbed for {cleaned_url} with {len(tokens)} token(s): {[t[0] for t in tokens]}")
    
    # Collecter toutes les erreurs pour choisir la plus pertinente
    errors_by_code = {}  # {error_code: (error, token_source)}
    all_errors = []  # Liste de toutes les erreurs pour debug
    
    for token_source, access_token in tokens:
        # Retry jusqu'à 3 fois pour les erreurs transitoires (code 2)
        max_retries = 3 if retry_transient else 1
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    # Attendre avant de retry (backoff exponentiel: 0.5s, 1s, 2s)
                    wait_time = 0.5 * (2 ** (attempt - 1))
                    await asyncio.sleep(wait_time)
                    logger.info(f"🔄 Retry attempt {attempt} for {token_source} (waited {wait_time}s)")
                
                logger.debug(f"Trying token {token_source} (attempt {attempt + 1}/{max_retries})")
                oembed_data = await call_meta(
                    method="GET",
                    endpoint="v21.0/instagram_oembed",
                    params={"url": cleaned_url},
                    access_token=access_token,
                )
                logger.info(f"✅ oEmbed retrieved successfully using {token_source}")
                return oembed_data
                
            except HTTPException as meta_error:
                error_code, error_message = _extract_meta_error(meta_error)
                all_errors.append((token_source, error_code, error_message))
                logger.warning(f"❌ Token {token_source} failed (attempt {attempt + 1}/{max_retries}): code={error_code}, message={error_message[:100]}")
                
                # Si erreur transitoire (code 2) et qu'on peut retry, continuer la boucle
                if error_code == 2 and attempt < max_retries - 1:
                    logger.info(f"🔄 Will retry {token_source} due to transient error (code 2)")
                    continue
                
                # Sauvegarder l'erreur par code (garder la première occurrence de chaque code)
                if error_code not in errors_by_code:
                    errors_by_code[error_code] = (meta_error, token_source)
                    logger.info(f"📝 Saved error code {error_code} from {token_source}")
                
                # Si ce n'est pas une erreur transitoire, passer au token suivant
                if error_code != 2:
                    break
    
    # Tous les tokens ont échoué
    if not errors_by_code:
        logger.error(f"🚫 All {len(tokens)} token(s) failed but no error codes collected")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "All tokens failed but no error information available",
                "tokens_tried": len(tokens),
                "url": cleaned_url
            }
        )
    
    # Prioriser les erreurs : code 10 (permission) est plus informatif que code 2 (transitoire)
    # Logique : Si au moins un token retourne code 10, c'est plus explicite pour l'app review
    if 10 in errors_by_code:
        last_error, token_source = errors_by_code[10]
        logger.warning(f"⚠️ All tokens failed. Returning code 10 (permission) from {token_source} (most informative for app review)")
        error_code, error_message = _extract_meta_error(last_error)
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": error_code,
                "error_message": error_message,
                "message": "Meta oEmbed permission not approved yet. Requires Meta App Review approval.",
                "tokens_tried": len(tokens),
                "all_errors": [{"token": t[0], "code": t[1], "message": t[2][:100]} for t in all_errors]
            }
        )
    
    elif 2 in errors_by_code:
        last_error, token_source = errors_by_code[2]
        logger.error(f"⚠️ All tokens failed. Returning code 2 (transient) from {token_source} after {max_retries} retries each")
        error_code, error_message = _extract_meta_error(last_error)
        raise HTTPException(
            status_code=502,
            detail={
                "error_code": error_code,
                "error_message": error_message,
                "message": "Meta API temporarily unavailable. Please try again later.",
                "tokens_tried": len(tokens),
                "retries_per_token": max_retries,
                "all_errors": [{"token": t[0], "code": t[1], "message": t[2][:100]} for t in all_errors]
            }
        )
    
    else:
        # Autres erreurs (codes inconnus)
        error_codes = list(errors_by_code.keys())
        last_error, token_source = errors_by_code[error_codes[0]]
        error_code, error_message = _extract_meta_error(last_error)
        logger.error(f"⚠️ All tokens failed. Unknown error codes: {error_codes}")
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": error_code,
                "error_message": error_message,
                "message": f"Unable to fetch oEmbed: {error_message or 'Unknown error'}",
                "tokens_tried": len(tokens),
                "all_error_codes": error_codes,
                "all_errors": [{"token": t[0], "code": t[1], "message": t[2][:100]} for t in all_errors]
            }
        )


@router.get("/oembed")
async def get_oembed(
    url: str = Query(..., description="URL publique IG/FB à embarquer"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Récupère les données oEmbed pour un post Instagram.
    
    APP REVIEW NOTES:
    1. App Feature: Social media monitoring platform that embeds Instagram posts in user dashboards
    2. Permission: Meta oEmbed Read enables fetching oEmbed data (thumbnails, HTML, metadata)
    3. End-User Benefit: Users can preview Instagram content directly in veyl.io without leaving the platform
    """
    tokens = _get_all_meta_tokens(db, current_user)
    if not tokens:
        raise HTTPException(
            status_code=500,
            detail="No Meta access token available. Please configure META_LONG_TOKEN or IG_ACCESS_TOKEN, or connect your Instagram/Facebook account."
        )
    return await _fetch_oembed_with_tokens(url, tokens)


@router.get("/oembed/public")
async def get_oembed_public(
    url: str = Query(..., description="URL publique IG/FB à embarquer"),
    db: Session = Depends(get_db),
):
    """
    Public endpoint for oEmbed demo (no authentication required).
    Uses system tokens only (no user authentication required).
    """
    tokens = _get_all_meta_tokens(db, None)
    if not tokens:
        raise HTTPException(
            status_code=500,
            detail="No Meta access token configured. Please set META_LONG_TOKEN or IG_ACCESS_TOKEN."
        )
    return await _fetch_oembed_with_tokens(url, tokens)


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
    
    APP REVIEW NOTES:
    1. App Feature: Hashtag search and monitoring for Instagram content discovery
    2. Permission: Instagram Public Content Access enables searching public Instagram posts by hashtag
    3. End-User Benefit: Users can discover and monitor trending Instagram content by hashtag, 
       enabling content research and trend analysis for their projects.
    
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
    
    APP REVIEW NOTES:
    1. App Feature: Facebook Page content monitoring and analysis
    2. Permission: Page Public Content Access enables reading public posts from Facebook Pages
    3. End-User Benefit: Users can monitor and analyze public content from Facebook Pages 
       they manage or follow, enabling comprehensive social media monitoring across platforms.
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
    
    APP REVIEW NOTES:
    1. App Feature: Analytics dashboard for Instagram creators to track performance metrics
    2. Permissions: 
       - instagram_manage_insights: Allows fetching Instagram Business account insights
       - read_insights: Allows reading insights data for Facebook Pages
    3. End-User Benefit: Creators can monitor their Instagram performance (followers, reach, impressions) 
       directly in veyl.io analytics dashboard, enabling data-driven content strategy decisions.
    
    This endpoint uses the Meta Graph API insights endpoint to fetch metrics like:
    - followers_count, media_count (account metrics)
    - impressions, reach, engagement (post metrics)
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

