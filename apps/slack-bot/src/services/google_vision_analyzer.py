"""
Analyseur Google Vision spécialisé
"""

import os
import base64
import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import io

try:
    from google.cloud import vision
    from google.cloud.vision_v1 import types
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False

from .vision_models import VisionAnalysis, VisionConfig

logger = logging.getLogger(__name__)

class GoogleVisionAnalyzer:
    """Analyseur spécialisé utilisant Google Vision API"""

    def __init__(self, config: VisionConfig):
        self.config = config
        self.client = None

        if GOOGLE_VISION_AVAILABLE and config.api_key:
            try:
                # Configuration pour l'API key
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config.api_key
                self.client = vision.ImageAnnotatorClient()
                logger.info("✅ Google Vision API client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Vision: {e}")
                self.client = None
        else:
            logger.warning("⚠️ Google Vision API not available, using fallback mode")

    def analyze_image(self, image_url: str) -> VisionAnalysis:
        """
        Analyse une image avec Google Vision - refactorisé pour réduire la complexité

        Args:
            image_url: URL ou chemin de l'image

        Returns:
            Résultat d'analyse complet
        """
        logger.info(f"🔍 Analyzing image: {image_url}")
        start_time = datetime.now()

        try:
            # Étape 1: Analyse de base (Google Vision ou fallback)
            analysis_data = _perform_vision_analysis(self, image_url)

            # Étape 2: Analyse spécialisée
            specialized_data = _perform_specialized_analysis(self, analysis_data)

            # Étape 3: Construction du résultat
            return _build_vision_analysis_result(image_url, analysis_data, specialized_data, start_time)

        except Exception as e:
            return _handle_vision_analysis_error(self, image_url, e, start_time)

def _perform_vision_analysis(analyzer, image_url: str) -> Dict[str, Any]:
    """Effectue l'analyse de vision de base"""
    if analyzer.client:
        return _perform_google_vision_analysis(analyzer, image_url)
    else:
        return _perform_fallback_vision_analysis(analyzer)

def _perform_google_vision_analysis(analyzer, image_url: str) -> Dict[str, Any]:
    """Effectue l'analyse avec Google Vision API"""
    image = analyzer._load_image(image_url)

    return {
        'labels': analyzer._detect_labels(image, analyzer.client),
        'text': analyzer._detect_text(image, analyzer.client),
        'objects': analyzer._detect_objects(image, analyzer.client),
        'faces': analyzer._detect_faces(image, analyzer.client),
        'colors': analyzer._detect_colors(image, analyzer.client),
        'safe_search': analyzer._detect_safe_search(image, analyzer.client)
    }

def _perform_fallback_vision_analysis(analyzer) -> Dict[str, Any]:
    """Effectue l'analyse en mode fallback"""
    labels, text, objects, faces, colors, safe_search = analyzer._fallback_analysis()
    return {
        'labels': labels,
        'text': text,
        'objects': objects,
        'faces': faces,
        'colors': colors,
        'safe_search': safe_search
    }

