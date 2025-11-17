# auth_unified/providers/tiktok.py
"""Provider OAuth pour TikTok"""
import logging
import httpx
import secrets
from typing import Dict, Any, Optional
from uuid import UUID
from urllib.parse import quote
from fastapi import HTTPException

from core.config import settings
from .base import BaseOAuthProvider

logger = logging.getLogger(__name__)


class TikTokOAuthProvider(BaseOAuthProvider):
    """Provider OAuth pour TikTok"""
    
    def get_provider_name(self) -> str:
        return "tiktok"
    
    def get_scopes(self) -> str:
        return "user.info.basic,user.info.profile,user.info.stats,video.list"
    
    def get_redirect_uri(self) -> str:
        return settings.TIKTOK_REDIRECT_URI.strip() if settings.TIKTOK_REDIRECT_URI else ""
    
    def generate_state(self, user_id: Optional[UUID] = None) -> str:
        """Génère un state TikTok (peut utiliser token_urlsafe ou format timestamp_userid)"""
        if user_id:
            # Utiliser le format de la classe de base
            return super().generate_state(user_id)
        # TikTok peut utiliser un token sécurisé aléatoire
        return secrets.token_urlsafe(32)
    
    def build_auth_url(self, state: str) -> str:
        """Construit l'URL d'autorisation TikTok"""
        client_key = settings.TIKTOK_CLIENT_KEY.strip() if settings.TIKTOK_CLIENT_KEY else None
        redirect_uri = self.get_redirect_uri()
        
        if not client_key:
            raise HTTPException(status_code=500, detail="TIKTOK_CLIENT_KEY vide ou non configuré")
        if not redirect_uri:
            raise HTTPException(status_code=500, detail="TIKTOK_REDIRECT_URI vide ou non configuré")
        
        # Validation
        if len(client_key) < 10:
            raise HTTPException(
                status_code=500,
                detail=f"TIKTOK_CLIENT_KEY semble invalide (trop court: {len(client_key)} caractères)"
            )
        
        if not redirect_uri.startswith("https://"):
            logger.warning(f"TikTok OAuth - Redirect URI ne commence pas par https:// : {redirect_uri}")
        
        params = {
            "client_key": client_key,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": self.get_scopes(),
            "state": state
        }
        
        query_parts = []
        for key, value in params.items():
            if key == "redirect_uri":
                encoded_value = quote(str(value), safe="/:")
            else:
                encoded_value = quote(str(value), safe="")
            query_parts.append(f"{quote(str(key), safe='')}={encoded_value}")
        
        logger.info(f"TikTok OAuth - Client Key: {client_key[:10]}...")
        logger.info(f"TikTok OAuth - Redirect URI: {redirect_uri}")
        logger.info(f"TikTok OAuth - Scopes: {self.get_scopes()}")
        
        return "https://www.tiktok.com/v2/auth/authorize?" + "&".join(query_parts)
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Échange le code OAuth contre un access token TikTok"""
        client_key = settings.TIKTOK_CLIENT_KEY.strip() if settings.TIKTOK_CLIENT_KEY else None
        client_secret = settings.TIKTOK_CLIENT_SECRET.strip() if settings.TIKTOK_CLIENT_SECRET else None
        redirect_uri = self.get_redirect_uri()
        
        if not client_key or not client_secret or not redirect_uri:
            raise HTTPException(status_code=500, detail="Configuration TikTok manquante")
        
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                "https://open.tiktokapis.com/v2/oauth/token/",
                data={
                    "client_key": client_key,
                    "client_secret": client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if r.status_code != 200:
                raise HTTPException(status_code=r.status_code, detail=f"Erreur TikTok OAuth: {r.text}")
            
            token_data = r.json()
            
            if token_data.get("error"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Erreur TikTok: {token_data.get('error_description', 'Unknown error')}"
                )
            
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            
            if not access_token:
                raise HTTPException(status_code=400, detail="Access token TikTok non obtenu")
            
            return {"access_token": access_token, "refresh_token": refresh_token, "client": client}
    
    async def get_user_info(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les informations utilisateur TikTok"""
        client = token_data.get("client")
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        
        if not client:
            raise HTTPException(status_code=500, detail="Client HTTP manquant")
        
        r = await client.get(
            "https://open.tiktokapis.com/v2/user/info/",
            params={"fields": "open_id,union_id,avatar_url,display_name"},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=f"Erreur récupération info TikTok: {r.text}")
        
        user_info = r.json()
        user_data = user_info.get("data", {}).get("user", {})
        
        tiktok_user_id = user_data.get("open_id") or user_data.get("union_id")
        display_name = user_data.get("display_name", "")
        avatar_url = user_data.get("avatar_url")
        
        if not tiktok_user_id:
            raise HTTPException(status_code=400, detail="Impossible de récupérer l'ID utilisateur TikTok")
        
        return {
            "provider_user_id": str(tiktok_user_id),
            "name": display_name or f"TikTok User {tiktok_user_id[:8]}",
            "email": None,  # TikTok ne fournit pas d'email
            "access_token": access_token,
            "refresh_token": refresh_token,
            "avatar_url": avatar_url  # Pour mise à jour du User.picture_url
        }

