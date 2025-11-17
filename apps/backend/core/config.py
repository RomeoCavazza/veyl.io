# core/config.py
# Configuration centralisée pour l'API

import os
from typing import Optional
from dotenv import load_dotenv  # type: ignore

# Charger les variables d'environnement depuis .env
load_dotenv()

class Settings:
    """Configuration centralisée de l'application"""
    
    def __init__(self):
        
        # Base de données - OBLIGATOIRE
        self.DATABASE_URL: str = os.getenv("DATABASE_URL")
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set in environment variables")
        
        # Clé secrète JWT - OBLIGATOIRE
        self.SECRET_KEY: str = os.getenv("SECRET_KEY")
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in environment variables")
        
        # Configuration JWT
        self.ALGORITHM: str = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 jours
        
        # Configuration Instagram Business API - OBLIGATOIRE
        self.IG_ACCESS_TOKEN: Optional[str] = os.getenv("IG_ACCESS_TOKEN")
        self.META_LONG_TOKEN: Optional[str] = os.getenv("META_LONG_TOKEN")
        self.IG_USER_ID: Optional[str] = os.getenv("IG_USER_ID")
        self.IG_APP_ID: Optional[str] = os.getenv("IG_APP_ID")
        self.IG_APP_SECRET: Optional[str] = os.getenv("IG_APP_SECRET")
        self.IG_REDIRECT_URI: str = os.getenv("IG_REDIRECT_URI", "https://api.veyl.io/api/v1/auth/instagram/callback")
        
        # Configuration Facebook API - OBLIGATOIRE
        self.FB_APP_ID: Optional[str] = os.getenv("FB_APP_ID")
        self.FB_APP_SECRET: Optional[str] = os.getenv("FB_APP_SECRET")
        self.FB_REDIRECT_URI: str = os.getenv("FB_REDIRECT_URI", "https://api.veyl.io/api/v1/auth/facebook/callback")
        
        # Configuration OAuth - OBLIGATOIRE
        self.OAUTH_STATE_SECRET: str = os.getenv("OAUTH_STATE_SECRET")
        if not self.OAUTH_STATE_SECRET:
            raise ValueError("OAUTH_STATE_SECRET must be set in environment variables")
        
        # Configuration Webhook - OBLIGATOIRE
        self.WEBHOOK_VERIFY_TOKEN: str = os.getenv("WEBHOOK_VERIFY_TOKEN")
        if not self.WEBHOOK_VERIFY_TOKEN:
            raise ValueError("WEBHOOK_VERIFY_TOKEN must be set in environment variables")
        
        # Configuration Google OAuth - OBLIGATOIRE
        self.GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
        self.GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
        
        # Configuration redirect URI - priorité à PROD si défini, sinon détection auto
        self.GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI_PROD") or os.getenv("GOOGLE_REDIRECT_URI") or "https://veyl.io/api/v1/auth/google/callback"
        
        # Configuration TikTok API - OBLIGATOIRE pour récupérer des données
        self.TIKTOK_CLIENT_KEY: Optional[str] = os.getenv("TIKTOK_CLIENT_KEY")
        self.TIKTOK_CLIENT_SECRET: Optional[str] = os.getenv("TIKTOK_CLIENT_SECRET")
        self.TIKTOK_REDIRECT_URI: str = os.getenv("TIKTOK_REDIRECT_URI", "https://veyl.io/api/v1/auth/tiktok/callback")

# Instance globale
settings = Settings()