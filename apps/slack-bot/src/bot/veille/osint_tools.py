"""
Outils OSINT refactorisés
Utilise des modules spécialisés pour éviter le spaghetti code
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Importer les modules spécialisés
from .osint_models import OSINTResult
from .maltego_integration import MaltegoIntegration
from .public_records_search import PublicRecordsSearch
from .social_media_osint import SocialMediaOSINT
from .osint_engine import OSINTEngine, run_osint_search

# Fonctions de compatibilité pour l'ancien code
def get_osint_engine() -> OSINTEngine:
    """Retourne une instance du moteur OSINT"""
    return OSINTEngine()

# Classes de compatibilité
class OSINTAnalysis:
    """Wrapper de compatibilité pour OSINTEngine"""

    def __init__(self):
        self.engine = OSINTEngine()

    def analyze_target(self, target: str, target_type: str = 'company') -> Dict:
        """Analyse une cible OSINT"""
        report = self.engine.search_target(target, target_type)
        return {
            'results': [r.__dict__ for r in report.results],
            'summary': report.summary,
            'target': report.target.__dict__
        }

    def get_health_status(self) -> Dict:
        """Retourne le statut de santé"""
        return self.engine.health_check()

# Instance globale pour compatibilité
_osint_engine = None

def get_global_osint_engine() -> OSINTEngine:
    """Retourne l'instance globale du moteur OSINT"""
    global _osint_engine
    if _osint_engine is None:
        _osint_engine = OSINTEngine()
    return _osint_engine

