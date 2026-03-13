"""
Analyseur de contenu social (TikTok, Instagram, etc.)
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .vision_models import VisionAnalysis, VisionBatchResult, VisionConfig
from .google_vision_analyzer import GoogleVisionAnalyzer

logger = logging.getLogger(__name__)

class SocialVisionAnalyzer:
    """Analyseur spécialisé pour le contenu social"""

    def __init__(self, config: VisionConfig):
        self.config = config
        self.vision_analyzer = GoogleVisionAnalyzer(config)

    async def analyze_tiktok_images(self, tiktok_data: List[Dict], brand_keywords: List[str] = None) -> Dict[str, List[VisionAnalysis]]:
        """
        Analyse les images TikTok pour détecter les mentions de marque

        Args:
            tiktok_data: Liste des données TikTok avec URLs d'images
            brand_keywords: Mots-clés de marque à rechercher

        Returns:
            Dictionnaire avec les analyses par vidéo
        """
        logger.info(f"🎵 Analyzing {len(tiktok_data)} TikTok images")

        if brand_keywords is None:
            brand_keywords = ['logo', 'brand', 'product']

        results = {}
        total_processed = 0
        total_brand_mentions = 0

        # Optimisation : utilisation de list comprehensions et dict comprehensions
        video_data = [
            (item.get('id', f"video_{i}"), item.get('image_urls', [])[:5])
            for i, item in enumerate(tiktok_data)
            if item.get('image_urls')
        ]

        for video_id, image_urls in video_data:
            try:
                # Analyse optimisée avec list comprehension
                video_analyses = [
                    self._analyze_single_image(image_url, brand_keywords)
                    for image_url in image_urls
                    if image_url
                ]

                # Filtrer les analyses réussies
                successful_analyses = [analysis for analysis in video_analyses if analysis is not None]

                if successful_analyses:
                    results[video_id] = successful_analyses
                    total_processed += 1
                    total_brand_mentions += sum(len(analysis.brand_mentions) for analysis in successful_analyses)

                    logger.info(f"✅ Video {video_id}: {len(successful_analyses)} images analyzed, {sum(len(analysis.brand_mentions) for analysis in successful_analyses)} brand mentions")

            except Exception as e:
                logger.error(f"Failed to analyze video {video_id}: {e}")

        summary = {
            'total_videos_processed': total_processed,
            'total_brand_mentions': total_brand_mentions,
            'results': results
        }

        logger.info(f"🎵 TikTok analysis completed: {total_brand_mentions} brand mentions across {total_processed} videos")

        return summary

    def _analyze_single_image(self, image_url: str, brand_keywords: list) -> Optional[Any]:
        """Analyse une seule image de manière optimisée"""
        try:
            analysis = self.vision_analyzer.analyze_image(image_url)

            # Vérifier les mentions de marque de manière optimisée
            brand_mentions = self._detect_brand_mentions(analysis, brand_keywords)
            if brand_mentions:
                analysis.brand_mentions.extend(brand_mentions)

            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze image {image_url}: {e}")
            return None

    async def analyze_instagram_content(self, instagram_data: List[Dict], brand_keywords: List[str] = None) -> VisionBatchResult:
        """
        Analyse le contenu Instagram

        Args:
            instagram_data: Liste des posts Instagram
            brand_keywords: Mots-clés de marque

        Returns:
            Résultat d'analyse par lot
        """
        logger.info(f"📸 Analyzing {len(instagram_data)} Instagram posts")

        if brand_keywords is None:
            brand_keywords = ['instagram', 'social', 'post']

        start_time = datetime.now()
        analyses = []
        errors = []

        for post in instagram_data:
            try:
                image_url = post.get('image_url') or post.get('media_url')
                if image_url:
                    analysis = self.vision_analyzer.analyze_image(image_url)

                    # Enrichir avec les métadonnées Instagram
                    analysis = self._enrich_instagram_analysis(analysis, post)

                    analyses.append(analysis)

            except Exception as e:
                errors.append(f"Post {post.get('id', 'unknown')}: {str(e)}")

        processing_time = (datetime.now() - start_time).total_seconds()

        result = VisionBatchResult(
            total_images=len(instagram_data),
            successful_analyses=len(analyses),
            failed_analyses=len(errors),
            analyses=analyses,
            errors=errors,
            processing_time=processing_time
        )

        logger.info(f"📸 Instagram analysis completed: {len(analyses)}/{len(instagram_data)} successful")

        return result

    async def analyze_social_media_batch(self, social_data: List[Dict], platform: str = 'generic') -> VisionBatchResult:
        """
        Analyse générique par lot pour les réseaux sociaux

        Args:
            social_data: Liste des données sociales
            platform: Plateforme sociale

        Returns:
            Résultat d'analyse par lot
        """
        logger.info(f"📱 Analyzing {len(social_data)} {platform} posts")

        start_time = datetime.now()
        analyses = []
        errors = []

        for item in social_data:
            try:
                # Détecter l'URL de l'image
                image_url = self._extract_image_url(item)

                if image_url:
                    analysis = self.vision_analyzer.analyze_image(image_url)

                    # Enrichir selon la plateforme
                    analysis = self._enrich_platform_analysis(analysis, item, platform)

                    analyses.append(analysis)
                else:
                    errors.append(f"No image URL found for item {item.get('id', 'unknown')}")

            except Exception as e:
                errors.append(f"Item {item.get('id', 'unknown')}: {str(e)}")

        processing_time = (datetime.now() - start_time).total_seconds()

        result = VisionBatchResult(
            total_images=len(social_data),
            successful_analyses=len(analyses),
            failed_analyses=len(errors),
            analyses=analyses,
            errors=errors,
            processing_time=processing_time
        )

        logger.info(f"📱 {platform} analysis completed: {len(analyses)}/{len(social_data)} successful")

        return result

    def _detect_brand_mentions(self, analysis: VisionAnalysis, brand_keywords: List[str]) -> List[str]:
        """Détecte les mentions de marque dans l'analyse"""
        mentions = []

        # Chercher dans le texte détecté
        for text in analysis.text_detected:
            text_lower = text.lower()
            for keyword in brand_keywords:
                if keyword.lower() in text_lower:
                    mentions.append(text)
                    break

        # Chercher dans les labels
        for label in analysis.labels:
            label_desc = label['description'].lower()
            for keyword in brand_keywords:
                if keyword.lower() in label_desc:
                    mentions.append(f"Label: {label['description']}")
                    break

        # Chercher dans les objets
        for obj in analysis.objects_detected:
            obj_name = obj['name'].lower()
            for keyword in brand_keywords:
                if keyword.lower() in obj_name:
                    mentions.append(f"Object: {obj['name']}")
                    break

        return list(set(mentions))  # Éliminer les doublons

    def _extract_image_url(self, item: Dict) -> Optional[str]:
        """Extrait l'URL de l'image des données sociales"""
        # Essayer différentes clés possibles
        possible_keys = ['image_url', 'media_url', 'url', 'thumbnail_url', 'photo_url']

        for key in possible_keys:
            url = item.get(key)
            if url and isinstance(url, str) and url.startswith(('http', 'https')):
                return url

        # Pour les vidéos, essayer de récupérer la miniature
        if item.get('type') == 'video':
            return item.get('thumbnail_url') or item.get('preview_url')

        return None

    def _enrich_instagram_analysis(self, analysis: VisionAnalysis, post: Dict) -> VisionAnalysis:
        """Enrichit l'analyse avec les métadonnées Instagram"""
        # Ajouter les hashtags comme texte détecté
        hashtags = post.get('hashtags', [])
        if hashtags:
            analysis.text_detected.extend([f"#{tag}" for tag in hashtags])

        # Ajouter les mentions
        mentions = post.get('mentions', [])
        if mentions:
            analysis.text_detected.extend([f"@{mention}" for mention in mentions])

        # Enrichir les métadonnées
        if not analysis.metadata:
            analysis.metadata = {}

        analysis.metadata.update({
            'platform': 'instagram',
            'likes': post.get('likes', 0),
            'comments': post.get('comments', 0),
            'engagement_rate': post.get('engagement_rate', 0),
            'post_type': post.get('type', 'image')
        })

        return analysis

    def _enrich_platform_analysis(self, analysis: VisionAnalysis, item: Dict, platform: str) -> VisionAnalysis:
        """Enrichit l'analyse avec les métadonnées de plateforme"""
        if not analysis.metadata:
            analysis.metadata = {}

        analysis.metadata.update({
            'platform': platform,
            'item_id': item.get('id'),
            'timestamp': item.get('timestamp'),
            'engagement': item.get('engagement', {}),
            'source_url': item.get('url')
        })

        return analysis

    def generate_brand_insights(self, analyses: List[VisionAnalysis], brand_keywords: List[str]) -> Dict[str, Any]:
        """
        Génère des insights sur la présence de marque

        Args:
            analyses: Liste des analyses vision
            brand_keywords: Mots-clés de marque

        Returns:
            Insights sur la marque
        """
        total_mentions = 0
        mention_sources = []
        sentiment_distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
        color_themes = []
        object_associations = []

        for analysis in analyses:
            # Compter les mentions
            brand_mentions = self._detect_brand_mentions(analysis, brand_keywords)
            total_mentions += len(brand_mentions)

            if brand_mentions:
                mention_sources.append({
                    'image_url': analysis.image_url,
                    'mentions': brand_mentions,
                    'sentiment': analysis.sentiment_visual
                })

            # Analyser le sentiment
            sentiment_distribution[analysis.sentiment_visual] += 1

            # Collecter les thèmes de couleur
            for color in analysis.colors_dominant[:3]:  # Top 3 couleurs
                color_themes.append(color)

            # Collecter les associations d'objets
            for obj in analysis.objects_detected[:3]:  # Top 3 objets
                object_associations.append(obj['name'])

        return {
            'total_brand_mentions': total_mentions,
            'mention_sources': mention_sources,
            'sentiment_distribution': sentiment_distribution,
            'dominant_colors': color_themes[:10],  # Top 10 couleurs
            'common_objects': list(set(object_associations))[:10],  # Top 10 objets uniques
            'brand_presence_score': min(total_mentions / len(analyses), 1.0) if analyses else 0,
            'generated_at': datetime.now().isoformat()
        }
