# app.py
from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.openapi.utils import get_openapi  # type: ignore
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
from auth_unified.oauth_accounts_endpoints import oauth_accounts_router

# Import des modules CRUD
from posts.posts_endpoints import posts_router
from hashtags.hashtags_endpoints import hashtags_router
from platforms.platforms_endpoints import platforms_router
from analytics.analytics_endpoints import analytics_router
from projects.projects_endpoints import projects_router
from meta.meta_endpoints import router as meta_router
from tiktok.tiktok_endpoints import router as tiktok_router
from webhooks.webhooks_endpoints import webhooks_router

# Import rate limiting
from core.ratelimit import setup_rate_limit
from core.middleware import RequestIDMiddleware, ErrorHandlerMiddleware

app = FastAPI(
    title="Insider Trends API",
    version="2.0.0",
    description="API pour l'analyse des tendances",
    # Configuration pour Railway proxy
    # root_path est utilisé quand l'app est derrière un proxy (Railway, nginx, etc.)
    # Railway ajoute automatiquement les headers X-Forwarded-*
    root_path="",  # Laisser vide pour Railway (pas de sous-chemin)
    redirect_slashes=False,  # Désactiver pour éviter les redirections 307
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    security_schemes["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    paths = openapi_schema.get("paths", {})
    http_methods = {"get", "post", "put", "patch", "delete", "options", "head"}
    for path_item in paths.values():
        for method_name, operation in path_item.items():
            if method_name.lower() in http_methods and isinstance(operation, dict):
                operation.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Middleware de tracing (Request ID) - doit être avant les autres
app.add_middleware(RequestIDMiddleware)

# Middleware de gestion d'erreurs standardisé
app.add_middleware(ErrorHandlerMiddleware)

# Configuration du rate limiting
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
        logger.warning(f"X-Forwarded-Proto inattendu: {forwarded_proto} pour {request.url.path}")
    
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

# CORS
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
app.include_router(oauth_accounts_router)
app.include_router(posts_router)
app.include_router(hashtags_router)
app.include_router(platforms_router)
app.include_router(analytics_router)
app.include_router(projects_router)
app.include_router(meta_router)
app.include_router(tiktok_router)
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

@app.get("/health")
@app.get("/healthz")
@app.get("/api/healthz")
def healthz():
    """Health check Kubernetes - pas de rate limit"""
    return {"status": "ok", "message": "API running"}


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
# LIFECYCLE EVENTS
# =====================================================

@app.on_event("startup")
async def startup_event():
    """Démarrage de l'application - Création des tables"""
    # Créer les tables si elles n'existent pas
    logger.info("Création des tables de base de données...")
    try:
        from db.base import Base, engine
        # Importer tous les modèles pour qu'ils soient enregistrés dans Base.metadata
        from db.models import User, OAuthAccount, Platform, Hashtag, Post, PostHashtag, Subscription, Project, ProjectHashtag, ProjectCreator
        Base.metadata.create_all(bind=engine)
        logger.info("Tables de base de données créées/vérifiées")
    except Exception as e:
        logger.error(f"Erreur création tables: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        raise  # Propager l'erreur pour arrêter le démarrage si problème