def _perform_specialized_analysis(analyzer, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Effectue l'analyse spécialisée"""
    return {
        'brand_mentions': analyzer._analyze_brand_mentions(analysis_data['text']),
        'sentiment_visual': analyzer._analyze_visual_sentiment(analysis_data['colors'], analysis_data['objects']),
        'confidence_score': analyzer._calculate_confidence_score(analysis_data['labels'], analysis_data['text'], analysis_data['objects'])
    }

def _build_vision_analysis_result(image_url: str, analysis_data: Dict[str, Any],
                                specialized_data: Dict[str, Any], start_time: datetime) -> VisionAnalysis:
    """Construit le résultat d'analyse complet"""
    analysis = VisionAnalysis(
        image_url=image_url,
        timestamp=datetime.now(),
        labels=analysis_data['labels'],
        text_detected=analysis_data['text'],
        objects_detected=analysis_data['objects'],
        faces_detected=analysis_data['faces'],
        colors_dominant=analysis_data['colors'],
        safe_search=analysis_data['safe_search'],
        brand_mentions=specialized_data['brand_mentions'],
        sentiment_visual=specialized_data['sentiment_visual'],
        confidence_score=specialized_data['confidence_score']
    )

    logger.info(f"✅ Image analysis completed in {(datetime.now() - start_time).total_seconds():.2f}s")
    return analysis

def _handle_vision_analysis_error(analyzer, image_url: str, error: Exception, start_time: datetime) -> VisionAnalysis:
    """Gère les erreurs d'analyse de vision"""
    logger.error(f"❌ Image analysis failed: {error}")
    return analyzer._create_error_analysis(image_url, str(error))

    def _load_image(self, image_source: str) -> vision.Image:
        """Charge une image depuis URL ou fichier"""
        if image_source.startswith('http'):
            # Charger depuis URL
            response = requests.get(image_source)
            content = response.content
        else:
            # Charger depuis fichier
            with open(image_source, 'rb') as f:
                content = f.read()

        return vision.Image(content=content)

    def _get_vision_features(self) -> List[types.Feature]:
        """Définit les features à analyser"""
        return [
            types.Feature(type_=types.Feature.Type.LABEL_DETECTION, max_results=self.config.max_results),
            types.Feature(type_=types.Feature.Type.TEXT_DETECTION, max_results=self.config.max_results),
            types.Feature(type_=types.Feature.Type.OBJECT_LOCALIZATION, max_results=self.config.max_results),
            types.Feature(type_=types.Feature.Type.FACE_DETECTION, max_results=self.config.max_results),
            types.Feature(type_=types.Feature.Type.IMAGE_PROPERTIES, max_results=self.config.max_results),
            types.Feature(type_=types.Feature.Type.SAFE_SEARCH_DETECTION),
        ]

    def _detect_labels(self, image: vision.Image, client) -> List[Dict[str, Any]]:
        """Détecte les labels"""
        try:
            response = client.label_detection(image=image, max_results=self.config.max_results)
            return [
                {'description': label.description, 'score': label.score}
                for label in response.label_annotations
            ]
        except Exception as e:
            logger.error(f"Label detection failed: {e}")
            return []

    def _detect_text(self, image: vision.Image, client) -> List[str]:
        """Détecte le texte"""
        try:
            response = client.text_detection(image=image)
            if response.text_annotations:
                return [text.description for text in response.text_annotations[1:]]  # Skip first (full text)
            return []
        except Exception as e:
            logger.error(f"Text detection failed: {e}")
            return []

    def _detect_objects(self, image: vision.Image, client) -> List[Dict[str, Any]]:
        """Détecte les objets"""
        try:
            response = client.object_localization(image=image)
            return [
                {
                    'name': obj.name,
                    'score': obj.score,
                    'bounding_box': self._bounding_box_to_dict(obj.bounding_poly)
                }
                for obj in response.localized_object_annotations
            ]
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return []

    def _detect_faces(self, image: vision.Image, client) -> List[Dict[str, Any]]:
        """Détecte les visages"""
        try:
            response = client.face_detection(image=image)
            return [
                {
                    'joy_likelihood': face.joy_likelihood,
                    'sorrow_likelihood': face.sorrow_likelihood,
                    'anger_likelihood': face.anger_likelihood,
                    'surprise_likelihood': face.surprise_likelihood,
                    'bounding_box': self._bounding_box_to_dict(face.bounding_poly)
                }
                for face in response.face_annotations
            ]
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return []

    def _detect_colors(self, image: vision.Image, client) -> List[Dict[str, Any]]:
        """Détecte les couleurs dominantes"""
        try:
            response = client.image_properties(image=image)
            return [
                {
                    'color': {
                        'red': color.color.red,
                        'green': color.color.green,
                        'blue': color.color.blue
                    },
                    'score': color.score,
                    'pixel_fraction': color.pixel_fraction
                }
                for color in response.image_properties_annotation.dominant_colors.colors[:5]  # Top 5
            ]
        except Exception as e:
            logger.error(f"Color detection failed: {e}")
            return []

    def _detect_safe_search(self, image: vision.Image, client) -> Dict[str, str]:
        """Détecte le contenu sensible"""
        try:
            response = client.safe_search_detection(image=image)
            annotation = response.safe_search_annotation
            return {
                'adult': annotation.adult.name,
                'spoof': annotation.spoof.name,
                'medical': annotation.medical.name,
                'violence': annotation.violence.name,
                'racy': annotation.racy.name
            }
        except Exception as e:
            logger.error(f"Safe search detection failed: {e}")
            return {'adult': 'UNKNOWN', 'spoof': 'UNKNOWN', 'medical': 'UNKNOWN', 'violence': 'UNKNOWN', 'racy': 'UNKNOWN'}

    def _bounding_box_to_dict(self, bounding_poly) -> Dict[str, Any]:
        """Convertit un bounding box en dictionnaire"""
        if not bounding_poly or not bounding_poly.vertices:
            return {}

        vertices = [
            {'x': vertex.x, 'y': vertex.y}
            for vertex in bounding_poly.vertices
        ]
        return {'vertices': vertices}

    def _fallback_analysis(self) -> tuple:
        """Analyse en mode fallback (sans Google Vision)"""
        labels = [{'description': 'image', 'score': 0.8}]
        text = ['Sample text detected']
        objects = [{'name': 'object', 'score': 0.6, 'bounding_box': {}}]
        faces = [{'joy_likelihood': 'LIKELY', 'bounding_box': {}}]
        colors = [{'color': {'red': 128, 'green': 128, 'blue': 128}, 'score': 0.5}]
        safe_search = {'adult': 'VERY_UNLIKELY', 'spoof': 'UNLIKELY', 'medical': 'UNLIKELY', 'violence': 'UNLIKELY', 'racy': 'UNLIKELY'}

        return labels, text, objects, faces, colors, safe_search

    def _analyze_brand_mentions(self, text_detected: List[str]) -> List[str]:
        """Analyse les mentions de marques dans le texte"""
        brand_keywords = ['logo', 'brand', 'company', 'product', 'advertisement']
        mentions = []

        for text in text_detected:
            text_lower = text.lower()
            for keyword in brand_keywords:
                if keyword in text_lower:
                    mentions.append(text)
                    break

        return mentions

    def _analyze_visual_sentiment(self, colors: List[Dict], objects: List[Dict]) -> str:
        """Analyse le sentiment visuel basé sur les couleurs et objets"""
        # Analyse simple basée sur les couleurs
        bright_colors = 0
        dark_colors = 0

        for color_info in colors:
            color = color_info['color']
            brightness = (color['red'] + color['green'] + color['blue']) / 3

            if brightness > 128:
                bright_colors += 1
            else:
                dark_colors += 1

        if bright_colors > dark_colors:
            return 'positive'
        elif dark_colors > bright_colors:
            return 'negative'
        else:
            return 'neutral'

    def _calculate_confidence_score(self, labels: List[Dict], text: List[str], objects: List[Dict]) -> float:
        """Calcule un score de confiance global"""
        scores = []

        # Score basé sur les labels
        if labels:
            avg_label_score = sum(label['score'] for label in labels) / len(labels)
            scores.append(avg_label_score)

        # Score basé sur le texte détecté
        if text:
            text_confidence = min(len(text) / 10, 1.0)  # Plus de texte = plus de confiance
            scores.append(text_confidence)

        # Score basé sur les objets
        if objects:
            avg_object_score = sum(obj['score'] for obj in objects) / len(objects)
            scores.append(avg_object_score)

        return sum(scores) / len(scores) if scores else 0.5

    def _create_error_analysis(self, image_url: str, error: str) -> VisionAnalysis:
        """Crée une analyse d'erreur"""
        return VisionAnalysis(
            image_url=image_url,
            timestamp=datetime.now(),
            labels=[],
            text_detected=[f"Error: {error}"],
            objects_detected=[],
            faces_detected=[],
            colors_dominant=[],
            safe_search={'error': error},
            brand_mentions=[],
            sentiment_visual='error',
            confidence_score=0.0
        )
