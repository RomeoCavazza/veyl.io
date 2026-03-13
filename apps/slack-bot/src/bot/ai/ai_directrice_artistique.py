"""
AI Directrice Artistique - Version Refactorisée
Utilise des modules spécialisés pour éviter le spaghetti code
"""

import json
import openai
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os

from .style_guide import StyleGuide, ImagePrompt, ColorPalette, VisualStyle
from .image_apis import ImageGenerator

logger = logging.getLogger(__name__)

@dataclass
class StyleGuide:
    """Guide de style généré par l'AI"""
    brand_name: str
    sector: str
    mood: str
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str
    heading_font: str
    subheading_font: str
    body_font: str
    visual_style: str
    imagery_style: str
    color_palette: List[str]
    typography_hierarchy: Dict[str, str]
    design_principles: List[str]
    inspiration_sources: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "brand_name": self.brand_name,
            "sector": self.sector,
            "mood": self.mood,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "accent_color": self.accent_color,
            "background_color": self.background_color,
            "heading_font": self.heading_font,
            "subheading_font": self.subheading_font,
            "body_font": self.body_font,
            "visual_style": self.visual_style,
            "imagery_style": self.imagery_style,
            "color_palette": self.color_palette,
            "typography_hierarchy": self.typography_hierarchy,
            "design_principles": self.design_principles,
            "inspiration_sources": self.inspiration_sources
        }

@dataclass
class ImagePrompt:
    """Prompt pour génération d'image"""
    description: str
    style: str
    mood: str
    colors: List[str]
    composition: str
    target_use: str
    api_specific_prompt: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "description": self.description,
            "style": self.style,
            "mood": self.mood,
            "colors": self.colors,
            "composition": self.composition,
            "target_use": self.target_use,
            "api_specific_prompt": self.api_specific_prompt
        }

@dataclass
class ColorPalette:
    """Palette de couleurs générée par l'AI"""
    primary: str
    secondary: str
    accent: str
    background: str
    text: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convertit en dictionnaire"""
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "background": self.background,
            "text": self.text
        }

@dataclass
class VisualStyle:
    """Style visuel généré par l'AI"""
    typography: str
    layout: str
    spacing: str
    imagery: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convertit en dictionnaire"""
        return {
            "typography": self.typography,
            "layout": self.layout,
            "spacing": self.spacing,
            "imagery": self.imagery
        }

class AIDirectriceArtistique:
    """AI Directrice Artistique principale"""
    
    def __init__(self, openai_api_key: str = None, preferred_image_api: str = "dalle"):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key

        # Générateur d'images unifié
        self.image_generator = ImageGenerator(preferred_api=preferred_image_api)
        
    def generate_style_guide(self, brief_data: Dict, veille_data: Dict) -> StyleGuide:
        """Génère un guide de style basé sur le brief et la veille"""
        logger.info(f"🎨 Generating style guide for {brief_data.get('brand_name', 'Unknown')}")

        try:
            # Utilisation du service AI unifié
            from src.services.ai_service import get_ai_service
            ai_service = get_ai_service()

            # Prompt pour génération du style guide
            prompt = self._build_style_guide_prompt(brief_data, veille_data)

            # Génération avec AI
            response = ai_service.call_ai({
                'content': prompt,
                'analysis_type': 'style_guide',
                'context': {'brief': brief_data, 'veille': veille_data}
            })

            if response.success:
                style_data = response.result
                style_guide = StyleGuide(
                    brand_name=brief_data.get('brand_name', 'Unknown'),
                    primary_colors=style_data.get('primary_colors', ['#2C3E50']),
                    secondary_colors=style_data.get('secondary_colors', ['#34495E']),
                    typography=style_data.get('typography', {}),
                    visual_elements=style_data.get('visual_elements', []),
                    tone_of_voice=style_data.get('tone_of_voice', 'Professional'),
                    target_audience=style_data.get('target_audience', 'General')
                )

                logger.info("✅ Style guide generated successfully")
                return style_guide
            else:
                logger.error(f"❌ Failed to generate style guide: {response.error_message}")
                return self._create_fallback_style_guide(brief_data)

        except Exception as e:
            logger.error(f"❌ Error generating style guide: {e}")
            return self._create_fallback_style_guide(brief_data)

    def generate_image_prompt(self, description: str, platform: str = "instagram") -> ImagePrompt:
        """Génère un prompt d'image optimisé"""
        logger.info(f"📸 Generating image prompt for {platform}")

        try:
            # Utilisation du service AI unifié
            from src.services.ai_service import get_ai_service
            ai_service = get_ai_service()

            prompt = f"Create an optimized image prompt for {platform} about: {description}"

            response = ai_service.call_ai({
                'content': prompt,
                'analysis_type': 'image_prompt',
                'context': {'platform': platform, 'description': description}
            })

            if response.success:
                prompt_data = response.result
                image_prompt = ImagePrompt(
                    description=description,
                    style=prompt_data.get('style', 'modern'),
                    mood=prompt_data.get('mood', 'professional'),
                    colors=prompt_data.get('colors', ['#2C3E50']),
                    elements=prompt_data.get('elements', []),
                    platform=platform,
                    dimensions=prompt_data.get('dimensions', '1080x1080')
                )

                return image_prompt
            else:
                return self._create_fallback_image_prompt(description, platform)

        except Exception as e:
            logger.error(f"❌ Error generating image prompt: {e}")
            return self._create_fallback_image_prompt(description, platform)

    def generate_images(self, prompts: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Génère des images à partir de prompts"""
        logger.info(f"🎨 Generating {len(prompts)} images")

        return self.image_generator.generate_multiple_images(prompts, **kwargs)

    def _build_style_guide_prompt(self, brief_data: Dict, veille_data: Dict) -> str:
        """Construit le prompt pour génération du style guide"""
        return f"""
        Create a comprehensive style guide for {brief_data.get('brand_name', 'the brand')} in the {brief_data.get('sector', 'industry')} sector.

        Brief Information:
        - Target Audience: {brief_data.get('target_audience', 'General audience')}
        - Brand Values: {', '.join(brief_data.get('core_values', []))}
        - Positioning: {brief_data.get('positioning', 'Premium positioning')}

        Veille Insights:
        - Trends: {', '.join(veille_data.get('trends', [])[:5])}
        - Competitors: {', '.join([c.get('name', '') for c in veille_data.get('competitors', [])[:3]])}
        - Sentiment: {veille_data.get('sentiment', {}).get('overall', 'neutral')}

        Generate a complete style guide with colors, typography, visual elements, and design principles.
        """

    def _create_fallback_style_guide(self, brief_data: Dict) -> StyleGuide:
        """Crée un guide de style de secours"""
        return StyleGuide(
            brand_name=brief_data.get('brand_name', 'Unknown'),
            primary_colors=['#2C3E50', '#3498DB'],
            secondary_colors=['#34495E', '#E74C3C'],
            typography={'heading': 'Montserrat', 'body': 'Open Sans'},
            visual_elements=['clean', 'modern', 'professional'],
            tone_of_voice='Professional and approachable',
            target_audience=brief_data.get('target_audience', 'General audience')
        )

    def _create_fallback_image_prompt(self, description: str, platform: str) -> ImagePrompt:
        """Crée un prompt d'image de secours"""
        return ImagePrompt(
            description=description,
            style='modern',
            mood='professional',
            colors=['#2C3E50', '#3498DB'],
            elements=['clean', 'minimalist'],
            platform=platform,
            dimensions='1080x1080'
        )
