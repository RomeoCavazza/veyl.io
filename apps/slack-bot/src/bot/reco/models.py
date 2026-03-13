from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class BriefReminder(BaseModel):
    """Rappel d'un brief."""
    title: str
    objectives: List[str]
    internal_reformulation: Optional[str] = None
    summary: str

class TrendItem(BaseModel):
    """Item de tendance."""
    source: str
    title: str
    date: str
    snippet: str
    theme: str
    evidence: List[str]
    summary: str

class Insight(BaseModel):
    """Insight."""
    label: str
    evidence: List[str]
    impact: str

class Hypothesis(BaseModel):
    """Hypothèse."""
    label: str
    confidence: str
    validation: List[str]

class KPI(BaseModel):
    """KPI."""
    label: str
    value: float
    target: float
    trend: str

class DeckData(BaseModel):
    """Données pour la génération d'un deck."""
    brief_reminder: BriefReminder
    trends: List[TrendItem] = []
    brand_overview: Optional[Dict[str, Any]] = None
    state_of_play: Optional[List[Dict[str, Any]]] = None
    insights: Optional[List[Dict[str, Any]]] = None
    hypotheses: Optional[List[Dict[str, Any]]] = None
    kpis: Optional[List[Dict[str, Any]]] = None
    executive_summary: Optional[str] = None
    ideas: Optional[List[Dict[str, Any]]] = None
    timeline: Optional[List[Dict[str, Any]]] = None
    budget: Optional[List[Dict[str, Any]]] = None

class BrandOverview(BaseModel):
    """Vue d'ensemble d'une marque."""
    description_paragraphs: List[str]
    competitive_positioning: Dict[str, List[str]]
    persona: Dict[str, List[str]]
    top3_competitor_actions: List[str]

class BudgetItem(BaseModel):
    """Item de budget."""
    category: str
    estimate: float
    comment: str

class Idea(BaseModel):
    """Idée."""
    label: str
    bullets: List[str]

class Milestone(BaseModel):
    """Jalon dans une timeline."""
    label: str
    deadline: str

class StateOfPlaySection(BaseModel):
    """Section d'état des lieux."""
    theme: str
    evidence: List[str]

class RecommendationModel:
    """Modèle de base pour les recommandations."""
    
    def __init__(self):
        pass
        
    def predict(self, text: str) -> List[Dict[str, Any]]:
        """Génère des recommandations à partir du texte."""
        return []

class TrendModel:
    """Modèle pour la détection de tendances."""
    
    def __init__(self):
        pass
        
    def detect_trends(self, items: List[Dict[str, Any]]) -> List[str]:
        """Détecte les tendances dans une liste d'items."""
        return []
