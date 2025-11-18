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
                "fields": "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count,username",
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
            # PRIORITÉ 1: Extraire username depuis l'API response (le plus fiable)
            author = item.get("username")
            
            # PRIORITÉ 2: Extraire username depuis permalink si pas dans API response
            if not author:
                permalink = item.get("permalink")
                if permalink:
                    # Format: https://www.instagram.com/p/{code}/ ou https://www.instagram.com/{username}/p/{code}/
                    permalink_match = re.search(r'instagram\.com/([^/]+)/', permalink)
                    if permalink_match:
                        potential_username = permalink_match.group(1)
                        # Ignorer les patterns spéciaux comme 'p', 'reel', etc.
                        if potential_username not in ['p', 'reel', 'tv', 'stories']:
                            author = potential_username
            
            defaults = {
                "author": author,
                "caption": item.get("caption", ""),
                "media_url": item.get("media_url"),
                "posted_at": parse_timestamp(item.get("timestamp")),
                "metrics": json.dumps({
                    "likes": item.get("like_count", 0),
                    "comments": item.get("comments_count", 0),
                    "like_count": item.get("like_count", 0),  # Ajouter aussi pour compatibilité
                    "comment_count": item.get("comments_count", 0),  # Ajouter aussi pour compatibilité
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
        # Pour toutes les erreurs Meta API (400, 401, 403, 404, 500, etc.), faire le fallback DB
        logger.warning(f"Meta API returned {http_exc.status_code} for #{tag}, falling back to DB: {http_exc.detail}")
        # Ne pas relancer l'exception, continuer vers le fallback DB
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
        api_payload = payload_data["api_payload"]
        
        # Extraire username depuis api_payload ou permalink
        author = post.author
        if not author and api_payload:
            author = (
                api_payload.get('username')
                or api_payload.get('owner_username')
                or api_payload.get('from', {}).get('username')
            )
        # Si toujours pas trouvé, essayer depuis permalink (si stocké dans api_payload)
        if not author and api_payload:
            permalink = api_payload.get('permalink')
            if permalink:
                permalink_match = re.search(r'instagram\.com/([^/]+)/', permalink)
                if permalink_match:
                    potential_username = permalink_match.group(1)
                    if potential_username not in ['p', 'reel', 'tv', 'stories']:
                        author = potential_username
        
        results.append({
            "id": post.id,
            "caption": post.caption,
            "media_url": post.media_url,
            "permalink": api_payload.get('permalink') if api_payload else None,
            "username": author,
            "author": author,
            "like_count": metrics.get("likes") or metrics.get("like_count") or 0,
            "comments_count": metrics.get("comments") or metrics.get("comments_count") or metrics.get("comment_count") or 0,
            "timestamp": post.posted_at.isoformat() if post.posted_at else None,
            "media_type": api_payload.get('media_type') if api_payload else None,
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
    page_id: str = Query(..., min_length=1, description="Facebook Page ID"),
    limit: int = Query(10, ge=1, le=50, description="Nombre de posts à récupérer"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Récupère les posts publics d'une page Facebook.
    
    APP REVIEW NOTES:
    1. App Feature: Facebook Page content monitoring and analysis for social media intelligence
    2. Permission: pages_read_user_content - Allows reading user-generated content on Facebook Pages (posts, comments, ratings)
    3. End-User Benefit: Users can monitor and analyze public content from Facebook Pages 
       they manage or follow, enabling comprehensive social media monitoring across platforms (Instagram + Facebook).
       This helps users track brand mentions, competitor activity, and industry trends.
    
    This endpoint uses the Meta Graph API to fetch public posts from Facebook Pages:
    - Post content (message, created_time, permalink_url)
    - Engagement metrics (reactions, comments)
    - Media attachments if available
    """
    from services.meta_client import MetaAPIError
    
    try:
        # Appeler Meta API pour récupérer les posts de la Page
        # Fields disponibles: id, message, created_time, permalink_url, reactions, comments, attachments, etc.
        posts_response = await call_meta(
            method="GET",
            endpoint=f"v21.0/{page_id}/posts",
            params={
                "fields": "id,message,created_time,permalink_url,reactions.summary(true),comments.summary(true),attachments{media,subattachments}",
                "limit": limit,
            },
            access_token=_get_meta_token(db, current_user) if current_user else None,
        )
        
        # Meta API retourne: {"data": [...], "paging": {...}}
        posts_data = posts_response.get("data", [])
        
        # Transformer les posts pour un format plus cohérent avec Instagram
        transformed_posts = []
        for post in posts_data:
            # Extraire les métriques d'engagement
            reactions = post.get("reactions", {}).get("summary", {})
            comments = post.get("comments", {}).get("summary", {})
            
            # Extraire les médias si disponibles
            attachments = post.get("attachments", {}).get("data", [])
            media_url = None
            if attachments and len(attachments) > 0:
                # Prendre le premier média
                first_attachment = attachments[0]
                if first_attachment.get("media"):
                    media_url = first_attachment["media"].get("image", {}).get("src")
                elif first_attachment.get("subattachments"):
                    subattachments = first_attachment["subattachments"].get("data", [])
                    if subattachments and len(subattachments) > 0:
                        media_url = subattachments[0].get("media", {}).get("image", {}).get("src")
            
            transformed_posts.append({
                "id": post.get("id"),
                "message": post.get("message"),
                "created_time": post.get("created_time"),
                "permalink_url": post.get("permalink_url"),
                "like_count": reactions.get("total_count", 0),
                "comment_count": comments.get("total_count", 0),
                "media_url": media_url,
                "platform": "facebook",
            })
        
        return {
            "page_id": page_id,
            "data": transformed_posts,
            "total": len(transformed_posts),
            "raw_data": posts_data,  # Garder les données brutes pour debug
        }
        
    except MetaAPIError as e:
        logger.error(f"Meta API error fetching page posts for {page_id}: {e}")
        raise HTTPException(
            status_code=e.status_code if hasattr(e, 'status_code') else 500,
            detail={
                "error": "Meta API error",
                "message": str(e),
                "page_id": page_id,
            }
        )
    except Exception as e:
        logger.error(f"Error fetching page posts for {page_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal error",
                "message": f"Error fetching page posts: {str(e)}",
                "page_id": page_id,
            }
        )


async def _get_ig_business_account_id(db: Session, current_user: Optional[User], access_token: str) -> Optional[str]:
    """Récupère l'Instagram Business Account ID depuis les Pages Facebook de l'utilisateur"""
    import httpx
    
    try:
        # Récupérer les Pages Facebook de l'utilisateur
        async with httpx.AsyncClient(timeout=20) as client:
            pages_response = await client.get(
                "https://graph.facebook.com/v21.0/me/accounts",
                params={"access_token": access_token}
            )
            if pages_response.status_code != 200:
                logger.warning(f"Failed to fetch pages: {pages_response.status_code}")
                return None
            
            pages_data = pages_response.json().get("data", [])
            
            # Pour chaque Page, chercher l'IG Business Account
            for page in pages_data:
                page_id = page.get("id")
                if not page_id:
                    continue
                
                try:
                    page_response = await client.get(
                        f"https://graph.facebook.com/v21.0/{page_id}",
                        params={
                            "fields": "instagram_business_account{id}",
                            "access_token": access_token
                        }
                    )
                    if page_response.status_code == 200:
                        ig_account = page_response.json().get("instagram_business_account")
                        if ig_account and ig_account.get("id"):
                            ig_business_id = ig_account["id"]
                            logger.info(f"Found IG Business Account ID: {ig_business_id}")
                            return ig_business_id
                except Exception as e:
                    logger.warning(f"Error fetching IG Business Account for page {page_id}: {e}")
                    continue
        
        return None
    except Exception as e:
        logger.error(f"Error in _get_ig_business_account_id: {e}")
        return None


@router.get("/insights")
async def get_insights(
    resource_id: str = Query(..., description="IG Business ID, Page ID, ou 'me' pour utiliser le compte connecté"),
    metrics: str = Query(..., description="Liste metrics Graph API (comma-separated)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Récupère les insights (métriques) pour un compte Instagram Business ou une page Facebook.
    
    Si resource_id='me', récupère automatiquement l'IG Business Account ID de l'utilisateur connecté.
    
    APP REVIEW NOTES:
    1. App Feature: Analytics dashboard for Instagram creators to track performance metrics
    2. Permissions: 
       - instagram_manage_insights: Allows fetching Instagram Business account insights
       - instagram_business_manage_insights: Allows fetching Instagram professional account insights
       - read_insights: Allows reading insights data for Facebook Pages
    3. End-User Benefit: Creators can monitor their Instagram performance (followers, reach, impressions) 
       directly in veyl.io analytics dashboard, enabling data-driven content strategy decisions.
    
    This endpoint uses the Meta Graph API insights endpoint to fetch metrics like:
    - followers_count, media_count (account metrics)
    - impressions, reach, engagement (post metrics)
    - profile_views, website_clicks (account metrics)
    """
    from services.meta_client import MetaAPIError
    
    # Si resource_id='me', récupérer l'IG Business Account ID de l'utilisateur
    actual_resource_id = resource_id
    if resource_id == "me":
        if not current_user:
            raise HTTPException(
                status_code=401,
                detail="Authentication required when using resource_id='me'. Please log in or provide a specific resource_id."
            )
        
        # Récupérer le token de l'utilisateur
        try:
            access_token = _get_meta_token(db, current_user)
        except HTTPException:
            raise HTTPException(
                status_code=400,
                detail="No Meta/Instagram account connected. Please connect your Instagram or Facebook account in Profile settings."
            )
        
        # Récupérer l'IG Business Account ID
        ig_business_id = await _get_ig_business_account_id(db, current_user, access_token)
        if not ig_business_id:
            raise HTTPException(
                status_code=404,
                detail="Instagram Business Account not found. Please ensure your Facebook Page is connected to an Instagram Business account."
            )
        
        actual_resource_id = ig_business_id
        logger.info(f"Using IG Business Account ID for user {current_user.id}: {actual_resource_id}")
    
    # Parser les metrics (peut être comma-separated ou déjà un array)
    metrics_list = [m.strip() for m in metrics.split(",")] if isinstance(metrics, str) else metrics
    
    try:
        # Appeler Meta API pour récupérer les insights
        # Note: Meta API retourne un objet avec 'data' array contenant les métriques
        insights_response = await call_meta(
            method="GET",
            endpoint=f"v21.0/{actual_resource_id}/insights",
            params={"metric": ",".join(metrics_list)},
            access_token=_get_meta_token(db, current_user) if current_user else None,
        )
        
        # Meta API retourne: {"data": [{"name": "followers_count", "values": [...]}, ...]}
        # On transforme en format plus simple pour le frontend
        insights_data = insights_response.get("data", [])
        
        # Extraire les valeurs des métriques
        result = {}
        for metric_data in insights_data:
            metric_name = metric_data.get("name")
            values = metric_data.get("values", [])
            # Prendre la dernière valeur (ou la somme si plusieurs périodes)
            if values:
                if len(values) == 1:
                    result[metric_name] = values[0].get("value", 0)
                else:
                    # Pour les métriques avec plusieurs périodes, prendre la somme ou la dernière
                    result[metric_name] = sum(v.get("value", 0) for v in values)
            else:
                result[metric_name] = 0
        
        # Ajouter les métriques de compte si disponibles (via endpoint account)
        # Note: followers_count et media_count ne sont pas dans insights, mais dans le profil
        # On peut les récupérer séparément si nécessaire
        
        return {
            "resource_id": actual_resource_id,
            "metrics": result,
            "raw_data": insights_data,  # Garder les données brutes pour debug
        }
        
    except MetaAPIError as e:
        logger.error(f"Meta API error fetching insights for {actual_resource_id}: {e}")
        raise HTTPException(
            status_code=e.status_code if hasattr(e, 'status_code') else 500,
            detail={
                "error": "Meta API error",
                "message": str(e),
                "resource_id": actual_resource_id,
            }
        )
    except Exception as e:
        logger.error(f"Error fetching insights for {actual_resource_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal error",
                "message": f"Error fetching insights: {str(e)}",
                "resource_id": actual_resource_id,
            }
        )


@router.get("/ig-business-profile")
async def get_instagram_business_profile(
    ig_business_account_id: str = Query(..., description="IG Business Account ID ou 'me' pour utiliser le compte connecté"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Récupère le profil d'un compte Instagram Business.
    
    Si ig_business_account_id='me', récupère automatiquement l'IG Business Account ID de l'utilisateur connecté.
    
    APP REVIEW NOTES:
    1. App Feature: Creator profile display in projects and analytics dashboards
    2. Permission: instagram_business_basic - Allows reading Instagram Business account profile information
    3. End-User Benefit: Users can view detailed creator profiles (username, followers, media count, bio) 
       directly in veyl.io without leaving the platform, enabling better creator discovery and analysis.
    
    This endpoint uses the Meta Graph API to fetch Instagram Business account information:
    - username, profile_picture_url
    - followers_count, media_count
    - website, biography
    """
    from services.meta_client import MetaAPIError
    
    # Si ig_business_account_id='me', récupérer l'IG Business Account ID de l'utilisateur
    actual_ig_business_id = ig_business_account_id
    if ig_business_account_id == "me":
        if not current_user:
            raise HTTPException(
                status_code=401,
                detail="Authentication required when using ig_business_account_id='me'. Please log in or provide a specific IG Business Account ID."
            )
        
        # Récupérer le token de l'utilisateur
        try:
            access_token = _get_meta_token(db, current_user)
        except HTTPException:
            raise HTTPException(
                status_code=400,
                detail="No Meta/Instagram account connected. Please connect your Instagram or Facebook account in Profile settings."
            )
        
        # Récupérer l'IG Business Account ID
        ig_business_id = await _get_ig_business_account_id(db, current_user, access_token)
        if not ig_business_id:
            raise HTTPException(
                status_code=404,
                detail="Instagram Business Account not found. Please ensure your Facebook Page is connected to an Instagram Business account."
            )
        
        actual_ig_business_id = ig_business_id
        logger.info(f"Using IG Business Account ID for user {current_user.id}: {actual_ig_business_id}")
    
    try:
        # Appeler Meta API pour récupérer le profil Instagram Business
        # Fields disponibles: username, profile_picture_url, followers_count, media_count, website, biography
        profile_data = await call_meta(
            method="GET",
            endpoint=f"v21.0/{actual_ig_business_id}",
            params={
                "fields": "username,profile_picture_url,followers_count,media_count,website,biography"
            },
            access_token=_get_meta_token(db, current_user) if current_user else None,
        )
        
        return {
            "ig_business_account_id": actual_ig_business_id,
            "username": profile_data.get("username"),
            "profile_picture_url": profile_data.get("profile_picture_url"),
            "followers_count": profile_data.get("followers_count", 0),
            "media_count": profile_data.get("media_count", 0),
            "website": profile_data.get("website"),
            "biography": profile_data.get("biography"),
            "raw_data": profile_data,  # Garder les données brutes pour debug
        }
        
    except MetaAPIError as e:
        logger.error(f"Meta API error fetching IG Business profile for {actual_ig_business_id}: {e}")
        raise HTTPException(
            status_code=e.status_code if hasattr(e, 'status_code') else 500,
            detail={
                "error": "Meta API error",
                "message": str(e),
                "ig_business_account_id": actual_ig_business_id,
            }
        )
    except Exception as e:
        logger.error(f"Error fetching IG Business profile for {actual_ig_business_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal error",
                "message": f"Error fetching Instagram Business profile: {str(e)}",
                "ig_business_account_id": actual_ig_business_id,
            }
        )


@router.get("/ig-profile")
async def get_instagram_profile(
    username: Optional[str] = Query(None, description="Instagram username (sans @)"),
    user_id: Optional[str] = Query(None, description="Instagram user ID"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """
    Récupère le profil d'un compte Instagram (personnel ou Business).
    
    Utilise instagram_basic pour les comptes personnels ou instagram_business_basic pour les comptes Business.
    
    APP REVIEW NOTES:
    1. App Feature: Creator profile display in projects and analytics dashboards
    2. Permission: instagram_basic - Allows reading Instagram personal account profile information
    3. End-User Benefit: Users can view Instagram creator profiles (username, profile picture, bio) 
       directly in veyl.io, enabling better creator discovery and analysis for both personal and business accounts.
    
    This endpoint uses the Meta Graph API to fetch Instagram account information:
    - username, profile_picture_url
    - biography (if available)
    - followers_count, media_count (if Business account)
    """
    from services.meta_client import MetaAPIError
    
    if not username and not user_id:
        raise HTTPException(
            status_code=400,
            detail="Either username or user_id must be provided"
        )
    
    try:
        # Si on a un username, essayer de récupérer le profil
        # Note: Meta Graph API nécessite un user_id pour récupérer le profil
        # Pour instagram_basic, on peut utiliser l'endpoint /{user-id} avec les champs de base
        
        # Si user_id fourni, l'utiliser directement
        if user_id:
            profile_data = await call_meta(
                method="GET",
                endpoint=f"v21.0/{user_id}",
                params={
                    "fields": "username,profile_picture_url,biography"
                },
                access_token=_get_meta_token(db, current_user) if current_user else None,
            )
        else:
            # Si seulement username fourni, on ne peut pas récupérer directement via Graph API
            # Il faudrait d'abord chercher le user_id via hashtag search ou autre méthode
            # Pour l'instant, on retourne une erreur explicative
            raise HTTPException(
                status_code=400,
                detail="Instagram user_id is required. Username lookup is not directly supported by Meta Graph API. Please provide the Instagram user ID."
            )
        
        return {
            "user_id": user_id,
            "username": profile_data.get("username") or username,
            "profile_picture_url": profile_data.get("profile_picture_url"),
            "biography": profile_data.get("biography"),
            "raw_data": profile_data,  # Garder les données brutes pour debug
        }
        
    except MetaAPIError as e:
        logger.error(f"Meta API error fetching IG profile for {user_id or username}: {e}")
        raise HTTPException(
            status_code=e.status_code if hasattr(e, 'status_code') else 500,
            detail={
                "error": "Meta API error",
                "message": str(e),
                "user_id": user_id,
                "username": username,
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching IG profile for {user_id or username}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal error",
                "message": f"Error fetching Instagram profile: {str(e)}",
                "user_id": user_id,
                "username": username,
            }
        )


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

