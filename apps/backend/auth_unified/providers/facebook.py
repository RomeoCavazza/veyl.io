# auth_unified/providers/facebook.py
"""Provider OAuth pour Facebook"""
import logging
import httpx
from typing import Dict, Any
from urllib.parse import urlencode
from fastapi import HTTPException

from core.config import settings
from .base import BaseOAuthProvider

logger = logging.getLogger(__name__)


class FacebookOAuthProvider(BaseOAuthProvider):
    """Provider OAuth pour Facebook"""
    
    def get_provider_name(self) -> str:
        return "facebook"
    
    def get_scopes(self) -> str:
        # Scopes de base uniquement (les scopes avancés nécessitent App Review et seront automatiquement disponibles une fois approuvés)
        return "public_profile,email,pages_show_list"
    
    def get_redirect_uri(self) -> str:
        return settings.FB_REDIRECT_URI
    
    def build_auth_url(self, state: str) -> str:
        """Construit l'URL d'autorisation Facebook"""
        params = {
            "client_id": settings.FB_APP_ID,
            "redirect_uri": self.get_redirect_uri(),
            "response_type": "code",
            "scope": self.get_scopes(),
            "state": state,
        }
        return "https://www.facebook.com/v21.0/dialog/oauth?" + urlencode(params)
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Échange le code OAuth contre un access token Facebook"""
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(
                "https://graph.facebook.com/v21.0/oauth/access_token",
                params={
                    "client_id": settings.FB_APP_ID,
                    "client_secret": settings.FB_APP_SECRET,
                    "redirect_uri": self.get_redirect_uri(),
                    "code": code,
                },
            )
            r.raise_for_status()
            data = r.json()
            access_token = data.get("access_token")
            if not access_token:
                raise HTTPException(status_code=400, detail="Access token manquant")
            return {"access_token": access_token}
    
    async def get_user_info(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les informations utilisateur Facebook"""
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token manquant")
        
        # Créer un nouveau client (le précédent est fermé)
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(
                "https://graph.facebook.com/v21.0/me",
                params={
                    "fields": "id,name,email",
                    "access_token": access_token
                }
            )
            r.raise_for_status()
            user_info = r.json()
            
            fb_user_id = user_info.get("id")
            email = user_info.get("email")
            name = user_info.get("name")
            
            if not fb_user_id:
                raise HTTPException(status_code=400, detail="Impossible de récupérer l'ID utilisateur Facebook")
            
            # Email peut être None selon les permissions
            if not email:
                email = f"facebook_{fb_user_id}@insidr.dev"
            
            # Ne passer que si c'est un email réel (pas généré)
            email_to_pass = None
            if email and not email.endswith(('@veyl.io', '@insidr.dev')) and '@' in email:
                email_to_pass = email
            
            return {
                "provider_user_id": str(fb_user_id),
                "name": name or f"Facebook User {fb_user_id}",
                "email": email_to_pass,  # None si email généré
                "access_token": access_token
            }


