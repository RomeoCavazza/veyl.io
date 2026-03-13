"""
Configuration du Pipeline
Module spécialisé pour la configuration
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PipelineConfig:
    """Configuration du pipeline"""
    brand_name: str
    sector: str
    project_type: str
    target_audience: str
    brand_story: str
    core_values: List[str]
    positioning: str
    competitors: List[str]
    output_format: str = 'pptx'
    enable_image_generation: bool = True
    enable_veille: bool = True
    enable_ai_da: bool = True

    def to_dict(self) -> Dict:
        """Convertit en dictionnaire"""
        return {
            'brand_name': self.brand_name,
            'sector': self.sector,
            'project_type': self.project_type,
            'target_audience': self.target_audience,
            'brand_story': self.brand_story,
            'core_values': self.core_values,
            'positioning': self.positioning,
            'competitors': self.competitors,
            'output_format': self.output_format,
            'enable_image_generation': self.enable_image_generation,
            'enable_veille': self.enable_veille,
            'enable_ai_da': self.enable_ai_da
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'PipelineConfig':
        """Crée une instance depuis un dictionnaire"""
        return cls(
            brand_name=data['brand_name'],
            sector=data['sector'],
            project_type=data['project_type'],
            target_audience=data['target_audience'],
            brand_story=data['brand_story'],
            core_values=data.get('core_values', []),
            positioning=data['positioning'],
            competitors=data.get('competitors', []),
            output_format=data.get('output_format', 'pptx'),
            enable_image_generation=data.get('enable_image_generation', True),
            enable_veille=data.get('enable_veille', True),
            enable_ai_da=data.get('enable_ai_da', True)
        )

@dataclass
class PipelineResult:
    """Résultat du pipeline"""
    success: bool
    veille_data: Optional[any] = None  # Type will be imported when needed
    style_guide: Optional[any] = None  # Type will be imported when needed
    presentation_path: Optional[str] = None
    image_prompts: List[any] = None  # Type will be imported when needed
    execution_time: float = 0.0
    errors: List[str] = None
    logs: List[str] = None

    def __post_init__(self):
        if self.image_prompts is None:
            self.image_prompts = []
        if self.errors is None:
            self.errors = []
        if self.logs is None:
            self.logs = []

    def to_dict(self) -> Dict:
        """Convertit en dictionnaire"""
        return {
            'success': self.success,
            'veille_data': self.veille_data,
            'style_guide': self.style_guide,
            'presentation_path': self.presentation_path,
            'image_prompts': self.image_prompts,
            'execution_time': self.execution_time,
            'errors': self.errors,
            'logs': self.logs
        }
