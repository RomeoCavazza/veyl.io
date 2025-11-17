# oauth/oauth_endpoints.py
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from db.base import get_db
from core.config import settings
from urllib.parse import quote
from .oauth_service import OAuthService

logger = logging.getLogger(__name__)
oauth_router = APIRouter(prefix="/api/v1/auth", tags=["oauth"])
oauth_service = OAuthService()

@oauth_router.get("/instagram/start")
def instagram_auth_start(user_id: Optional[UUID] = None):
    """Démarrer OAuth Instagram - Redirection directe"""
    auth_data = oauth_service.start_instagram_auth(user_id=user_id)
    return RedirectResponse(url=auth_data["auth_url"])

@oauth_router.get("/instagram/callback")
async def instagram_auth_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    error_description: str = None,
    db: Session = Depends(get_db)
):
    """Callback Instagram"""
    # settings et quote sont déjà importés en haut du fichier
    
    # Déterminer l'URL frontend
    if "veyl.io" in settings.IG_REDIRECT_URI:
        frontend_url = "https://veyl.io/auth/callback"
    else:
        frontend_url = "http://localhost:8081/auth/callback"
    
    # Gérer les erreurs OAuth de Facebook/Instagram
    if error:
        error_desc = quote(error_description or '')
        return RedirectResponse(url=f"{frontend_url}?error={quote(error)}&error_description={error_desc}")
    
    # Vérifier les paramètres requis
    if not code or not state:
        return RedirectResponse(url=f"{frontend_url}?error=missing_params&error_description={quote('Code ou state manquant dans la réponse Instagram')}")
    
    # Traiter le callback
    try:
        return await oauth_service.handle_instagram_callback(code, state, db)
    except HTTPException as e:
        # Rediriger vers le frontend avec l'erreur détaillée
        error_msg = quote(str(e.detail))
        return RedirectResponse(url=f"{frontend_url}?error=oauth_error&error_description={error_msg}")
    except Exception as e:
        # Capturer toutes les autres exceptions
        import traceback
        error_msg = quote(f"Erreur interne: {str(e)}")
        return RedirectResponse(url=f"{frontend_url}?error=internal_error&error_description={error_msg}")

@oauth_router.get("/callback")
async def auth_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """Callback général pour redirection vers localhost (dev uniquement)"""
    if error:
        return RedirectResponse(url=f"http://localhost:8081/auth/callback?error={error}")
    
    if code and state:
        # Appeler le callback Instagram (fallback pour dev)
        return await oauth_service.handle_instagram_callback(code, state, db)
    
    return RedirectResponse(url="http://localhost:8081/auth/callback")

@oauth_router.get("/facebook/start")
def facebook_auth_start(user_id: Optional[UUID] = None):
    """Démarrer OAuth Facebook - Redirection directe"""
    auth_data = oauth_service.start_facebook_auth(user_id=user_id)
    return RedirectResponse(url=auth_data["auth_url"])

@oauth_router.get("/facebook/callback")
async def facebook_auth_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    error_description: str = None,
    db: Session = Depends(get_db)
):
    """Callback Facebook"""
    # Déterminer l'URL frontend
    if "veyl.io" in settings.FB_REDIRECT_URI:
        frontend_url = "https://veyl.io/auth/callback"
    else:
        frontend_url = "http://localhost:8081/auth/callback"
    
    # Gérer les erreurs OAuth de Facebook
    if error:
        error_desc = quote(error_description or '')
        return RedirectResponse(url=f"{frontend_url}?error={quote(error)}&error_description={error_desc}")
    
    # Vérifier les paramètres requis
    if not code or not state:
        return RedirectResponse(url=f"{frontend_url}?error=missing_params&error_description={quote('Code ou state manquant dans la réponse Facebook')}")
    
    # Traiter le callback
    try:
        return await oauth_service.handle_facebook_callback(code, state, db)
    except HTTPException as e:
        # Rediriger vers le frontend avec l'erreur détaillée
        error_msg = quote(str(e.detail))
        return RedirectResponse(url=f"{frontend_url}?error=oauth_error&error_description={error_msg}")
    except Exception as e:
        # Capturer toutes les autres exceptions
        import traceback
        error_msg = quote(f"Erreur interne: {str(e)}")
        return RedirectResponse(url=f"{frontend_url}?error=internal_error&error_description={error_msg}")

@oauth_router.get("/google/start")
def google_auth_start():
    """Démarrer OAuth Google - Redirection directe"""
    auth_data = oauth_service.start_google_auth()
    return RedirectResponse(url=auth_data["auth_url"])

