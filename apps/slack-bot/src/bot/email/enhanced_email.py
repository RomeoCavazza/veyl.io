#!/usr/bin/env python3
"""
Enhanced Email Module refactorisé
Utilise des modules spécialisés pour éviter le spaghetti code
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Importer les modules spécialisés
from .email_config import EmailConfig
from .email_templates import EmailTemplate
from .email_sender import EmailSender
from .newsletter_manager import NewsletterManager
from .email_orchestrator import EmailOrchestrator, send_newsletter, send_report, send_alert

# Fonctions de compatibilité pour l'ancien code
def create_email_templates():
    """Fonction de compatibilité - crée les templates par défaut"""
    template_manager = EmailTemplate()
    return "Templates created successfully"

# Classes de compatibilité
class NewsletterManager:
    """Wrapper de compatibilité pour NewsletterManager"""

    def __init__(self, config=None):
        if config is None:
            from .email_config import get_default_email_config
            config = get_default_email_config()
        self.manager = NewsletterManager(config)

    def create_newsletter(self, *args, **kwargs):
        return self.manager.create_newsletter(*args, **kwargs)

    def send_newsletter(self, *args, **kwargs):
        return self.manager.send_newsletter(*args, **kwargs)

# Instance globale pour compatibilité
_email_orchestrator = None

def get_email_orchestrator():
    """Retourne l'orchestrateur email global"""
    global _email_orchestrator
    if _email_orchestrator is None:
        _email_orchestrator = EmailOrchestrator()
    return _email_orchestrator
    """Email configuration"""
