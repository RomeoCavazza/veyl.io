# auth_unified/providers/base.py
"""Classe de base pour les providers OAuth"""
import os
import time
import logging
import hashlib
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import quote

from core.config import settings
from db.models import User, OAuthAccount
from auth_unified.auth_service import AuthService

logger = logging.getLogger(__name__)


class BaseOAuthProvider(ABC):
    """Classe de base abstraite pour tous les providers OAuth"""
    
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
        self.provider_name = self.get_provider_name()
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Retourne le nom du provider (ex: 'instagram', 'facebook')"""
        pass
    
    @abstractmethod
    def get_scopes(self) -> str:
        """Retourne les scopes OAuth demandés"""
        pass
    
    @abstractmethod
    def get_redirect_uri(self) -> str:
        """Retourne l'URI de redirection OAuth"""
        pass
    
    @abstractmethod
    def build_auth_url(self, state: str) -> str:
        """Construit l'URL d'autorisation OAuth"""
        pass
    
    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Échange le code OAuth contre un access token"""
        pass
    
    @abstractmethod
    async def get_user_info(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère les informations utilisateur depuis le provider
        
        Args:
            token_data: Dictionnaire contenant 'access_token' et potentiellement 'client' (httpx.AsyncClient)
        
        Returns:
            Dictionnaire avec 'provider_user_id', 'name', 'email' (optionnel), 'access_token'
        """
        pass
    
    # =====================================================
    # MÉTHODES COMMUNES (utilisables par tous les providers)
    # =====================================================
    
    def generate_state(self, user_id: Optional[UUID] = None) -> str:
        """Génère un state OAuth sécurisé"""
        timestamp = str(int(time.time()))
        if user_id:
            user_id_str = str(user_id)
            state_data = f"{timestamp}_{user_id_str}"
            state_hash = hashlib.sha256(f"{state_data}_{settings.OAUTH_STATE_SECRET}".encode()).hexdigest()[:8]
            return f"{timestamp}_{user_id_str}_{state_hash}"
        return timestamp
    
    def extract_user_id_from_state(self, state: str) -> Optional[UUID]:
        """Extrait l'user_id depuis le state OAuth si présent"""
        try:
            if '_' not in state:
                return None
            
            parts = state.split('_')
            if len(parts) >= 3:
                # Format standard avec hash
                timestamp, user_id_str, state_hash = parts[0], parts[1], parts[2]
                expected_hash = hashlib.sha256(f"{timestamp}_{user_id_str}_{settings.OAUTH_STATE_SECRET}".encode()).hexdigest()[:8]
                if state_hash == expected_hash:
                    return UUID(user_id_str)
            elif len(parts) == 2:
                # Format alternatif sans hash (utilisé par TikTok parfois)
                try:
                    return UUID(parts[1])
                except ValueError:
                    pass
        except (ValueError, IndexError, AttributeError):
            pass
        return None
    
    def get_frontend_url(self) -> str:
        """Détermine l'URL frontend selon l'environnement"""
        redirect_uri = self.get_redirect_uri()
        if os.getenv("ENVIRONMENT") == "production" or "veyl.io" in redirect_uri:
            return "https://veyl.io/auth/callback"
        return "http://localhost:8081/auth/callback"
    
    def create_or_update_oauth_account(
        self,
        db: Session,
        user: User,
        provider_user_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        scopes: Optional[list] = None
    ) -> None:
        """Crée ou met à jour un OAuthAccount pour un User"""
        existing_oauth = db.query(OAuthAccount).filter(
            OAuthAccount.user_id == user.id,
            OAuthAccount.provider == self.provider_name,
            OAuthAccount.provider_user_id == str(provider_user_id)
        ).first()
        
        if existing_oauth:
            existing_oauth.access_token = access_token
            if refresh_token:
                existing_oauth.refresh_token = refresh_token
            if scopes:
                existing_oauth.scopes = scopes
        else:
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider=self.provider_name,
                provider_user_id=str(provider_user_id),
                access_token=access_token,
                refresh_token=refresh_token,
                scopes=scopes
            )
            db.add(oauth_account)
        
        db.commit()
    
    def create_jwt_and_redirect(self, user: User) -> RedirectResponse:
        """Crée un JWT et redirige vers le frontend"""
        jwt_token = self.auth_service.create_access_token(data={"sub": str(user.id)})
        frontend_url = self.get_frontend_url()
        
        encoded_token = quote(jwt_token, safe='')
        encoded_email = quote(user.email or '', safe='')
        encoded_name = quote(user.name or '', safe='')
        
        redirect_url = f"{frontend_url}?token={encoded_token}&user_id={user.id}&email={encoded_email}&name={encoded_name}"
        return RedirectResponse(url=redirect_url)

