"""
Guide de style pour la direction artistique
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class StyleGuide:
    """Guide de style pour une marque"""

    brand_name: str
    primary_colors: List[str]
    secondary_colors: List[str]
    typography: Dict[str, str]
    visual_elements: List[str]
    tone_of_voice: str
    target_audience: str
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'brand_name': self.brand_name,
            'primary_colors': self.primary_colors,
            'secondary_colors': self.secondary_colors,
            'typography': self.typography,
            'visual_elements': self.visual_elements,
            'tone_of_voice': self.tone_of_voice,
            'target_audience': self.target_audience,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class ImagePrompt:
    """Prompt pour génération d'images"""

    description: str
    style: str
    mood: str
    colors: List[str]
    elements: List[str]
    platform: str
    dimensions: str
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_full_prompt(self) -> str:
        """Génère le prompt complet"""
        elements_str = ", ".join(self.elements)
        colors_str = ", ".join(self.colors)

        return f"{self.description}, {self.style} style, {self.mood} mood, " \
               f"colors: {colors_str}, elements: {elements_str}, " \
               f"for {self.platform}, {self.dimensions}"

@dataclass
class ColorPalette:
    """Palette de couleurs"""

    name: str
    primary: str
    secondary: str
    accent: str
    background: str
    text: str

    def to_dict(self) -> Dict[str, str]:
        """Convertit en dictionnaire"""
        return {
            'name': self.name,
            'primary': self.primary,
            'secondary': self.secondary,
            'accent': self.accent,
            'background': self.background,
            'text': self.text
        }

@dataclass
class VisualStyle:
    """Style visuel"""

    name: str
    description: str
    mood_board: List[str]
    reference_images: List[str]
    key_elements: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'name': self.name,
            'description': self.description,
            'mood_board': self.mood_board,
            'reference_images': self.reference_images,
            'key_elements': self.key_elements
        }
