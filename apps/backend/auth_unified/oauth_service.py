# oauth/oauth_service.py
import logging
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException

from db.models import User
from .schemas import TokenResponse
from .auth_service import AuthService
from .providers import (
    BaseOAuthProvider,
    InstagramOAuthProvider,
    FacebookOAuthProvider,
    GoogleOAuthProvider,
    TikTokOAuthProvider
)

logger = logging.getLogger(__name__)


class OAuthService:
    """Service OAuth unifié utilisant des providers modulaires"""
    
    def __init__(self):
        self.auth_service = AuthService()
        # Initialiser les providers
        self.instagram_provider = InstagramOAuthProvider(self.auth_service)
        self.facebook_provider = FacebookOAuthProvider(self.auth_service)
        self.google_provider = GoogleOAuthProvider(self.auth_service)
        self.tiktok_provider = TikTokOAuthProvider(self.auth_service)
    
    def create_or_get_user(self, db: Session, email: str, name: str, role: str = "user") -> User:
        """Créer ou récupérer un utilisateur
        
        IMPORTANT: Cette fonction ne doit JAMAIS être appelée si un User existant a déjà été trouvé
        via linked_user_id ou email réel dans find_or_create_user_for_oauth.
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logger.info(f"Création d'un nouveau User: email={email}, name={name}")
            user = User(email=email, name=name, role=role)
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            logger.info(f"User existant trouvé: email={email}, user_id={user.id}")
        return user
    
    def find_or_create_user_for_oauth(
        self,
        db: Session,
        provider: str,
        provider_user_id: str,
        email: str = None,
        name: str = None,
        linked_user_id: Optional[UUID] = None
    ) -> User:
        """
        Fonction centralisée pour trouver ou créer un User lors d'une connexion OAuth.
        
        PRIORITÉ 1: Si linked_user_id est fourni, utiliser ce User
        PRIORITÉ 2: Chercher si un OAuthAccount du même provider existe déjà
        PRIORITÉ 3: Si email réel fourni, chercher un User existant avec cet email
        PRIORITÉ 4: Chercher via d'autres OAuthAccounts existants (cross-linking)
        PRIORITÉ 5: Créer un nouveau User uniquement en dernier recours
        
        Retourne: User existant ou nouvellement créé
        """
        from db.models import OAuthAccount
        
        # PRIORITÉ 1: User lié explicitement
        if linked_user_id:
            user = db.query(User).filter(User.id == linked_user_id).first()
            if user:
                logger.info(f"Liaison OAuth {provider} au User ID: {linked_user_id}")
                return user
            logger.warning(f"User ID {linked_user_id} non trouvé, poursuite de la recherche...")
        
        # PRIORITÉ 2: Chercher si un OAuthAccount du même provider existe déjà
        existing_oauth = db.query(OAuthAccount).filter(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == str(provider_user_id)
        ).first()
        
        if existing_oauth:
            user = db.query(User).filter(User.id == existing_oauth.user_id).first()
            if user:
                logger.info(f"OAuthAccount {provider} existe déjà pour User ID: {user.id}")
                return user
        
        # PRIORITÉ 3: Si email réel fourni, chercher un User existant avec cet email
        if email:
            is_real_email = (
                not email.startswith(('instagram_', 'facebook_', 'tiktok_', 'google_')) and
                not email.endswith(('@veyl.io', '@insidr.dev')) and
                '@' in email
            )
            if is_real_email:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    logger.info(f"User trouvé via email réel: {email} (User ID: {user.id})")
                    return user
        
        # PRIORITÉ 4: Chercher via d'autres OAuthAccounts existants (cross-linking)
        # Si un autre provider a déjà un OAuthAccount avec le même email ou user_id, lier
        if email and '@' in email:
            other_oauth = db.query(OAuthAccount).join(User).filter(User.email == email).first()
            if other_oauth:
                user = db.query(User).filter(User.id == other_oauth.user_id).first()
                if user:
                    logger.info(f"User trouvé via cross-linking OAuth: {email} (User ID: {user.id})")
                    return user
        
        # PRIORITÉ 5: Créer un nouveau User uniquement en dernier recours
        if not email:
            email = f"{provider}_{provider_user_id}@veyl.io"
        if not name:
            name = f"{provider.title()} User {provider_user_id[:8]}"
        
        logger.warning(
            f"Création d'un nouveau User pour OAuth {provider} "
            f"(provider_user_id={provider_user_id}, linked_user_id={linked_user_id})"
        )
        user = self.create_or_get_user(db, email=email, name=name)
        logger.info(f"Nouveau User créé: user_id={user.id}, email={user.email}, name={user.name}")
        return user
    
    # =====================================================
    # MÉTHODES START AUTH (génération URL d'autorisation)
    # =====================================================
    
    def start_instagram_auth(self, user_id: Optional[UUID] = None) -> Dict[str, str]:
        """Démarrer le processus OAuth Instagram"""
        logger.info(f"Démarrage OAuth Instagram (user_id: {user_id})")
        state = self.instagram_provider.generate_state(user_id)
        auth_url = self.instagram_provider.build_auth_url(state)
        logger.info(f"URL OAuth Instagram générée: {auth_url[:100]}...")
        return {"auth_url": auth_url, "state": state}
    
    def start_facebook_auth(self, user_id: Optional[UUID] = None) -> Dict[str, str]:
        """Démarrer le processus OAuth Facebook"""
        logger.info(f"Démarrage OAuth Facebook (user_id: {user_id})")
        state = self.facebook_provider.generate_state(user_id)
        auth_url = self.facebook_provider.build_auth_url(state)
        return {"auth_url": auth_url, "state": state}
    
    def start_google_auth(self) -> Dict[str, str]:
        """Démarrer le processus OAuth Google"""
        logger.info("Démarrage OAuth Google")
        state = self.google_provider.generate_state()
        auth_url = self.google_provider.build_auth_url(state)
        return {"auth_url": auth_url, "state": state}
    
    def start_tiktok_auth(self, user_id: Optional[UUID] = None) -> Dict[str, str]:
        """Démarrer le processus OAuth TikTok"""
        logger.info(f"Démarrage OAuth TikTok (user_id: {user_id})")
        state = self.tiktok_provider.generate_state(user_id)
        auth_url = self.tiktok_provider.build_auth_url(state)
        logger.info(f"TikTok OAuth URL générée: {auth_url[:150]}...")
        return {"auth_url": auth_url, "state": state}
    
    # =====================================================
    # MÉTHODES HANDLE CALLBACK (traitement du callback OAuth)
    # =====================================================
    
    async def _handle_oauth_callback(
        self,
        provider: BaseOAuthProvider,
        code: str,
        state: str,
        db: Session
    ) -> TokenResponse:
        """Méthode générique pour gérer un callback OAuth"""
        # Extraire linked_user_id depuis le state
        linked_user_id = provider.extract_user_id_from_state(state)
        if linked_user_id:
            logger.info(f"Liaison {provider.provider_name} OAuth au User ID: {linked_user_id}")
        
        logger.info(f"Callback {provider.provider_name} reçu - Code: {code[:20]}..., State: {state}")
        
        # 1. Échanger le code contre un token
        token_data = await provider.exchange_code_for_token(code)
        
        # 2. Récupérer les infos utilisateur
        user_info = await provider.get_user_info(token_data)
        
        provider_user_id = user_info.get("provider_user_id")
        name = user_info.get("name")
        email = user_info.get("email")
        access_token = user_info.get("access_token")
        refresh_token = user_info.get("refresh_token")
        avatar_url = user_info.get("avatar_url")
        
        if not provider_user_id or not access_token:
            raise HTTPException(status_code=400, detail=f"Données {provider.provider_name} incomplètes")
        
        # 3. Trouver ou créer le User
        logger.info(f"Recherche/création User pour {provider.provider_name} - linked_user_id={linked_user_id}, provider_user_id={provider_user_id}")
        
        user = self.find_or_create_user_for_oauth(
            db=db,
            provider=provider.provider_name,
            provider_user_id=provider_user_id,
            email=email,
            name=name,
            linked_user_id=linked_user_id
        )
        
        logger.info(f"User trouvé/créé pour {provider.provider_name}: user_id={user.id}, email={user.email}, name={user.name}")
        
        # 4. Mettre à jour l'avatar si disponible (TikTok)
        if avatar_url:
            user.picture_url = avatar_url
            db.commit()
        
        # 5. Créer ou mettre à jour l'OAuthAccount
        provider.create_or_update_oauth_account(
            db=db,
            user=user,
            provider_user_id=provider_user_id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        # 6. Créer JWT et rediriger
        return provider.create_jwt_and_redirect(user)
    
    async def handle_instagram_callback(self, code: str, state: str, db: Session) -> TokenResponse:
        """Gérer le callback OAuth Instagram"""
        return await self._handle_oauth_callback(self.instagram_provider, code, state, db)
    
    async def handle_facebook_callback(self, code: str, state: str, db: Session) -> TokenResponse:
        """Gérer le callback OAuth Facebook"""
        return await self._handle_oauth_callback(self.facebook_provider, code, state, db)
    
    async def handle_google_callback(self, code: str, state: str, db: Session) -> TokenResponse:
        """Gérer le callback OAuth Google"""
        return await self._handle_oauth_callback(self.google_provider, code, state, db)
    
    async def handle_tiktok_callback(self, code: str, state: str, db: Session) -> TokenResponse:
        """Gérer le callback OAuth TikTok"""
        return await self._handle_oauth_callback(self.tiktok_provider, code, state, db)
