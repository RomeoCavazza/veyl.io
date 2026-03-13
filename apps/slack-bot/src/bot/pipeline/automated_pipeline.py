"""
Pipeline Automatisé refactorisé
Utilise des modules spécialisés pour éviter le spaghetti code
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Importer les modules spécialisés
from .pipeline_config import PipelineConfig, PipelineResult
from .pipeline_executors import (
    VeilleExecutor,
    StyleGuideExecutor,
    PresentationExecutor,
    DeliveryExecutor
)
from .pipeline_orchestrator import (
    AutomatedPipeline,
    PipelineOrchestrator,
    test_automated_pipeline,
    test_pipeline_orchestrator
)

# Fonctions de compatibilité pour l'ancien code
def create_pipeline_config(**kwargs) -> PipelineConfig:
    """Crée une configuration de pipeline"""
    return PipelineConfig(**kwargs)

# Classes de compatibilité (simplifiées)
from .pipeline_config import PipelineConfig as RealPipelineConfig, PipelineResult as RealPipelineResult

class PipelineConfig(RealPipelineConfig):
    """Wrapper de compatibilité"""
    pass

class PipelineResult(RealPipelineResult):
    """Wrapper de compatibilité"""
    pass

# Instance globale pour compatibilité
_pipeline_orchestrator = None

def get_pipeline_orchestrator() -> PipelineOrchestrator:
    """Retourne l'orchestrateur de pipeline global"""
    global _pipeline_orchestrator
    if _pipeline_orchestrator is None:
        _pipeline_orchestrator = PipelineOrchestrator()
    return _pipeline_orchestrator
    """Configuration du pipeline"""
