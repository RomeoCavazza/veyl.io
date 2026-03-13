"""
Service Vision refactorisé
Utilise des modules spécialisés pour éviter le spaghetti code
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Importer les modules spécialisés
from .vision_models import VisionAnalysis, VisionConfig, VisionBatchResult
from .google_vision_analyzer import GoogleVisionAnalyzer, GOOGLE_VISION_AVAILABLE
from .social_vision_analyzer import SocialVisionAnalyzer
from .vision_orchestrator import VisionService, analyze_tiktok_images, get_vision_service

# Fonctions de compatibilité pour l'ancien code
def get_vision_analyzer(api_key: Optional[str] = None) -> GoogleVisionAnalyzer:
    """Retourne un analyseur Google Vision"""
    config = VisionConfig(api_key=api_key)
    return GoogleVisionAnalyzer(config)

# Classes de compatibilité
class VisionAnalyzer:
    """Wrapper de compatibilité pour GoogleVisionAnalyzer"""

    def __init__(self, api_key: Optional[str] = None):
        self.analyzer = get_vision_analyzer(api_key)

    def analyze_image(self, image_url: str) -> VisionAnalysis:
        """Analyse une image"""
        return self.analyzer.analyze_image(image_url)

# Instance globale pour compatibilité
_vision_analyzer = None

def get_global_vision_analyzer(api_key: Optional[str] = None) -> GoogleVisionAnalyzer:
    """Retourne l'analyseur vision global"""
    global _vision_analyzer
    if _vision_analyzer is None or (api_key and _vision_analyzer.config.api_key != api_key):
        _vision_analyzer = get_vision_analyzer(api_key)
    return _vision_analyzer