@oauth_router.get("/google/callback")
async def google_auth_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    error_description: str = None,
    db: Session = Depends(get_db)
):
    """Callback Google"""
    # settings et quote sont déjà importés en haut du fichier
    
    # Déterminer l'URL frontend
    if "veyl.io" in settings.GOOGLE_REDIRECT_URI:
        frontend_url = "https://veyl.io/auth/callback"
    else:
        frontend_url = "http://localhost:8081/auth/callback"
    
    # Gérer les erreurs OAuth de Google
    if error:
        error_desc = quote(error_description or '')
        return RedirectResponse(url=f"{frontend_url}?error={quote(error)}&error_description={error_desc}")
    
    # Vérifier les paramètres requis
    if not code or not state:
        return RedirectResponse(url=f"{frontend_url}?error=missing_params&error_description={quote('Code ou state manquant dans la réponse Google')}")
    
    # Traiter le callback
    try:
        return await oauth_service.handle_google_callback(code, state, db)
    except HTTPException as e:
        # Rediriger vers le frontend avec l'erreur détaillée
        error_msg = quote(str(e.detail))
        return RedirectResponse(url=f"{frontend_url}?error=oauth_error&error_description={error_msg}")
    except Exception as e:
        # Capturer toutes les autres exceptions
        import traceback
        error_msg = quote(f"Erreur interne: {str(e)}")
        return RedirectResponse(url=f"{frontend_url}?error=internal_error&error_description={error_msg}")

@oauth_router.get("/tiktok/start")
def tiktok_auth_start(user_id: Optional[UUID] = None):
    """Démarrer OAuth TikTok - Redirection directe"""
    auth_data = oauth_service.start_tiktok_auth(user_id=user_id)
    return RedirectResponse(url=auth_data["auth_url"])

@oauth_router.get("/tiktok/callback")
async def tiktok_auth_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    error_description: str = None,
    error_type: str = None,
    db: Session = Depends(get_db)
):
    """Callback TikTok"""
    # Déterminer l'URL frontend
    if "veyl.io" in settings.TIKTOK_REDIRECT_URI:
        frontend_url = "https://veyl.io/auth/callback"
    else:
        frontend_url = "http://localhost:8081/auth/callback"
    
    # Gérer les erreurs OAuth de TikTok
    if error:
        error_desc = quote(error_description or error_type or error)
        error_msg = f"TikTok OAuth Error: {error}"
        if error_type:
            error_msg += f" (type: {error_type})"
        
        # Messages d'aide spécifiques selon le type d'erreur
        if error == "unauthorized_client" or "client_key" in error.lower():
            error_msg += ")\n\n🔧 Solutions possibles:\n"
            error_msg += "1. Vérifiez que TIKTOK_CLIENT_KEY est configuré dans Railway\n"
            error_msg += "2. Vérifiez que le redirect_uri dans TikTok Developer Portal correspond EXACTEMENT à: " + settings.TIKTOK_REDIRECT_URI + "\n"
            error_msg += "3. Vérifiez que l'application TikTok est approuvée/en production\n"
            error_msg += "4. Vérifiez que le Client Key dans TikTok Portal correspond à TIKTOK_CLIENT_KEY"
        elif error == "invalid_request":
            error_msg += ")\n\n🔧 Vérifiez que tous les paramètres OAuth sont correctement configurés"
        elif error == "access_denied":
            error_msg += ")\n\n🔧 L'utilisateur a refusé l'autorisation"
        else:
            error_msg += ")"
            
        logger.error(f"TikTok OAuth Error: {error} - {error_description or error_type}")
        return RedirectResponse(url=f"{frontend_url}?error={quote(error_msg)}&error_description={error_desc}")
    
    # Vérifier les paramètres requis
    if not code or not state:
        return RedirectResponse(url=f"{frontend_url}?error=missing_params&error_description={quote('Code ou state manquant dans la réponse TikTok')}")
    
    # Traiter le callback
    try:
        return await oauth_service.handle_tiktok_callback(code, state, db)
    except HTTPException as e:
        # Rediriger vers le frontend avec l'erreur détaillée
        error_msg = quote(str(e.detail))
        return RedirectResponse(url=f"{frontend_url}?error=oauth_error&error_description={error_msg}")
    except Exception as e:
        # Capturer toutes les autres exceptions
        import traceback
        error_msg = quote(f"Erreur interne: {str(e)}")
        return RedirectResponse(url=f"{frontend_url}?error=internal_error&error_description={error_msg}")