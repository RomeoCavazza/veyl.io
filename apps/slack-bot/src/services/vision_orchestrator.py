"""
Orchestrateur principal du service Vision
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from .vision_models import VisionAnalysis, VisionConfig, VisionBatchResult
from .google_vision_analyzer import GoogleVisionAnalyzer
from .social_vision_analyzer import SocialVisionAnalyzer

logger = logging.getLogger(__name__)

class VisionService:
    """Service Vision principal orchestrateur"""

    def __init__(self, config: Optional[VisionConfig] = None):
        self.config = config or VisionConfig()
        self.google_analyzer = GoogleVisionAnalyzer(self.config)
        self.social_analyzer = SocialVisionAnalyzer(self.config)

    def analyze_image(self, image_url: str) -> VisionAnalysis:
        """
        Analyse une image unique

        Args:
            image_url: URL ou chemin de l'image

        Returns:
            Résultat d'analyse complet
        """
        return self.google_analyzer.analyze_image(image_url)

    def analyze_batch(self, image_urls: List[str]) -> VisionBatchResult:
        """
        Analyse un lot d'images

        Args:
            image_urls: Liste des URLs d'images

        Returns:
            Résultat d'analyse par lot
        """
        logger.info(f"🔍 Analyzing batch of {len(image_urls)} images")

        start_time = datetime.now()
        analyses = []
        errors = []

        for i, image_url in enumerate(image_urls):
            try:
                analysis = self.analyze_image(image_url)
                analyses.append(analysis)

                if (i + 1) % 10 == 0:  # Log tous les 10
                    logger.info(f"📊 Processed {i + 1}/{len(image_urls)} images")

            except Exception as e:
                error_msg = f"Image {image_url}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)

        processing_time = (datetime.now() - start_time).total_seconds()

        result = VisionBatchResult(
            total_images=len(image_urls),
            successful_analyses=len(analyses),
            failed_analyses=len(errors),
            analyses=analyses,
            errors=errors,
            processing_time=processing_time
        )

        logger.info(f"✅ Batch analysis completed: {len(analyses)}/{len(image_urls)} successful in {processing_time:.2f}s")

        return result

    async def analyze_social_content(self, platform: str, content_data: List[Dict]) -> VisionBatchResult:
        """
        Analyse du contenu social

        Args:
            platform: Plateforme sociale ('tiktok', 'instagram', etc.)
            content_data: Données du contenu social

        Returns:
            Résultat d'analyse par lot
        """
        if platform.lower() == 'tiktok':
            # Utiliser l'analyseur TikTok spécialisé
            result = await self.social_analyzer.analyze_tiktok_images(content_data)
            # Convertir le format
            return self._convert_tiktok_result_to_batch(result)

        elif platform.lower() == 'instagram':
            # Utiliser l'analyseur Instagram
            return await self.social_analyzer.analyze_instagram_content(content_data)

        else:
            # Analyseur générique
            return await self.social_analyzer.analyze_social_media_batch(content_data, platform)

    async def analyze_tiktok_images(self, tiktok_data: List[Dict], brand_keywords: List[str] = None) -> Dict[str, List[VisionAnalysis]]:
        """
        Analyse spécialisée des images TikTok

        Args:
            tiktok_data: Données TikTok
            brand_keywords: Mots-clés de marque

        Returns:
            Analyse par vidéo
        """
        return await self.social_analyzer.analyze_tiktok_images(tiktok_data, brand_keywords)

    def generate_brand_insights(self, analyses: List[VisionAnalysis], brand_keywords: List[str]) -> Dict[str, Any]:
        """
        Génère des insights sur la marque

        Args:
            analyses: Liste des analyses
            brand_keywords: Mots-clés de marque

        Returns:
            Insights sur la marque
        """
        return self.social_analyzer.generate_brand_insights(analyses, brand_keywords)

    def health_check(self) -> Dict[str, Any]:
        """Vérifie la santé du service Vision"""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'config': {
                'api_key_configured': bool(self.config.api_key),
                'max_results': self.config.max_results,
                'language_hints': self.config.language_hints
            },
            'capabilities': {
                'google_vision': self.google_analyzer.client is not None,
                'batch_processing': True,
                'social_analysis': True
            }
        }

    def _convert_tiktok_result_to_batch(self, tiktok_result: Dict) -> VisionBatchResult:
        """Convertit le résultat TikTok en format batch standard"""
        all_analyses = []
        errors = []

        for video_analyses in tiktok_result['results'].values():
            all_analyses.extend(video_analyses)

        return VisionBatchResult(
            total_images=tiktok_result['total_videos_processed'],
            successful_analyses=tiktok_result['total_videos_processed'],
            failed_analyses=0,
            analyses=all_analyses,
            errors=errors,
            processing_time=0.0  # Non tracké dans le résultat TikTok
        )

# Fonctions de compatibilité pour l'ancien code
def analyze_tiktok_images(tiktok_data: List[Dict], brand_keywords: List[str] = None) -> Dict[str, List[VisionAnalysis]]:
    """Fonction de compatibilité pour l'analyse TikTok"""
    service = VisionService()
    # Note: Cette fonction devrait être async, mais gardons la compatibilité
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(service.analyze_tiktok_images(tiktok_data, brand_keywords))
        return result
    finally:
        loop.close()

# Instance globale pour compatibilité
_vision_service = None

def get_vision_service(config: Optional[VisionConfig] = None) -> VisionService:
    """Retourne l'instance globale du service Vision"""
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionService(config)
    return _vision_service
