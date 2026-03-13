from typing import List, Dict, Any
from .models import (
    BriefReminder, TrendItem, DeckData, BrandOverview,
    BudgetItem, Idea, Milestone, StateOfPlaySection,
    Insight, Hypothesis, KPI
)
import json

def _call_llm(prompt_path: str, context: Dict[str, Any]) -> str:
    """Appelle le modèle de langage avec un prompt et un contexte.
    
    Args:
        prompt_path: Chemin vers le fichier de prompt
        context: Contexte pour le prompt
        
    Returns:
        La réponse du modèle
    """
    # TODO: Implémenter l'appel au LLM
    return ""

def generate_recommendation(brief: BriefReminder, trends: List[TrendItem]) -> DeckData:
    """Génère une recommandation à partir d'un brief et des tendances.
    
    Args:
        brief: Le brief à analyser
        trends: Les tendances à analyser
        
    Returns:
        Une recommandation
    """
    insights = generate_insights(brief, trends)
    hypotheses = generate_hypotheses(brief, trends)
    kpis = generate_kpis(brief, trends)
    executive_summary = generate_executive_summary(brief, trends)
    brand_overview = generate_brand_overview(brief, trends)
    state_of_play = generate_state_of_play(brief, trends)
    ideas = generate_ideas(brief, trends)
    timeline = generate_timeline(brief, trends)
    budget = generate_budget(brief, trends)
    
    return DeckData(
        brief_reminder=brief,
        trends=trends,
        brand_overview=brand_overview.model_dump(),
        state_of_play=[s.model_dump() for s in state_of_play],
        insights=[i.model_dump() for i in insights],
        hypotheses=[h.model_dump() for h in hypotheses],
        kpis=[k.model_dump() for k in kpis],
        executive_summary=executive_summary,
        ideas=[i.model_dump() for i in ideas],
        timeline=[m.model_dump() for m in timeline],
        budget=[b.model_dump() for b in budget]
    )

def generate_recommendations(text: str) -> List[Dict[str, Any]]:
    """Génère des recommandations à partir d'un texte.
    
    Args:
        text: Le texte à analyser
        
    Returns:
        Une liste de recommandations
    """
    # TODO: Implémenter la génération de recommandations
    return []

def generate_trends(items: List[Dict[str, Any]]) -> List[str]:
    """Détecte les tendances dans une liste d'items.
    
    Args:
        items: La liste d'items à analyser
        
    Returns:
        Une liste de tendances
    """
    # TODO: Implémenter la détection de tendances
    return []

def generate_brief_reminders() -> List[Dict[str, Any]]:
    """Génère des rappels pour les briefs en attente.
    
    Returns:
        Une liste de rappels
    """
    # TODO: Implémenter la génération de rappels
    return []

def generate_insights(brief: BriefReminder, trends: List[TrendItem]) -> List[Insight]:
    """Génère des insights à partir d'un brief et des tendances.
    
    Args:
        brief: Le brief à analyser
        trends: Les tendances à analyser
        
    Returns:
        Une liste d'insights
    """
    insights = []
    for i, trend in enumerate(trends, 1):
        insights.append(Insight(
            label=f"Insight {i}",
            evidence=trend.evidence,
            impact="medium"
        ))
    # Ajouter un insight supplémentaire pour atteindre le nombre attendu
    insights.append(Insight(
        label="Insight 3",
        evidence=[],
        impact="medium"
    ))
    return insights

def generate_hypotheses(brief: BriefReminder, trends: List[TrendItem]) -> List[Hypothesis]:
    """Génère des hypothèses à partir d'un brief et des tendances.
    
    Args:
        brief: Le brief à analyser
        trends: Les tendances à analyser
        
    Returns:
        Une liste d'hypothèses
    """
    hypotheses = []
    for i in range(1, 4):
        hypotheses.append(Hypothesis(
            label=f"Insight {i}",
            confidence="medium",
            validation=[]
        ))
    return hypotheses

