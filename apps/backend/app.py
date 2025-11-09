# app.py - REFACTORISÉ - SABOTAGE ÉLIMINÉ - SÉCURISÉ - REDIS INTÉGRÉ !
from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
import time
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Import des modules unifiés
from auth_unified.auth_endpoints import auth_router
from auth_unified.oauth_endpoints import oauth_router

# Import des modules CRUD
from posts.posts_endpoints import posts_router
from hashtags.hashtags_endpoints import hashtags_router
from platforms.platforms_endpoints import platforms_router
from analytics.analytics_endpoints import analytics_router
from jobs.jobs_endpoints import jobs_router
from projects.projects_endpoints import projects_router
from meta.meta_routes import router as meta_router

# Import Redis et rate limiting
from core.redis_client import redis
from core.ratelimit import setup_rate_limit, limiter

app = FastAPI(
    title="Insider Trends API",
    version="2.0.0",
    description="API refactorisée pour l'analyse des tendances - SÉCURISÉE",
    # Configuration pour Railway proxy
    # root_path est utilisé quand l'app est derrière un proxy (Railway, nginx, etc.)
    # Railway ajoute automatiquement les headers X-Forwarded-*
    root_path="",  # Laisser vide pour Railway (pas de sous-chemin)
    redirect_slashes=False,  # Désactiver pour éviter les redirections 307
)

# Configuration du rate limiting avec Redis
setup_rate_limit(app)

# Middleware pour gérer les headers Railway et éviter les redirections 307
@app.middleware("http")
async def railway_proxy_middleware(request, call_next):
    """
    Middleware pour gérer correctement les requêtes Railway.
    
    Railway gère HTTPS via son proxy, mais route les requêtes en HTTP vers le conteneur.
    Ce middleware :
    1. Détecte HTTPS via X-Forwarded-Proto (Railway l'ajoute automatiquement)
    2. NE FORCE PAS de redirection HTTPS (Railway le gère déjà)
    3. Ajoute les headers de sécurité appropriés
    """
    # Détecter HTTPS via X-Forwarded-Proto (Railway ajoute ce header automatiquement)
    forwarded_proto = request.headers.get("X-Forwarded-Proto", "").lower()
    is_https_request = forwarded_proto == "https"
    
    # Logger pour debugging (seulement en cas de problème)
    if forwarded_proto and forwarded_proto != "https" and forwarded_proto != "http":
        logger.warning(f"⚠️ X-Forwarded-Proto inattendu: {forwarded_proto} pour {request.url.path}")
    
    # IMPORTANT: Ne pas forcer de redirection HTTPS car Railway le gère déjà
    # Juste traiter la requête normalement
    
    response = await call_next(request)
    
    # Headers de sécurité
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Si la requête venait de HTTPS (via Railway proxy), ajouter HSTS
    if is_https_request:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# CORS - SÉCURISÉ
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://veyl.io",
        "https://www.veyl.io",
        "https://api.veyl.io",
        "http://localhost:3000",  # Dev uniquement
        "http://localhost:5173",  # Dev uniquement
        "http://localhost:8081",  # Dev uniquement - Frontend Insider
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type", 
        "Authorization", 
        "X-Requested-With",
        "Accept",
        "Origin",
        "X-Forwarded-Proto",  # Pour Railway/proxy
        "X-Forwarded-For",    # Pour Railway/proxy
    ],
    expose_headers=["X-Total-Count"],
    max_age=3600,  # Cache preflight requests
)

# Inclusion des routers
app.include_router(auth_router)
app.include_router(oauth_router)
app.include_router(posts_router)
app.include_router(hashtags_router)
app.include_router(platforms_router)
app.include_router(analytics_router)
app.include_router(jobs_router)
app.include_router(projects_router)
app.include_router(meta_router)
from auth_unified.oauth_accounts_endpoints import oauth_accounts_router
app.include_router(oauth_accounts_router)
from webhooks.webhooks_endpoints import webhooks_router
app.include_router(webhooks_router)

# =====================================================
# ENDPOINTS DE BASE - SIMPLES ET PROPRES
# =====================================================

