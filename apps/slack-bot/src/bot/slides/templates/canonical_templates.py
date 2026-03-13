"""
Templates canoniques génériques et adaptatifs pour les slides
Basés sur l'analyse détaillée des recos existantes
"""

import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

# Chargement des templates canoniques
def load_canonical_templates():
    """Charge les templates canoniques depuis le fichier JSON"""
    template_path = os.path.join(os.path.dirname(__file__), 'canonical_templates.json')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Extraire les templates de la clé "templates"
            return data.get('templates', {})
    except FileNotFoundError:
        print(f"Warning: canonical_templates.json not found at {template_path}")
        return {}

CANONICAL_TEMPLATES = load_canonical_templates()

class SlideStyle(Enum):
    """Styles de slides identifiés"""
    STRUCTURED = "structured"  # Havana Club, EVANEOS
    CREATIVE = "creative"      # Zadig & Voltaire
    EVENT = "event"           # Serge Lutens

class SlideType(Enum):
    """Types de slides identifiés"""
    COVER = "cover"
    STRATEGIC_PRIORITIES = "strategic_priorities"
    SOMMAIRE = "sommaire"
    BRAND_OVERVIEW = "brand_overview"
    STATE_OF_PLAY = "state_of_play"
    IDEA_HEADER = "idea_header"
    IDEA_REASON = "idea_reason"
    IDEA_DATA = "idea_data"
    IDEA_EXPLANATION = "idea_explanation"
    IDEA_SOS = "idea_sos"
    IDEA_MOODBOARD = "idea_moodboard"
    IDEA_EXECUTION = "idea_execution"
    IDEA_RESULT = "idea_result"
    TIMELINE = "timeline"
    BUDGET = "budget"

class LayoutType(Enum):
    """Types de layouts identifiés"""
    CENTERED_MINIMAL = "centered_minimal"
    GRID_2X2 = "grid_2x2"
    VERTICAL_LIST = "vertical_list"
    SECTION_HEADER = "section_header"
    CENTERED_TITLE = "centered_title"
    TWO_COLUMNS = "two_columns"
    TEXT_VISUALS = "text_visuals"
    EXECUTION_DETAILS = "execution_details"
    RESULTS_KPIS = "results_kpis"
    HORIZONTAL_TIMELINE = "horizontal_timeline"
    TABLE = "table"

@dataclass
class StyleGuide:
    """Guide de style pour chaque variation"""
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str
    heading_font: str
    subheading_font: str
    body_font: str

@dataclass
class CoverContent:
    """Contenu pour slide de couverture"""
    main_title: str
    subtitle: str
    agency: str = "REVOLVR"
    tagline: str = "KILLING IT SINCE 2010"
    brand_logo_url: Optional[str] = None
    agency_logo_url: str = "assets/revolvr_logo.png"

@dataclass
class CoverTemplate:
    """Template générique pour slide de couverture"""
    type: str = "cover"
    layout: str = "centered_minimal"
    content: CoverContent = field(default_factory=CoverContent)
    
    def get_style_guide(self, style: SlideStyle) -> StyleGuide:
        """Retourne le guide de style selon le style choisi"""
        style_guides = {
            SlideStyle.STRUCTURED: StyleGuide(
                primary_color="#2C3E50",
                secondary_color="#34495E",
                accent_color="#3498DB",
                background_color="#ECF0F1",
                heading_font="Montserrat Bold",
                subheading_font="Montserrat Regular",
                body_font="Open Sans Regular"
            ),
            SlideStyle.CREATIVE: StyleGuide(
                primary_color="#E74C3C",
                secondary_color="#F39C12",
                accent_color="#9B59B6",
                background_color="#F8F9FA",
                heading_font="Playfair Display",
                subheading_font="Open Sans",
                body_font="Lato Regular"
            ),
            SlideStyle.EVENT: StyleGuide(
                primary_color="#1ABC9C",
                secondary_color="#16A085",
                accent_color="#F1C40F",
                background_color="#FFFFFF",
                heading_font="Roboto Condensed",
                subheading_font="Roboto",
                body_font="Roboto Regular"
            )
        }
        return style_guides[style]