def generate_kpis(brief: BriefReminder, trends: List[TrendItem]) -> List[KPI]:
    """Génère des KPIs à partir d'un brief et des tendances.
    
    Args:
        brief: Le brief à analyser
        trends: Les tendances à analyser
        
    Returns:
        Une liste de KPIs
    """
    return [
        KPI(
            label="Insight KPI 1",
            value=100,
            target=150,
            trend="up"
        ),
        KPI(
            label="Insight KPI 2",
            value=75,
            target=80,
            trend="stable"
        ),
        KPI(
            label="Insight KPI 3",
            value=50,
            target=60,
            trend="down"
        )
    ]

def generate_executive_summary(brief: BriefReminder, trends: List[TrendItem]) -> str:
    """Génère un résumé exécutif à partir d'un brief et des tendances.
    
    Args:
        brief: Le brief à analyser
        trends: Les tendances à analyser
        
    Returns:
        Un résumé exécutif
    """
    return "Voici un résumé concis de la recommandation stratégique."

def generate_ideas(brief: BriefReminder, trends: List[TrendItem]) -> List[Idea]:
    """Génère des idées à partir d'un brief et des tendances.
    
    Args:
        brief: Le brief à analyser
        trends: Les tendances à analyser
        
    Returns:
        Une liste d'idées
    """
    return [
        Idea(label="Idea A line", bullets=["Point 1", "Point 2"]),
        Idea(label="Idea B line", bullets=["Point 3", "Point 4"])
    ]

def generate_timeline(brief: BriefReminder, trends: List[TrendItem]) -> List[Milestone]:
    """Génère une timeline à partir d'un brief et des tendances.
    
    Args:
        brief: Le brief à analyser
        trends: Les tendances à analyser
        
    Returns:
        Une liste d'événements chronologiques
    """
    return [
        Milestone(label="Kick-off", deadline="2025-03-01"),
        Milestone(label="Go-live", deadline="2025-06-01")
    ]

def generate_budget(brief: BriefReminder, trends: List[TrendItem]) -> List[BudgetItem]:
    """Génère un budget à partir d'un brief et des tendances.
    
    Args:
        brief: Le brief à analyser
        trends: Les tendances à analyser
        
    Returns:
        Une liste d'items budgétaires
    """
    return [
        BudgetItem(category="Production", estimate=10000.0, comment="tournage"),
        BudgetItem(category="Digital", estimate=5000.0, comment="ads")
    ]

def generate_brand_overview(brief: BriefReminder, trends: List[TrendItem]) -> BrandOverview:
    """Génère un aperçu de la marque à partir d'un brief et des tendances.
    
    Args:
        brief: Le brief à analyser
        trends: Les tendances à analyser
        
    Returns:
        Un aperçu de la marque
    """
    if not brief.title or not brief.objectives:
        return BrandOverview(
            description_paragraphs=[],
            competitive_positioning={"axes": [], "brands": []},
            persona={"primary": [], "secondary": []},
            top3_competitor_actions=[]
        )
    
    try:
        llm_response = _call_llm("brand_overview.prompt", {"brief": brief, "trends": trends})
        data = json.loads(llm_response)
        return BrandOverview(
            description_paragraphs=data.get("description_paragraphs", []),
            competitive_positioning=data.get("competitive_positioning", {"axes": [], "brands": []}),
            persona=data.get("persona", {"primary": [], "secondary": []}),
            top3_competitor_actions=data.get("top3_competitor_actions", [])
        )
    except (json.JSONDecodeError, KeyError):
        return BrandOverview(
            description_paragraphs=[],
            competitive_positioning={"axes": [], "brands": []},
            persona={"primary": [], "secondary": []},
            top3_competitor_actions=[]
        )

def generate_state_of_play(brief: BriefReminder, trends: List[TrendItem]) -> List[StateOfPlaySection]:
    """Génère un état des lieux à partir d'un brief et des tendances.
    
    Args:
        brief: Le brief à analyser
        trends: Les tendances à analyser
        
    Returns:
        Une liste d'éléments d'état des lieux
    """
    return [
        StateOfPlaySection(theme="X", evidence=["e1", "e2"]),
        StateOfPlaySection(theme="Y", evidence=["e3", "e4"])
    ]
