"""
Templates package for slides generation
"""

import os

from .canonical_templates import (
    TemplateFactory, StyleDetector, ContentAdapter, IdeaGenerator,
    SlideStyle, SlideType, CoverTemplate, StrategicPrioritiesTemplate,
    SommaireTemplate, BrandOverviewTemplate, StateOfPlayTemplate,
    IdeaTemplate, TimelineTemplate, BudgetTemplate, CANONICAL_TEMPLATES
)

# Fonction utilitaire pour obtenir le chemin des templates
def get_template_path(template_name: str) -> str:
    """Retourne le chemin vers un template"""
    template_dir = os.path.dirname(__file__)
    return os.path.join(template_dir, f"{template_name}.json")

def get_default_template() -> dict:
    """Retourne le template par défaut (cover)"""
    return CANONICAL_TEMPLATES.get('cover', {})

def get_available_templates() -> list:
    """Retourne la liste des templates disponibles"""
    return list(CANONICAL_TEMPLATES.keys())

def get_template_metadata(template_name: str) -> dict:
    """Retourne les métadonnées d'un template"""
    template_data = CANONICAL_TEMPLATES.get(template_name, {})
    return {
        "name": template_name,
        "description": f"Canonical template: {template_name}",
        "author": "REVOLVR AI",
        "version": "2.0",
        "type": "canonical",
        "data": template_data
    }

def apply_theme(presentation, theme_name: str) -> None:
    """Applique un thème à une présentation (placeholder)"""
    pass

def get_layout(presentation, layout_name: str):
    """Récupère un layout de slide (placeholder)"""
    return None

__all__ = [
    'TemplateFactory',
    'StyleDetector', 
    'ContentAdapter',
    'IdeaGenerator',
    'SlideStyle',
    'SlideType',
    'CoverTemplate',
    'StrategicPrioritiesTemplate',
    'SommaireTemplate',
    'BrandOverviewTemplate',
    'StateOfPlayTemplate',
    'IdeaTemplate',
    'TimelineTemplate',
    'BudgetTemplate',
    'CANONICAL_TEMPLATES',
    'get_template_path',
    'get_default_template',
    'get_available_templates',
    'get_template_metadata',
    'apply_theme',
    'get_layout'
]
