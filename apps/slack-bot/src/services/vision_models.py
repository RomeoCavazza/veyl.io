"""
Modèles de données pour le service Vision
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class VisionAnalysis:
    """Résultat d'analyse d'image/vidéo"""
    image_url: str
    timestamp: datetime
    labels: List[Dict[str, Any]]
    text_detected: List[str]
    objects_detected: List[Dict[str, Any]]
    faces_detected: List[Dict[str, Any]]
    colors_dominant: List[Dict[str, Any]]
    safe_search: Dict[str, str]
    brand_mentions: List[str]
    sentiment_visual: str
    confidence_score: float

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'image_url': self.image_url,
            'timestamp': self.timestamp.isoformat(),
            'labels': self.labels,
            'text_detected': self.text_detected,
            'objects_detected': self.objects_detected,
            'faces_detected': self.faces_detected,
            'colors_dominant': self.colors_dominant,
            'safe_search': self.safe_search,
            'brand_mentions': self.brand_mentions,
            'sentiment_visual': self.sentiment_visual,
            'confidence_score': self.confidence_score
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VisionAnalysis':
        """Crée une instance depuis un dictionnaire"""
        return cls(
            image_url=data['image_url'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            labels=data.get('labels', []),
            text_detected=data.get('text_detected', []),
            objects_detected=data.get('objects_detected', []),
            faces_detected=data.get('faces_detected', []),
            colors_dominant=data.get('colors_dominant', []),
            safe_search=data.get('safe_search', {}),
            brand_mentions=data.get('brand_mentions', []),
            sentiment_visual=data.get('sentiment_visual', 'neutral'),
            confidence_score=data.get('confidence_score', 0.5)
        )

@dataclass
class VisionConfig:
    """Configuration du service Vision"""
    api_key: Optional[str] = None
    max_results: int = 10
    language_hints: List[str] = None
    model: str = 'builtin/stable'

    def __post_init__(self):
        if self.language_hints is None:
            self.language_hints = ['en', 'fr']

@dataclass
class VisionBatchResult:
    """Résultat d'analyse par lot"""
    total_images: int
    successful_analyses: int
    failed_analyses: int
    analyses: List[VisionAnalysis]
    errors: List[str]
    processing_time: float

    def success_rate(self) -> float:
        """Calcule le taux de succès"""
        return self.successful_analyses / self.total_images if self.total_images > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'total_images': self.total_images,
            'successful_analyses': self.successful_analyses,
            'failed_analyses': self.failed_analyses,
            'success_rate': self.success_rate(),
            'analyses': [analysis.to_dict() for analysis in self.analyses],
            'errors': self.errors,
            'processing_time': self.processing_time
        }