@dataclass
class Priority:
    """Une priorité stratégique"""
    text: str
    icon: Optional[str] = None
    color: Optional[str] = None

@dataclass
class StrategicPrioritiesContent:
    """Contenu pour slide des priorités stratégiques"""
    title: str = "STRATEGIC PRIORITIES"
    priorities: List[Priority] = field(default_factory=list)

@dataclass
class StrategicPrioritiesTemplate:
    """Template générique pour slide des priorités stratégiques"""
    type: str = "strategic_priorities"
    layout: str = "grid_2x2"
    content: StrategicPrioritiesContent = field(default_factory=StrategicPrioritiesContent)
    
    def get_priorities_by_sector(self, sector: str) -> List[str]:
        """Retourne les priorités typiques par secteur"""
        sector_priorities = {
            "luxury": ["Increase brand awareness", "Drive consideration", "Generate leads", "Build community"],
            "tech": ["User acquisition", "Product adoption", "Retention", "Virality"],
            "fashion": ["Brand awareness", "Desire", "Purchase intent", "Loyalty"],
            "food": ["Trial", "Repeat purchase", "Recommendation", "Brand love"],
            "automotive": ["Awareness", "Consideration", "Test drive", "Purchase"],
            "default": ["Increase awareness", "Drive engagement", "Generate leads", "Build loyalty"]
        }
        return sector_priorities.get(sector, sector_priorities["default"])

@dataclass
class SommaireSection:
    """Section du sommaire"""
    number: str
    title: str
    subtitle: str

@dataclass
class SommaireContent:
    """Contenu pour slide de sommaire"""
    title: str = "SOMMAIRE"
    sections: List[SommaireSection] = field(default_factory=list)

@dataclass
class SommaireTemplate:
    """Template générique pour slide de sommaire"""
    type: str = "sommaire"
    layout: str = "vertical_list"
    content: SommaireContent = field(default_factory=SommaireContent)
    
    def get_trend_types(self) -> Dict[str, str]:
        """Retourne les types de tendances disponibles"""
        return {
            "social": "SOCIAL TREND",
            "tech": "TECH TREND",
            "cultural": "CULTURAL TREND",
            "behavioral": "BEHAVIORAL TREND",
            "environmental": "ENVIRONMENTAL TREND"
        }

@dataclass
class BrandOverviewContent:
    """Contenu pour slide de brand overview"""
    title: str = "BRAND OVERVIEW"
    brand_story: str = ""
    core_values: List[str] = field(default_factory=list)
    positioning: str = ""
    target_demographics: str = ""
    target_psychographics: str = ""
    key_messages: List[str] = field(default_factory=list)

@dataclass
class BrandOverviewTemplate:
    """Template générique pour slide de brand overview"""
    type: str = "brand_overview"
    layout: str = "two_columns"
    content: BrandOverviewContent = field(default_factory=BrandOverviewContent)

@dataclass
class StateOfPlaySection:
    """Section du state of play"""
    title: str
    content: str
    data_points: List[str] = field(default_factory=list)

@dataclass
class StateOfPlayContent:
    """Contenu pour slide de state of play"""
    title: str = "STATE OF PLAY"
    sections: List[StateOfPlaySection] = field(default_factory=list)

@dataclass
class StateOfPlayTemplate:
    """Template générique pour slide de state of play"""
    type: str = "state_of_play"
    layout: str = "grid_2x2"
    content: StateOfPlayContent = field(default_factory=StateOfPlayContent)

@dataclass
class IdeaContent:
    """Contenu pour une idée"""
    title: str
    concept_name: str
    trend_context: str
    opportunity: str
    market_gap: str
    consumer_need: str
    statistics: List[Dict[str, str]] = field(default_factory=list)
    trends: str = ""
    how_it_works: str = ""
    key_components: List[str] = field(default_factory=list)
    user_journey: str = ""
    amplification: str = ""
    viral_elements: List[str] = field(default_factory=list)
    partnerships: str = ""
    visual_direction: str = ""
    color_palette: List[str] = field(default_factory=list)
    imagery_style: str = ""
    ai_generated_images: List[str] = field(default_factory=list)
    implementation: str = ""
    channels: List[str] = field(default_factory=list)
    execution_timeline: str = ""
    resource_requirements: str = ""
    expected_outcomes: List[str] = field(default_factory=list)
    kpis: List[Dict[str, str]] = field(default_factory=list)
    roi_projection: str = ""