@app.get("/")
def root():
    """Endpoint racine - pas de rate limit (health check)"""
    return {
        "message": "Insider Trends API",
        "version": "2.0.0",
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/ping")
def ping():
    """Health check simple - pas de rate limit"""
    return {"pong": True, "timestamp": int(time.time())}

@app.get("/healthz")
@app.get("/api/healthz")
def healthz():
    """Health check Kubernetes - pas de rate limit"""
    return {"status": "ok", "message": "API running"}

@app.get("/api/v1/meilisearch/test")
def test_meilisearch():
    """Test de connexion Meilisearch"""
    from services.meilisearch_client import meilisearch_service
    
    if not meilisearch_service.client:
        return {
            "status": "error",
            "message": "Meilisearch client non initialisé",
            "check": "Vérifier MEILI_HOST et MEILI_MASTER_KEY"
        }
    
    try:
        stats = meilisearch_service.get_stats()
        return {
            "status": "ok",
            "message": "Meilisearch connecté avec succès",
            "stats": stats,
            "index_name": meilisearch_service.index_name
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur connexion Meilisearch: {str(e)}"
        }

@app.get("/api/v1/tiktok/test")
async def test_tiktok():
    """Test de connexion TikTok API"""
    from services.tiktok_service import tiktok_service
    
    if not tiktok_service.client_id or not tiktok_service.client_secret:
        return {
            "status": "error",
            "message": "TikTok credentials manquants",
            "check": "Vérifier TIKTOK_CLIENT_KEY et TIKTOK_CLIENT_SECRET"
        }
    
    try:
        token = await tiktok_service.get_access_token()
        if token:
            return {
                "status": "ok",
                "message": "TikTok API connecté avec succès",
                "has_token": True,
                "client_id": tiktok_service.client_id[:8] + "..."  # Masquer partiellement
            }
        else:
            return {
                "status": "error",
                "message": "Impossible d'obtenir le token TikTok",
                "check": "Vérifier les credentials ou statut de l'application TikTok"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur connexion TikTok: {str(e)}"
        }

@app.get("/api/v1/oauth/debug/tiktok")
def debug_tiktok_oauth():
    """Debug: voir l'URL OAuth TikTok générée et la configuration"""
    import os
    from auth_unified.oauth_service import OAuthService
    from core.config import settings
    oauth_service = OAuthService()
    
    try:
        auth_data = oauth_service.start_tiktok_auth()
        
        # Récupérer les valeurs réelles des settings
        client_key = settings.TIKTOK_CLIENT_KEY
        client_secret = settings.TIKTOK_CLIENT_SECRET
        redirect_uri = settings.TIKTOK_REDIRECT_URI
        
        return {
            "status": "ok",
            "auth_url": auth_data["auth_url"],
            "state": auth_data["state"],
            "config": {
                "has_client_key": bool(client_key),
                "client_key_length": len(client_key) if client_key else 0,
                "client_key_preview": client_key[:10] + "..." if client_key and len(client_key) > 10 else (client_key if client_key else None),
                "has_client_secret": bool(client_secret),
                "client_secret_length": len(client_secret) if client_secret else 0,
                "redirect_uri": redirect_uri,
                "redirect_uri_matches": redirect_uri == "https://veyl.io/api/v1/auth/tiktok/callback" or redirect_uri == "https://api.veyl.io/api/v1/auth/tiktok/callback"
            },
            "recommendations": {
                "check_tiktok_portal": "Vérifier que le redirect_uri dans TikTok Developer Portal correspond EXACTEMENT à: " + redirect_uri,
                "check_app_status": "Vérifier que l'application TikTok est approuvée/en production dans TikTok Developer Portal",
                "check_client_key": "Vérifier que TIKTOK_CLIENT_KEY dans Railway correspond au Client Key dans TikTok Developer Portal"
            }
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "config_check": {
                "TIKTOK_CLIENT_KEY_set": bool(os.getenv("TIKTOK_CLIENT_KEY")),
                "TIKTOK_CLIENT_SECRET_set": bool(os.getenv("TIKTOK_CLIENT_SECRET")),
                "TIKTOK_REDIRECT_URI_set": bool(os.getenv("TIKTOK_REDIRECT_URI")),
            }
        }

@app.get("/api/v1/oauth/debug/google")
def debug_google_oauth():
    """Debug: voir l'URL OAuth Google générée"""
    from core.config import settings
    from fastapi import HTTPException
    
    try:
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        client_id_set = bool(settings.GOOGLE_CLIENT_ID)
        client_secret_set = bool(settings.GOOGLE_CLIENT_SECRET)
        
        if not client_id_set:
            return {
                "status": "error",
                "message": "GOOGLE_CLIENT_ID non configuré dans Railway",
                "redirect_uri_used": redirect_uri,
                "client_id_set": False,
                "client_secret_set": client_secret_set
            }
        
        from auth_unified.oauth_service import OAuthService
        oauth_service = OAuthService()
        auth_data = oauth_service.start_google_auth()
        
        return {
            "status": "ok",
            "auth_url": auth_data["auth_url"],
            "redirect_uri_used": redirect_uri,
            "client_id_set": client_id_set,
            "client_secret_set": client_secret_set,
            "client_id_preview": settings.GOOGLE_CLIENT_ID[:20] + "..." if settings.GOOGLE_CLIENT_ID else None,
            "state": auth_data["state"],
            "instructions": "Vérifier que 'redirect_uri_used' correspond EXACTEMENT à celui dans Google Console"
        }
    except HTTPException as e:
        return {
            "status": "error",
            "message": e.detail,
            "status_code": e.status_code,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "client_id_set": bool(settings.GOOGLE_CLIENT_ID)
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc(),
            "redirect_uri": settings.GOOGLE_REDIRECT_URI if hasattr(settings, 'GOOGLE_REDIRECT_URI') else "N/A",
            "client_id_set": bool(settings.GOOGLE_CLIENT_ID) if hasattr(settings, 'GOOGLE_CLIENT_ID') else False
        }

@app.get("/api/v1/oauth/debug/instagram")
def debug_instagram_oauth():
    """Debug: voir l'URL OAuth Instagram générée"""
    from core.config import settings
    from fastapi import HTTPException
    
    try:
        redirect_uri = settings.IG_REDIRECT_URI
        app_id_set = bool(settings.IG_APP_ID)
        app_secret_set = bool(settings.IG_APP_SECRET)
        
        # Validation de l'App ID
        app_id_raw = settings.IG_APP_ID.strip() if settings.IG_APP_ID else None
        app_id_valid = False
        app_id_error = None
        
        if app_id_raw:
            # Facebook App ID doit être numérique et avoir entre 15 et 17 chiffres
            if app_id_raw.isdigit() and 15 <= len(app_id_raw) <= 17:
                app_id_valid = True
            else:
                app_id_error = f"App ID invalide: '{app_id_raw}' - doit être un nombre de 15-17 chiffres"
        
        if not app_id_set:
            return {
                "status": "error",
                "message": "IG_APP_ID non configuré dans Railway",
                "redirect_uri_used": redirect_uri,
                "app_id_set": False,
                "app_secret_set": app_secret_set,
                "app_id_valid": False
            }
        
        if not app_id_valid and app_id_error:
            return {
                "status": "error",
                "message": app_id_error,
                "redirect_uri_used": redirect_uri,
                "app_id_set": app_id_set,
                "app_id_preview": app_id_raw[:20] + "..." if app_id_raw else None,
                "app_id_length": len(app_id_raw) if app_id_raw else 0,
                "app_id_is_digit": app_id_raw.isdigit() if app_id_raw else False,
                "app_secret_set": app_secret_set,
                "instructions": "L'App ID Facebook doit être un nombre de 15-17 chiffres. Vérifiez dans Railway que IG_APP_ID ne contient pas d'espaces ou de caractères invalides."
            }
        
        from auth_unified.oauth_service import OAuthService
        oauth_service = OAuthService()
        auth_data = oauth_service.start_instagram_auth()
        
        return {
            "status": "ok",
            "auth_url": auth_data["auth_url"],
            "redirect_uri_used": redirect_uri,
            "app_id_set": app_id_set,
            "app_id_valid": app_id_valid,
            "app_id_preview": app_id_raw[:10] + "..." if app_id_raw else None,
            "app_id_length": len(app_id_raw) if app_id_raw else 0,
            "app_secret_set": app_secret_set,
            "state": auth_data["state"],
            "instructions": "Vérifier que 'redirect_uri_used' correspond EXACTEMENT à celui dans Facebook Developer Console > Valid OAuth Redirect URIs"
        }
    except HTTPException as e:
        return {
            "status": "error",
            "message": e.detail,
            "status_code": e.status_code,
            "redirect_uri": settings.IG_REDIRECT_URI if hasattr(settings, 'IG_REDIRECT_URI') else "N/A",
            "app_id_set": bool(settings.IG_APP_ID) if hasattr(settings, 'IG_APP_ID') else False
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc(),
            "redirect_uri": settings.IG_REDIRECT_URI if hasattr(settings, 'IG_REDIRECT_URI') else "N/A",
            "app_id_set": bool(settings.IG_APP_ID) if hasattr(settings, 'IG_APP_ID') else False
        }

# =====================================================
# LIFECYCLE EVENTS - REDIS STARTUP CHECK
# =====================================================

@app.on_event("startup")
async def startup_event():
    """Démarrage de l'application - Création des tables"""
    # Vérifier Redis
    try:
        await redis.ping()
        logger.info("✅ Redis OK - Rate limiting activé")
    except Exception as e:
        logger.warning(f"⚠️ Redis KO: {e} - Rate limiting désactivé")
    
    # Créer les tables si elles n'existent pas
    logger.info("🔄 Création des tables de base de données...")
    try:
        from db.base import Base, engine
        # Importer tous les modèles pour qu'ils soient enregistrés dans Base.metadata
        from db.models import User, OAuthAccount, Platform, Hashtag, Post, PostHashtag, Subscription, Project, ProjectHashtag, ProjectCreator
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables de base de données créées/vérifiées")
    except Exception as e:
        logger.error(f"❌ Erreur création tables: {e}")
        import traceback
        traceback.print_exc()
        raise  # Propager l'erreur pour arrêter le démarrage si problème
