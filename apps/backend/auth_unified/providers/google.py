# auth_unified/providers/google.py
"""Provider OAuth pour Google"""
import logging
import httpx
from typing import Dict, Any
from urllib.parse import quote
from fastapi import HTTPException

from core.config import settings
from .base import BaseOAuthProvider

logger = logging.getLogger(__name__)


class GoogleOAuthProvider(BaseOAuthProvider):
    """Provider OAuth pour Google"""
    
    def get_provider_name(self) -> str:
        return "google"
    
    def get_scopes(self) -> str:
        return "openid email profile"
    
    def get_redirect_uri(self) -> str:
        return settings.GOOGLE_REDIRECT_URI.strip() if settings.GOOGLE_REDIRECT_URI else ""
    
    def build_auth_url(self, state: str) -> str:
        """Construit l'URL d'autorisation Google"""
        client_id = settings.GOOGLE_CLIENT_ID.strip() if settings.GOOGLE_CLIENT_ID else None
        redirect_uri = self.get_redirect_uri()
        
        if not client_id:
            raise HTTPException(status_code=500, detail="GOOGLE_CLIENT_ID vide ou non configuré")
        if not redirect_uri:
            raise HTTPException(status_code=500, detail="GOOGLE_REDIRECT_URI vide ou non configuré")
        
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": self.get_scopes(),
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        
        # Construire l'URL manuellement avec quote (pas quote_plus) pour éviter les +
        query_parts = []
        for key, value in params.items():
            if key == "redirect_uri":
                encoded_value = quote(str(value), safe="/:")
            else:
                encoded_value = quote(str(value), safe="")
            query_parts.append(f"{quote(str(key), safe='')}={encoded_value}")
        
        return "https://accounts.google.com/o/oauth2/v2/auth?" + "&".join(query_parts)
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Échange le code OAuth contre un access token Google"""
        client_id = settings.GOOGLE_CLIENT_ID.strip() if settings.GOOGLE_CLIENT_ID else None
        client_secret = settings.GOOGLE_CLIENT_SECRET.strip() if settings.GOOGLE_CLIENT_SECRET else None
        redirect_uri = self.get_redirect_uri()
        
        if not client_id or not client_secret or not redirect_uri:
            raise HTTPException(status_code=500, detail="Configuration Google manquante")
        
        async with httpx.AsyncClient(timeout=20) as client:
            try:
                r = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "redirect_uri": redirect_uri,
                        "code": code,
                        "grant_type": "authorization_code"
                    }
                )
                if r.status_code != 200:
                    error_detail = r.text
                    error_json = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
                    error_msg = error_json.get("error", "unknown_error")
                    error_desc = error_json.get("error_description", error_detail)
                    
                    if error_msg == "invalid_client":
                        raise HTTPException(
                            status_code=400,
                            detail=f"Erreur Google OAuth: invalid_client - {error_desc}. "
                                   f"Vérifiez dans Google Cloud Console."
                        )
                    raise HTTPException(
                        status_code=400,
                        detail=f"Erreur Google token: {r.status_code} - {error_msg}: {error_desc}"
                    )
                
                token_data = r.json()
                access_token = token_data.get("access_token")
                if not access_token:
                    raise HTTPException(status_code=400, detail="Access token manquant")
                return {"access_token": access_token, "client": client}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Erreur requête Google token: {str(e)}")
    
    async def get_user_info(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les informations utilisateur Google"""
        client = token_data.get("client")
        access_token = token_data.get("access_token")
        
        if not client:
            raise HTTPException(status_code=500, detail="Client HTTP manquant")
        
        try:
            r = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if r.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Erreur récupération user info Google: {r.status_code}"
                )
            
            user_info = r.json()
            google_user_id = user_info.get("id")
            email = user_info.get("email")
            name = user_info.get("name")
            
            if not google_user_id:
                raise HTTPException(status_code=400, detail="Impossible de récupérer l'ID utilisateur Google")
            if not email:
                raise HTTPException(status_code=400, detail="Impossible de récupérer l'email Google")
            
            return {
                "provider_user_id": str(google_user_id),
                "name": name or email.split("@")[0],
                "email": email,
                "access_token": access_token
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erreur requête user info Google: {str(e)}")

