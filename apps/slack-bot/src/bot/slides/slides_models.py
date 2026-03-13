"""
Modèles de données pour Google Slides
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SlideContent:
    """Contenu d'une slide"""
    title: str
    subtitle: Optional[str] = None
    content: List[str] = None
    image_url: Optional[str] = None
    chart_data: Optional[Dict] = None
    table_data: Optional[List[List[str]]] = None
    bullet_points: List[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None

    def __post_init__(self):
        if self.content is None:
            self.content = []
        if self.bullet_points is None:
            self.bullet_points = []

@dataclass
class PresentationConfig:
    """Configuration d'une présentation"""
    title: str
    subtitle: Optional[str] = None
    theme: str = "default"
    slide_size: str = "16:9"
    background_color: str = "#FFFFFF"
    primary_color: str = "#4285F4"
    secondary_color: str = "#34A853"
    font_family: str = "Arial"
    font_size_title: int = 32
    font_size_subtitle: int = 24
    font_size_body: int = 16

@dataclass
class GoogleSlidesResult:
    """Résultat d'une opération Google Slides"""
    success: bool
    presentation_id: Optional[str] = None
    presentation_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = None
    slide_count: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict:
        """Convertit en dictionnaire"""
        return {
            'success': self.success,
            'presentation_id': self.presentation_id,
            'presentation_url': self.presentation_url,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'slide_count': self.slide_count
        }
