# auth_unified/providers/instagram.py
"""Provider OAuth pour Instagram (via Facebook OAuth)"""
import logging
import httpx
from typing import Dict, Any, Optional
from urllib.parse import quote
from fastapi import HTTPException

from core.config import settings
from .base import BaseOAuthProvider

logger = logging.getLogger(__name__)


class InstagramOAuthProvider(BaseOAuthProvider):
    """Provider OAuth pour Instagram Business (via Facebook OAuth)"""
    
    def get_provider_name(self) -> str:
        return "instagram"
    
    def get_scopes(self) -> str:
        return "pages_show_list,pages_read_engagement,instagram_basic"
    
    def get_redirect_uri(self) -> str:
        return settings.IG_REDIRECT_URI.strip() if settings.IG_REDIRECT_URI else ""
    
    def build_auth_url(self, state: str) -> str:
        """Construit l'URL d'autorisation Instagram (via Facebook OAuth)"""
        app_id = settings.IG_APP_ID.strip() if settings.IG_APP_ID else None
        redirect_uri = self.get_redirect_uri()
        
        if not app_id:
            raise HTTPException(status_code=500, detail="IG_APP_ID vide ou non configuré")
        if not redirect_uri:
            raise HTTPException(status_code=500, detail="IG_REDIRECT_URI vide ou non configuré")
        
        # Valider le format de l'App ID Facebook
        if not app_id.isdigit() or not (15 <= len(app_id) <= 17):
            raise HTTPException(
                status_code=500,
                detail=f"IG_APP_ID invalide: doit être un nombre de 15-17 chiffres"
            )
        
        params = {
            "client_id": app_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": self.get_scopes(),
            "state": state,
        }
        
        query_parts = []
        for key, value in params.items():
            if key == "redirect_uri":
                encoded_value = quote(str(value), safe="/:")
            else:
                encoded_value = quote(str(value), safe="")
            query_parts.append(f"{quote(str(key), safe='')}={encoded_value}")
        
        return "https://www.facebook.com/v21.0/dialog/oauth?" + "&".join(query_parts)
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Échange le code OAuth contre un long-lived token Instagram"""
        app_id = settings.IG_APP_ID.strip() if settings.IG_APP_ID else None
        app_secret = settings.IG_APP_SECRET.strip() if settings.IG_APP_SECRET else None
        redirect_uri = self.get_redirect_uri()
        
        if not app_id or not app_secret or not redirect_uri:
            raise HTTPException(status_code=500, detail="Configuration Instagram manquante")
        
        async with httpx.AsyncClient(timeout=20) as client:
            # 1) Short-lived token
            try:
                r = await client.get(
                    "https://graph.facebook.com/v21.0/oauth/access_token",
                    params={
                        "client_id": app_id,
                        "client_secret": app_secret,
                        "redirect_uri": redirect_uri,
                        "code": code,
                    },
                )
                if r.status_code != 200:
                    error_detail = r.text
                    error_json = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
                    error_msg = error_json.get("error", {}).get("message", "unknown_error") if isinstance(error_json.get("error"), dict) else error_json.get("error", "unknown_error")
                    
                    if "redirect_uri" in error_detail.lower() or "Invalid redirect" in error_detail:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Erreur Instagram OAuth: Invalid redirect_uri. Vérifiez dans Facebook Developer Console."
                        )
                    raise HTTPException(
                        status_code=400,
                        detail=f"Erreur Instagram token: {r.status_code} - {error_msg}"
                    )
                
                short_token = r.json().get("access_token")
                if not short_token:
                    raise HTTPException(status_code=400, detail="Access token manquant dans la réponse")
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Erreur requête Instagram token: {str(e)}")
            
            # 2) Long-lived token
            try:
                r2 = await client.get(
                    "https://graph.facebook.com/v21.0/oauth/access_token",
                    params={
                        "grant_type": "fb_exchange_token",
                        "client_id": app_id,
                        "client_secret": app_secret,
                        "fb_exchange_token": short_token,
                    },
                )
                if r2.status_code != 200:
                    error_json = r2.json() if r2.headers.get("content-type", "").startswith("application/json") else {}
                    error_msg = error_json.get("error", {}).get("message", "unknown_error") if isinstance(error_json.get("error"), dict) else error_json.get("error", "unknown_error")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Erreur Instagram long-lived token: {r2.status_code} - {error_msg}"
                    )
                long_token = r2.json().get("access_token")
                if not long_token:
                    raise HTTPException(status_code=400, detail="Long-lived token manquant")
                return {"access_token": long_token}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Erreur requête Instagram long-lived token: {str(e)}")
    
    async def get_user_info(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère l'Instagram Business ID depuis les Pages Facebook"""
        long_token = token_data.get("access_token")
        
        if not long_token:
            raise HTTPException(status_code=400, detail="Access token manquant")
        
        # Créer un nouveau client (le précédent est fermé)
        async with httpx.AsyncClient(timeout=20) as client:
            # Récupérer Page(s) -> IG Business ID
            try:
                pages = await client.get(
                    "https://graph.facebook.com/v21.0/me/accounts",
                    params={"access_token": long_token}
                )
                if pages.status_code != 200:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Erreur récupération Pages Instagram: {pages.status_code}"
                    )
                
                pages_data = pages.json().get("data", [])
                ig_user_id = None
                
                for p in pages_data:
                    page_id = p["id"]
                    try:
                        r3 = await client.get(
                            f"https://graph.facebook.com/v21.0/{page_id}",
                            params={
                                "fields": "instagram_business_account{username,id}",
                                "access_token": long_token
                            },
                        )
                        if r3.status_code == 200:
                            ig = r3.json().get("instagram_business_account")
                            if ig and ig.get("id"):
                                ig_user_id = ig["id"]
                                logger.info(f"Instagram Business ID trouvé: {ig_user_id}")
                                break
                    except Exception as e:
                        logger.warning(f"Erreur récupération IG Business Account pour Page {page_id}: {str(e)}")
                        continue
                
                if not ig_user_id:
                    raise HTTPException(
                        status_code=400,
                        detail="Instagram Business Account non trouvé. Assurez-vous que votre compte Facebook a une Page liée à un compte Instagram Business."
                    )
                
                return {
                    "provider_user_id": str(ig_user_id),
                    "name": f"Instagram User {ig_user_id}",
                    "email": None,
                    "access_token": long_token
                }
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Erreur requête Pages Instagram: {str(e)}")

