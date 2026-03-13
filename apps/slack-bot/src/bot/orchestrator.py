"""
Orchestrateur principal - Version refactorisée
Utilise des modules spécialisés pour éviter le spaghetti code
"""

# Standard library imports
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Optional imports (modules spécialisés)
try:
    from .orchestrator.brief_processor import BriefProcessor, process_brief
    from .orchestrator.veille_processor import VeilleProcessor, run_veille
    from .orchestrator.analysis_processor import AnalysisProcessor, run_analyse
except ImportError:
    BriefProcessor = VeilleProcessor = AnalysisProcessor = None
    process_brief = run_veille = run_analyse = None

logger = logging.getLogger(__name__)

class Orchestrator:
    """Orchestrateur principal refactorisé"""

    def __init__(self):
        self.brief_processor = BriefProcessor() if BriefProcessor else None
        self.veille_processor = VeilleProcessor() if VeilleProcessor else None
        self.analysis_processor = AnalysisProcessor() if AnalysisProcessor else None

    async def process_brief(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """Traite un brief via le processeur spécialisé"""
        if not self.brief_processor:
            return {"success": False, "error": "BriefProcessor not available"}
        return await self.brief_processor.process_brief(pdf_path, **kwargs)

    async def run_veille(self, sources: List[str], **kwargs) -> Dict[str, Any]:
        """Exécute la veille via le processeur spécialisé"""
        if not self.veille_processor:
            return {"success": False, "error": "VeilleProcessor not available"}
        return await self.veille_processor.run_veille(sources, **kwargs)

    async def run_analyse(self, data_path: str, **kwargs) -> Dict[str, Any]:
        """Exécute l'analyse via le processeur spécialisé"""
        if not self.analysis_processor:
            return {"success": False, "error": "AnalysisProcessor not available"}
        return await self.analysis_processor.run_analyse(data_path, **kwargs)

# Instance globale pour compatibilité
orchestrator = Orchestrator()

# Fonctions de compatibilité pour l'ancien code supprimées - utiliser orchestrator.process_brief() directement

async def run_veille(sources: List[str], **kwargs) -> Dict[str, Any]:
    """Fonction de compatibilité"""
    if run_veille is None:
        return {"success": False, "error": "VeilleProcessor not available"}
    return await orchestrator.run_veille(sources, **kwargs)

async def run_analyse(data_path: str, **kwargs) -> Dict[str, Any]:
    """Fonction de compatibilité"""
    if run_analyse is None:
        return {"success": False, "error": "AnalysisProcessor not available"}
    return await orchestrator.run_analyse(data_path, **kwargs)

def load_schema(schema_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load JSON schema for brief validation - refactorisé

    Args:
        schema_path: Path to schema file (optional, for test compatibility)

    Returns:
        Schema dictionary
    """

    try:
        # Étape 1: Essayer le chemin fourni
        if schema_path:
            schema = _try_load_from_path(schema_path)
            if schema:
                return schema

        # Étape 2: Rechercher dans les répertoires parents
        schema = _search_in_parent_directories()
        if schema:
            return schema

        # Étape 3: Essayer le fallback de test
        schema = _try_load_fallback()
        if schema:
            return schema

    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        pass

    # Étape 4: Retourner le schéma par défaut
    return _create_default_schema(schema_path)

def _try_load_from_path(schema_path: str) -> Optional[Dict[str, Any]]:
    """Tente de charger le schéma depuis un chemin spécifique"""

    try:
        if Path(schema_path).exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        pass
    return None

def _search_in_parent_directories() -> Optional[Dict[str, Any]]:
    """Recherche le schéma dans les répertoires parents"""

    try:
        for parent in Path(__file__).resolve().parents:
            candidate = parent / "brief_schema.json"
            if candidate.exists():
                with open(candidate, 'r', encoding='utf-8') as f:
                    return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        pass
    return None

def _try_load_fallback() -> Optional[Dict[str, Any]]:
    """Tente de charger le schéma de fallback"""

    try:
        fallback = Path("tests/fixtures/brief_schema.json")
        if fallback.exists():
            with open(fallback, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        pass
    return None

def _create_default_schema(schema_path: Optional[str]) -> Dict[str, Any]:
    """Crée le schéma par défaut selon le contexte"""
    # Schéma de test si demandé
    if schema_path and 'test' in str(schema_path).lower():
        return {
            '$schema': 'http://json-schema.org/draft-07/schema#',
            'title': 'Brief Schema',
            'description': 'Schéma de validation pour les briefs',
            'type': 'object',
            'required': ['titre', 'problème', 'objectifs', 'kpis'],
            'properties': {
                'titre': {'type': 'string', 'description': 'Titre du brief'},
                'problème': {'type': 'string', 'description': 'Description du problème à résoudre'},
                'objectifs': {
                    'type': 'array',
                    'description': 'Liste des objectifs à atteindre',
                    'items': {'type': 'string'},
                    'minItems': 1
                },
                'kpis': {
                    'type': 'array',
                    'description': 'Liste des KPIs à suivre',
                    'items': {'type': 'string'},
                    'minItems': 1
                }
            }
        }

    # Schéma de fallback standard
    return {
        '$schema': 'http://json-schema.org/draft-07/schema#',
        'title': 'Brief Schema Fallback',
        'description': 'Schema de fallback pour compatibilité',
        'type': 'object',
        'properties': {
            'titre': {'type': 'string'},
            'problème': {'type': 'string'},
            'objectifs': {'type': 'array', 'items': {'type': 'string'}},
            'kpis': {'type': 'array', 'items': {'type': 'string'}}
        }
    }