@dataclass
class IdeaTemplate:
    """Template générique pour les slides d'idées"""
    type: str = "idea_series"
    idea_count: int = 3
    slides_per_idea: int = 9
    content: IdeaContent = field(default_factory=IdeaContent)

@dataclass
class TimelinePhase:
    """Phase du timeline"""
    phase: str
    name: str
    duration: str
    activities: List[str] = field(default_factory=list)
    milestones: List[str] = field(default_factory=list)

@dataclass
class TimelineContent:
    """Contenu pour slide de timeline"""
    title: str = "TIMELINE"
    phases: List[TimelinePhase] = field(default_factory=list)

@dataclass
class TimelineTemplate:
    """Template générique pour slide de timeline"""
    type: str = "timeline"
    layout: str = "horizontal_timeline"
    content: TimelineContent = field(default_factory=TimelineContent)

@dataclass
class BudgetCategory:
    """Catégorie de budget"""
    category: str
    amount: str
    percentage: str
    breakdown: List[str] = field(default_factory=list)

@dataclass
class BudgetContent:
    """Contenu pour slide de budget"""
    title: str = "BUDGET"
    total_budget: str = ""
    categories: List[BudgetCategory] = field(default_factory=list)

@dataclass
class BudgetTemplate:
    """Template générique pour slide de budget"""
    type: str = "budget"
    layout: str = "table"
    content: BudgetContent = field(default_factory=BudgetContent)

class TemplateFactory:
    """Factory pour créer des templates"""
    
    @staticmethod
    def create_template(slide_type: SlideType, style: SlideStyle) -> Any:
        """Crée un template selon le type et le style"""
        template_map = {
            SlideType.COVER: CoverTemplate,
            SlideType.STRATEGIC_PRIORITIES: StrategicPrioritiesTemplate,
            SlideType.SOMMAIRE: SommaireTemplate,
            SlideType.BRAND_OVERVIEW: BrandOverviewTemplate,
            SlideType.STATE_OF_PLAY: StateOfPlayTemplate,
            SlideType.IDEA_HEADER: IdeaTemplate,
            SlideType.TIMELINE: TimelineTemplate,
            SlideType.BUDGET: BudgetTemplate
        }
        
        template_class = template_map.get(slide_type)
        if template_class:
            return template_class()
        else:
            raise ValueError(f"Unknown slide type: {slide_type}")

class StyleDetector:
    """Détecteur de style basé sur le contenu"""
    
    @staticmethod
    def detect_style(brief_content: str, sector: str, project_type: str) -> SlideStyle:
        """Détecte le style approprié basé sur le brief"""
        # Logique de détection basée sur le secteur et le type de projet
        if sector.lower() in ['luxury', 'premium', 'high-end']:
            return SlideStyle.STRUCTURED
        elif sector.lower() in ['fashion', 'creative', 'arts']:
            return SlideStyle.CREATIVE
        elif project_type.lower() in ['event', 'activation', 'launch']:
            return SlideStyle.EVENT
        else:
            return SlideStyle.STRUCTURED  # Default

class ContentAdapter:
    """Adaptateur de contenu pour les templates"""
    
    @staticmethod
    def adapt_content(template: Any, brief_data: Dict, veille_data: Dict, style: SlideStyle) -> Any:
        """Adapte le contenu du template selon les données"""
        # Logique d'adaptation du contenu
        return template

class IdeaGenerator:
    """Générateur d'idées basé sur la veille"""
    
    @staticmethod
    def generate_ideas(brief_data: Dict, veille_data: Dict, style: SlideStyle) -> List[IdeaContent]:
        """Génère des idées basées sur la veille et le brief"""
        # Logique de génération d'idées
        return []

# Fonction utilitaire pour obtenir le chemin des templates
def get_template_path(template_name: str) -> str:
    """Retourne le chemin vers un template"""
    template_dir = os.path.dirname(__file__)
    return os.path.join(template_dir, f"{template_name}.json")
