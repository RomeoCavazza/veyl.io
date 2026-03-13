#!/usr/bin/env python3
"""
Intégration du template de recommandation dans l'architecture Scout
Met à jour les modèles et générateurs existants
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any

class ScoutTemplateIntegrator:
    """Intégrateur de templates dans l'architecture Scout"""
    
    def __init__(self):
        self.scout_dir = Path("src/scout")
        self.template_file = Path("reco_template_havana.json")
        self.backup_dir = Path("backups/templates")
        
    def load_template(self) -> Dict[str, Any]:
        """Charge le template Havana"""
        with open(self.template_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def backup_existing_files(self):
        """Sauvegarde les fichiers existants"""
        print("💾 Sauvegarde des fichiers existants...")
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        files_to_backup = [
            "src/scout/data/recommendation_models.py",
            "src/scout/livrables/templates/recommendation_template.py",
            "src/scout/livrables/generators/recommendation_generator.py",
            "src/scout/intelligence/ai/recommendation_prompts.py"
        ]
        
        for file_path in files_to_backup:
            if Path(file_path).exists():
                backup_path = self.backup_dir / Path(file_path).name
                shutil.copy2(file_path, backup_path)
                print(f"  ✅ {file_path} → {backup_path}")
    
    def update_recommendation_models(self, template: Dict[str, Any]):
        """Met à jour les modèles de données"""
        print("📊 Mise à jour des modèles de recommandation...")
        
        models_content = '''"""
Modèles de données pour les recommandations - 7 parties structurées
Basé sur l'analyse Havana Club
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class RecommendationType(Enum):
    """Types de recommandations"""
    NEW_BUSINESS = "new_business"      # Nouveau client
    EXISTING_CLIENT = "existing_client"  # Client existant
    COMPETITIVE_PITCH = "competitive_pitch"  # Appel d'offres


@dataclass
class SlideData:
    """Données pour une slide individuelle"""
    slide_type: str
    title: str
    subtitle: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    visual_elements: List[str] = field(default_factory=list)
    data_mappings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BrandOverview:
    """1. Brand Overview - Vue d'ensemble de la marque"""
    brand_name: str
    description: str
    positioning: str
    target_persona: Dict[str, Any]
    brand_values: List[str] = field(default_factory=list)
    key_differentiators: List[str] = field(default_factory=list)
    market_position: str = ""
    brand_voice: str = ""
    visual_identity: Dict[str, Any] = field(default_factory=dict)
    slides: List[SlideData] = field(default_factory=list)


@dataclass
class StateOfPlay:
    """2. State of Play - État du marché et audit"""
    market_context: str
    client_audit: Dict[str, Any]
    benchmark_3_main: List[Dict[str, Any]] = field(default_factory=list)
    competitor_mapping: Dict[str, List[str]] = field(default_factory=dict)
    market_trends: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)
    market_size: Optional[str] = None
    growth_rate: Optional[str] = None
    slides: List[SlideData] = field(default_factory=list)


@dataclass
class CulturalTrend:
    """3. Idea #1. Cultural Trends - Tendances culturelles"""
    trend_name: str
    trend_description: str
    cultural_context: str
    opportunity_description: str
    brand_relevance: str
    potential_impact: str
    execution_concept: str
    key_elements: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    slides: List[SlideData] = field(default_factory=list)


@dataclass
class TikTokTrend:
    """4. Idea #2. TikTok Trends - Tendances TikTok"""
    trend_name: str
    trend_description: str
    virality_score: float
    concept_description: str
    viral_elements: List[str] = field(default_factory=list)
    content_strategy: str
    target_audience: str
    slides: List[SlideData] = field(default_factory=list)


@dataclass
class SocietalTrend:
    """5. Idea #3. Societal Trends - Tendances sociétales"""
    trend_name: str
    trend_description: str
    societal_impact: str
    purpose_statement: str
    social_impact: str
    brand_role: str
    purpose_alignment: str
    slides: List[SlideData] = field(default_factory=list)


@dataclass
class Timeline:
    """6. Timeline - Planning et échéances"""
    phases: List[Dict[str, Any]] = field(default_factory=list)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    deliverables: List[Dict[str, Any]] = field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    slides: List[SlideData] = field(default_factory=list)


@dataclass
class Budget:
    """7. Budget - Budget et ressources"""
    total_budget: float
    cost_breakdown: Dict[str, float] = field(default_factory=dict)
    roi_projection: Dict[str, Any] = field(default_factory=dict)
    resource_allocation: Dict[str, Any] = field(default_factory=dict)
    slides: List[SlideData] = field(default_factory=list)


@dataclass
class Recommendation:
    """Recommandation complète avec 7 parties"""
    recommendation_type: RecommendationType
    brand_overview: BrandOverview
    state_of_play: StateOfPlay
    cultural_trend: CulturalTrend
    tiktok_trend: TikTokTrend
    societal_trend: SocietalTrend
    timeline: Timeline
    budget: Budget
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_total_slides(self) -> int:
        """Retourne le nombre total de slides"""
        return (len(self.brand_overview.slides) + 
                len(self.state_of_play.slides) + 
                len(self.cultural_trend.slides) + 
                len(self.tiktok_trend.slides) + 
                len(self.societal_trend.slides) + 
                len(self.timeline.slides) + 
                len(self.budget.slides))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "recommendation_type": self.recommendation_type.value,
            "brand_overview": {
                "brand_name": self.brand_overview.brand_name,
                "description": self.brand_overview.description,
                "positioning": self.brand_overview.positioning,
                "target_persona": self.brand_overview.target_persona,
                "brand_values": self.brand_overview.brand_values,
                "key_differentiators": self.brand_overview.key_differentiators,
                "market_position": self.brand_overview.market_position,
                "brand_voice": self.brand_overview.brand_voice,
                "visual_identity": self.brand_overview.visual_identity
            },
            "state_of_play": {
                "market_context": self.state_of_play.market_context,
                "client_audit": self.state_of_play.client_audit,
                "benchmark_3_main": self.state_of_play.benchmark_3_main,
                "competitor_mapping": self.state_of_play.competitor_mapping,
                "market_trends": self.state_of_play.market_trends,
                "opportunities": self.state_of_play.opportunities,
                "threats": self.state_of_play.threats,
                "market_size": self.state_of_play.market_size,
                "growth_rate": self.state_of_play.growth_rate
            },
            "cultural_trend": {
                "trend_name": self.cultural_trend.trend_name,
                "trend_description": self.cultural_trend.trend_description,
                "cultural_context": self.cultural_trend.cultural_context,
                "opportunity_description": self.cultural_trend.opportunity_description,
                "brand_relevance": self.cultural_trend.brand_relevance,
                "potential_impact": self.cultural_trend.potential_impact,
                "execution_concept": self.cultural_trend.execution_concept,
                "key_elements": self.cultural_trend.key_elements,
                "deliverables": self.cultural_trend.deliverables
            },
            "tiktok_trend": {
                "trend_name": self.tiktok_trend.trend_name,
                "trend_description": self.tiktok_trend.trend_description,
                "virality_score": self.tiktok_trend.virality_score,
                "concept_description": self.tiktok_trend.concept_description,
                "viral_elements": self.tiktok_trend.viral_elements,
                "content_strategy": self.tiktok_trend.content_strategy,
                "target_audience": self.tiktok_trend.target_audience
            },
            "societal_trend": {
                "trend_name": self.societal_trend.trend_name,
                "trend_description": self.societal_trend.trend_description,
                "societal_impact": self.societal_trend.societal_impact,
                "purpose_statement": self.societal_trend.purpose_statement,
                "social_impact": self.societal_trend.social_impact,
                "brand_role": self.societal_trend.brand_role,
                "purpose_alignment": self.societal_trend.purpose_alignment
            },
            "timeline": {
                "phases": self.timeline.phases,
                "milestones": self.timeline.milestones,
                "deliverables": self.timeline.deliverables,
                "start_date": self.timeline.start_date.isoformat() if self.timeline.start_date else None,
                "end_date": self.timeline.end_date.isoformat() if self.timeline.end_date else None
            },
            "budget": {
                "total_budget": self.budget.total_budget,
                "cost_breakdown": self.budget.cost_breakdown,
                "roi_projection": self.budget.roi_projection,
                "resource_allocation": self.budget.resource_allocation
            },
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "total_slides": self.get_total_slides()
        }
'''
        
        with open("src/scout/data/recommendation_models.py", 'w', encoding='utf-8') as f:
            f.write(models_content)
        
        print("  ✅ Modèles de recommandation mis à jour")
    
    def update_recommendation_template(self, template: Dict[str, Any]):
        """Met à jour le template de recommandation"""
        print("📋 Mise à jour du template de recommandation...")
        
        template_content = f'''"""
Template pour les recommandations basé sur l'analyse Havana Club
Structure complète avec 7 parties et {template['total_slides']} slides
"""

from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass

from ...data.recommendation_models import (
    Recommendation, BrandOverview, StateOfPlay, CulturalTrend,
    TikTokTrend, SocietalTrend, Timeline, Budget, SlideData
)


@dataclass
class RecommendationTemplate:
    """Template pour les recommandations basé sur l'analyse Havana Club"""
    
    def __init__(self):
        self.template_data = {json.dumps(template, indent=2)}
    
    def generate_recommendation_template(self, recommendation: Recommendation) -> str:
        """
        Génère une recommandation au format Havana Club
        
        Structure:
        - 7 parties principales
        - {template['total_slides']} slides total
        - Mappings data → slides automatisés
        """
        return f"""
        RECOMMENDATION TEMPLATE - {template['name']}
        
        {template['description']}
        
        SECTIONS:
        {chr(10).join([f"- {{section}}: {{len(slides)}} slides" for section, slides in template['sections'].items()])}
        
        TOTAL SLIDES: {template['total_slides']}
        DATA SOURCES: {', '.join(template['data_sources'])}
        AI CONFIG: {template['ai_config']['model']} (temp: {template['ai_config']['temperature']})
        """
    
    def get_slide_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Retourne les templates de slides par section"""
        return {json.dumps(template['sections'], indent=2)}
    
    def map_data_to_slides(self, recommendation: Recommendation) -> Dict[str, List[SlideData]]:
        """Mappe les données de recommandation aux slides"""
        slides_mapping = {{}}
        
        # Mapping pour chaque section
        for section_name, slide_templates in template['sections'].items():
            slides_mapping[section_name] = []
            
            for slide_template in slide_templates:
                slide_data = SlideData(
                    slide_type=slide_template['slide_type'],
                    title=slide_template['title'],
                    subtitle=slide_template['subtitle'],
                    layout=slide_template['layout'],
                    content_sections=slide_template['content_sections'],
                    visual_elements=slide_template['visual_elements'],
                    data_mappings=slide_template['data_mappings'],
                    ai_prompts=slide_template['ai_prompts']
                )
                slides_mapping[section_name].append(slide_data)
        
        return slides_mapping
'''
        
        with open("src/scout/livrables/templates/recommendation_template.py", 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print("  ✅ Template de recommandation mis à jour")
    
    def update_recommendation_generator(self, template: Dict[str, Any]):
        """Met à jour le générateur de recommandation"""
        print("🔧 Mise à jour du générateur de recommandation...")
        
        generator_content = f'''"""
Générateur de recommandations basé sur le template Havana Club
Génère automatiquement {template['total_slides']} slides structurées
"""

from typing import Dict, Any, List
from ...data.recommendation_models import Recommendation, SlideData
from ..templates.recommendation_template import RecommendationTemplate


class RecommendationGenerator:
    """Générateur de recommandations avec template Havana Club"""
    
    def __init__(self):
        self.template = RecommendationTemplate()
        self.ai_config = {json.dumps(template['ai_config'], indent=2)}
    
    def generate_recommendation(self, 
                              brief_data: Dict[str, Any], 
                              veille_data: Dict[str, Any],
                              competitor_analysis: Dict[str, Any],
                              trend_analysis: Dict[str, Any]) -> Recommendation:
        """
        Génère une recommandation complète basée sur les données
        
        Args:
            brief_data: Données du brief client
            veille_data: Données de veille
            competitor_analysis: Analyse concurrentielle
            trend_analysis: Analyse des tendances
        
        Returns:
            Recommendation: Recommandation complète avec 7 parties
        """
        print(f"🚀 Génération de recommandation avec {template['total_slides']} slides...")
        
        # Génération des 7 parties
        brand_overview = self._generate_brand_overview(brief_data, veille_data)
        state_of_play = self._generate_state_of_play(brief_data, veille_data, competitor_analysis)
        cultural_trend = self._generate_cultural_trend(trend_analysis)
        tiktok_trend = self._generate_tiktok_trend(trend_analysis)
        societal_trend = self._generate_societal_trend(trend_analysis)
        timeline = self._generate_timeline(brief_data)
        budget = self._generate_budget(brief_data)
        
        # Création de la recommandation
        recommendation = Recommendation(
            recommendation_type=brief_data.get('recommendation_type', 'new_business'),
            brand_overview=brand_overview,
            state_of_play=state_of_play,
            cultural_trend=cultural_trend,
            tiktok_trend=tiktok_trend,
            societal_trend=societal_trend,
            timeline=timeline,
            budget=budget,
            metadata={{
                'template_version': 'havana_style',
                'total_slides': {template['total_slides']},
                'generated_at': datetime.now().isoformat()
            }}
        )
        
        # Mapping des slides
        slides_mapping = self.template.map_data_to_slides(recommendation)
        
        # Attribution des slides aux sections
        recommendation.brand_overview.slides = slides_mapping.get('1. Brand Overview', [])
        recommendation.state_of_play.slides = slides_mapping.get('2. State of Play', [])
        recommendation.cultural_trend.slides = slides_mapping.get('3. Idea #1. Cultural Trends', [])
        recommendation.tiktok_trend.slides = slides_mapping.get('4. Idea #2. TikTok Trends', [])
        recommendation.societal_trend.slides = slides_mapping.get('5. Idea #3. Societal Trends', [])
        recommendation.timeline.slides = slides_mapping.get('6. Timeline', [])
        recommendation.budget.slides = slides_mapping.get('7. Budget', [])
        
        print(f"✅ Recommandation générée avec {{recommendation.get_total_slides()}} slides")
        return recommendation
    
    def _generate_brand_overview(self, brief_data: Dict[str, Any], veille_data: Dict[str, Any]) -> BrandOverview:
        """Génère la section Brand Overview"""
        # Logique de génération avec IA
        return BrandOverview(
            brand_name=brief_data.get('brand_name', 'Unknown Brand'),
            description=brief_data.get('description', ''),
            positioning=brief_data.get('positioning', ''),
            target_persona=brief_data.get('target_persona', {{}}),
            brand_values=brief_data.get('brand_values', []),
            key_differentiators=brief_data.get('differentiators', []),
            market_position=veille_data.get('market_position', ''),
            brand_voice=brief_data.get('brand_voice', ''),
            visual_identity=brief_data.get('visual_identity', {{}})
        )
    
    def _generate_state_of_play(self, brief_data: Dict[str, Any], veille_data: Dict[str, Any], 
                               competitor_analysis: Dict[str, Any]) -> StateOfPlay:
        """Génère la section State of Play"""
        return StateOfPlay(
            market_context=veille_data.get('market_context', ''),
            client_audit=brief_data.get('client_audit', {{}}),
            benchmark_3_main=competitor_analysis.get('main_competitors', []),
            competitor_mapping=competitor_analysis.get('competitor_mapping', {{}}),
            market_trends=veille_data.get('market_trends', []),
            opportunities=veille_data.get('opportunities', []),
            threats=veille_data.get('threats', [])
        )
    
    def _generate_cultural_trend(self, trend_analysis: Dict[str, Any]) -> CulturalTrend:
        """Génère la section Cultural Trends"""
        cultural_data = trend_analysis.get('cultural_trends', {{}})
        return CulturalTrend(
            trend_name=cultural_data.get('trend_name', ''),
            trend_description=cultural_data.get('description', ''),
            cultural_context=cultural_data.get('context', ''),
            opportunity_description=cultural_data.get('opportunity', ''),
            brand_relevance=cultural_data.get('brand_relevance', ''),
            potential_impact=cultural_data.get('impact', ''),
            execution_concept=cultural_data.get('concept', ''),
            key_elements=cultural_data.get('elements', []),
            deliverables=cultural_data.get('deliverables', [])
        )
    
    def _generate_tiktok_trend(self, trend_analysis: Dict[str, Any]) -> TikTokTrend:
        """Génère la section TikTok Trends"""
        tiktok_data = trend_analysis.get('tiktok_trends', {{}})
        return TikTokTrend(
            trend_name=tiktok_data.get('trend_name', ''),
            trend_description=tiktok_data.get('description', ''),
            virality_score=tiktok_data.get('virality_score', 0.0),
            concept_description=tiktok_data.get('concept', ''),
            viral_elements=tiktok_data.get('viral_elements', []),
            content_strategy=tiktok_data.get('strategy', ''),
            target_audience=tiktok_data.get('audience', '')
        )
    
    def _generate_societal_trend(self, trend_analysis: Dict[str, Any]) -> SocietalTrend:
        """Génère la section Societal Trends"""
        societal_data = trend_analysis.get('societal_trends', {{}})
        return SocietalTrend(
            trend_name=societal_data.get('trend_name', ''),
            trend_description=societal_data.get('description', ''),
            societal_impact=societal_data.get('impact', ''),
            purpose_statement=societal_data.get('purpose', ''),
            social_impact=societal_data.get('social_impact', ''),
            brand_role=societal_data.get('brand_role', ''),
            purpose_alignment=societal_data.get('alignment', '')
        )
    
    def _generate_timeline(self, brief_data: Dict[str, Any]) -> Timeline:
        """Génère la section Timeline"""
        return Timeline(
            phases=brief_data.get('phases', []),
            milestones=brief_data.get('milestones', []),
            deliverables=brief_data.get('deliverables', [])
        )
    
    def _generate_budget(self, brief_data: Dict[str, Any]) -> Budget:
        """Génère la section Budget"""
        return Budget(
            total_budget=brief_data.get('total_budget', 0.0),
            cost_breakdown=brief_data.get('cost_breakdown', {{}}),
            roi_projection=brief_data.get('roi_projection', {{}}),
            resource_allocation=brief_data.get('resource_allocation', {{}})
        )
'''
        
        with open("src/scout/livrables/generators/recommendation_generator.py", 'w', encoding='utf-8') as f:
            f.write(generator_content)
        
        print("  ✅ Générateur de recommandation mis à jour")
    
    def integrate_template(self):
        """Intègre le template dans l'architecture Scout"""
        print("🔗 Intégration du template dans l'architecture Scout...")
        
        # Sauvegarde
        self.backup_existing_files()
        
        # Chargement du template
        template = self.load_template()
        
        # Mise à jour des fichiers
        self.update_recommendation_models(template)
        self.update_recommendation_template(template)
        self.update_recommendation_generator(template)
        
        print("✅ Intégration terminée !")
        
        return template

def main():
    """Fonction principale"""
    integrator = ScoutTemplateIntegrator()
    template = integrator.integrate_template()
    
    print("\n" + "="*60)
    print("🎉 INTÉGRATION TERMINÉE")
    print("="*60)
    
    print(f"📋 Template: {template['name']}")
    print(f"📊 Slides totales: {template['total_slides']}")
    print(f"📁 Sections: {len(template['sections'])}")
    print(f"🎯 Sources de données: {', '.join(template['data_sources'])}")
    print(f"🤖 Config AI: {template['ai_config']['model']}")
    
    print("\n📁 Fichiers mis à jour:")
    print("  ✅ src/scout/data/recommendation_models.py")
    print("  ✅ src/scout/livrables/templates/recommendation_template.py")
    print("  ✅ src/scout/livrables/generators/recommendation_generator.py")
    
    print("\n💾 Sauvegardes créées dans: backups/templates/")
    
    print("\n🚀 Prochaines étapes:")
    print("  1. Tester l'intégration avec pytest")
    print("  2. Valider les mappings data → slides")
    print("  3. Optimiser les prompts IA")
    print("  4. Déployer sur Slack/API")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main() 