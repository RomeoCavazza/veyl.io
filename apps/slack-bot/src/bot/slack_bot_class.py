"""
Classe SlackBot pour intégration Slack
Production-ready avec gestion d'erreurs
"""

import os
import logging
from typing import Dict, List, Any, Optional

try:
    from slack_bolt import App
    from slack_bolt.adapter.fastapi import SlackRequestHandler
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False

logger = logging.getLogger(__name__)

class SlackBot:
    """Bot Slack pour Revolver AI"""
    
    def __init__(self, bot_token: Optional[str] = None, signing_secret: Optional[str] = None):
        self.bot_token = bot_token or os.getenv('SLACK_BOT_TOKEN')
        self.signing_secret = signing_secret or os.getenv('SLACK_SIGNING_SECRET')
        self.app = None
        self.handler = None
        
        if SLACK_AVAILABLE and self.bot_token and self.signing_secret:
            try:
                self._init_slack_app()
                logger.info("✅ Slack Bot initialisé")
            except Exception as e:
                logger.warning(f"🟡 Slack Bot non disponible: {e}")
        else:
            logger.info("🟡 Slack Bot en mode fallback (credentials manquantes)")
    
    def _init_slack_app(self):
        """Initialiser l'app Slack"""
        self.app = App(
            token=self.bot_token,
            signing_secret=self.signing_secret
        )
        
        # Handler pour FastAPI
        self.handler = SlackRequestHandler(self.app)
        
        # Commandes enregistrées automatiquement via le handler
    
    # Méthode _register_commands supprimée - code mort

    def is_available(self) -> bool:
        """Vérifier si Slack est disponible"""
        return self.app is not None

# Instance globale
slack_bot = SlackBot()
