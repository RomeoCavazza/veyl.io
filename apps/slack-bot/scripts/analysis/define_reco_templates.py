#!/usr/bin/env python3
"""
Définition des templates de recommandation basée sur l'analyse Havana Club
Structure complète des 7 parties avec mappings data → slides
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class SlideTemplate:
    """Template pour une slide individuelle"""
    slide_type: str
    title: str
    subtitle: str = ""
    layout: str = "default"
    content_sections: List[str] = field(default_factory=list)
    visual_elements: List[str] = field(default_factory=list)
    data_mappings: Dict[str, str] = field(default_factory=dict)
    ai_prompts: List[str] = field(default_factory=list)

@dataclass
class RecommendationTemplate:
    """Template complet pour une recommandation"""
    name: str
    description: str
    total_slides: int
    sections: Dict[str, List[SlideTemplate]]
    data_sources: List[str]
    ai_config: Dict[str, Any]

class RecoTemplateBuilder:
    """Constructeur de templates de recommandation"""
    
    def __init__(self):
        self.templates = {}
    
    def build_havana_style_template(self) -> RecommendationTemplate:
        """Construit un template basé sur l'analyse Havana Club"""
        
        # 1. Brand Overview
        brand_overview_slides = [
            SlideTemplate(
                slide_type="cover",
                title="BRAND OVERVIEW",
                subtitle="{brand_name} - {year}",
                layout="centered_minimal",
                content_sections=["brand_intro", "brand_values", "target_persona"],
                visual_elements=["brand_logo", "hero_image"],
                data_mappings={
                    "brand_name": "brief.brand_name",
                    "year": "brief.year",
                    "brand_description": "veille.brand_analysis.description"
                },
                ai_prompts=[
                    "Analyse la marque {brand_name} et génère une vue d'ensemble",
                    "Définis les valeurs de marque principales",
                    "Crée un persona cible détaillé"
                ]
            ),
            SlideTemplate(
                slide_type="persona",
                title="TARGET PERSONA",
                subtitle="Understanding our audience",
                layout="persona_grid",
                content_sections=["persona_description", "behaviors", "motivations"],
                visual_elements=["persona_illustration", "behavior_icons"],
                data_mappings={
                    "persona_name": "analysis.target_persona.name",
                    "persona_description": "analysis.target_persona.description",
                    "behaviors": "analysis.target_persona.behaviors"
                },
                ai_prompts=[
                    "Crée un persona cible détaillé pour {brand_name}",
                    "Analyse les comportements et motivations de la cible"
                ]
            )
        ]
        
        # 2. State of Play
        state_of_play_slides = [
            SlideTemplate(
                slide_type="market_overview",
                title="STATE OF PLAY",
                subtitle="Market Context & Competitive Landscape",
                layout="two_columns",
                content_sections=["market_context", "key_insights", "opportunities"],
                visual_elements=["market_chart", "competitor_logos"],
                data_mappings={
                    "market_size": "veille.market_analysis.size",
                    "growth_rate": "veille.market_analysis.growth",
                    "key_players": "veille.competitor_analysis.top_players"
                },
                ai_prompts=[
                    "Analyse le contexte de marché pour {brand_name}",
                    "Identifie les opportunités principales"
                ]
            ),
            SlideTemplate(
                slide_type="competitor_benchmark",
                title="COMPETITOR BENCHMARK",
                subtitle="Top 3 Competitors Analysis",
                layout="competitor_grid",
                content_sections=["competitor_1", "competitor_2", "competitor_3"],
                visual_elements=["competitor_logos", "comparison_chart"],
                data_mappings={
                    "competitor_1": "veille.competitor_analysis.main_competitors[0]",
                    "competitor_2": "veille.competitor_analysis.main_competitors[1]",
                    "competitor_3": "veille.competitor_analysis.main_competitors[2]"
                },
                ai_prompts=[
                    "Analyse les 3 concurrents principaux de {brand_name}",
                    "Compare leurs stratégies et positionnements"
                ]
            )
        ]
        
        # 3. Idea #1. Cultural Trends
        cultural_trends_slides = [
            SlideTemplate(
                slide_type="trend_header",
                title="IDEA #1. CULTURAL TRENDS",
                subtitle="Cultural Opportunity",
                layout="section_header",
                content_sections=["trend_intro", "cultural_context"],
                visual_elements=["trend_visual", "cultural_icons"],
                data_mappings={
                    "trend_name": "veille.cultural_trends.main_trend.name",
                    "trend_description": "veille.cultural_trends.main_trend.description"
                },
                ai_prompts=[
                    "Identifie la tendance culturelle principale pour {brand_name}",
                    "Explique le contexte culturel de cette tendance"
                ]
            ),
            SlideTemplate(
                slide_type="trend_opportunity",
                title="THE OPPORTUNITY",
                subtitle="Why this matters for {brand_name}",
                layout="opportunity_layout",
                content_sections=["opportunity_description", "brand_relevance", "potential_impact"],
                visual_elements=["opportunity_visual", "impact_chart"],
                data_mappings={
                    "opportunity": "analysis.cultural_opportunity.description",
                    "brand_relevance": "analysis.cultural_opportunity.brand_fit",
                    "potential_impact": "analysis.cultural_opportunity.impact"
                },
                ai_prompts=[
                    "Définis l'opportunité culturelle pour {brand_name}",
                    "Explique la pertinence pour la marque"
                ]
            ),
            SlideTemplate(
                slide_type="trend_execution",
                title="THE EXECUTION",
                subtitle="How we bring this to life",
                layout="execution_grid",
                content_sections=["execution_concept", "key_elements", "deliverables"],
                visual_elements=["concept_visual", "execution_mockups"],
                data_mappings={
                    "concept": "ideas.cultural_trend.concept",
                    "key_elements": "ideas.cultural_trend.elements",
                    "deliverables": "ideas.cultural_trend.deliverables"
                },
                ai_prompts=[
                    "Crée le concept d'exécution pour la tendance culturelle",
                    "Définis les éléments clés et livrables"
                ]
            )
        ]
        
        # 4. Idea #2. TikTok Trends
        tiktok_trends_slides = [
            SlideTemplate(
                slide_type="trend_header",
                title="IDEA #2. TIKTOK TRENDS",
                subtitle="TikTok Opportunity",
                layout="section_header",
                content_sections=["tiktok_context", "trend_analysis"],
                visual_elements=["tiktok_logo", "trend_visuals"],
                data_mappings={
                    "tiktok_trend": "veille.tiktok_trends.main_trend.name",
                    "trend_virality": "veille.tiktok_trends.main_trend.virality_score"
                },
                ai_prompts=[
                    "Analyse les tendances TikTok pertinentes pour {brand_name}",
                    "Identifie l'opportunité TikTok principale"
                ]
            ),
            SlideTemplate(
                slide_type="tiktok_concept",
                title="TIKTOK CONCEPT",
                subtitle="Viral Strategy",
                layout="tiktok_layout",
                content_sections=["concept_description", "viral_elements", "content_strategy"],
                visual_elements=["tiktok_mockup", "content_examples"],
                data_mappings={
                    "concept": "ideas.tiktok_trend.concept",
                    "viral_elements": "ideas.tiktok_trend.viral_factors",
                    "content_plan": "ideas.tiktok_trend.content_strategy"
                },
                ai_prompts=[
                    "Crée un concept TikTok viral pour {brand_name}",
                    "Définis la stratégie de contenu TikTok"
                ]
            )
        ]
        
        # 5. Idea #3. Societal Trends
        societal_trends_slides = [
            SlideTemplate(
                slide_type="trend_header",
                title="IDEA #3. SOCIETAL TRENDS",
                subtitle="Societal Opportunity",
                layout="section_header",
                content_sections=["societal_context", "trend_impact"],
                visual_elements=["societal_visual", "impact_indicators"],
                data_mappings={
                    "societal_trend": "veille.societal_trends.main_trend.name",
                    "societal_impact": "veille.societal_trends.main_trend.impact"
                },
                ai_prompts=[
                    "Identifie la tendance sociétale principale pour {brand_name}",
                    "Analyse l'impact sociétal de cette tendance"
                ]
            ),
            SlideTemplate(
                slide_type="societal_concept",
                title="SOCIETAL CONCEPT",
                subtitle="Purpose-Driven Strategy",
                layout="purpose_layout",
                content_sections=["purpose_statement", "social_impact", "brand_role"],
                visual_elements=["purpose_visual", "impact_story"],
                data_mappings={
                    "purpose": "ideas.societal_trend.purpose",
                    "social_impact": "ideas.societal_trend.impact",
                    "brand_role": "ideas.societal_trend.brand_role"
                },
                ai_prompts=[
                    "Définis le concept sociétal pour {brand_name}",
                    "Crée une stratégie purpose-driven"
                ]
            )
        ]
        
        # 6. Timeline
        timeline_slides = [
            SlideTemplate(
                slide_type="timeline",
                title="TIMELINE",
                subtitle="Project Planning & Milestones",
                layout="horizontal_timeline",
                content_sections=["phases", "milestones", "deliverables"],
                visual_elements=["timeline_chart", "milestone_icons"],
                data_mappings={
                    "phases": "timeline.phases",
                    "milestones": "timeline.milestones",
                    "deliverables": "timeline.deliverables"
                },
                ai_prompts=[
                    "Crée un timeline détaillé pour la campagne {brand_name}",
                    "Définis les phases, milestones et livrables"
                ]
            )
        ]
        
        # 7. Budget
        budget_slides = [
            SlideTemplate(
                slide_type="budget",
                title="BUDGET",
                subtitle="Investment Breakdown",
                layout="budget_table",
                content_sections=["budget_overview", "cost_breakdown", "roi_projection"],
                visual_elements=["budget_chart", "roi_graph"],
                data_mappings={
                    "total_budget": "budget.total",
                    "cost_breakdown": "budget.breakdown",
                    "roi_projection": "budget.roi"
                },
                ai_prompts=[
                    "Définis le budget total pour la campagne {brand_name}",
                    "Crée le breakdown des coûts par activité"
                ]
            )
        ]
        
        # Construction du template complet
        template = RecommendationTemplate(
            name="Havana Style Recommendation",
            description="Template basé sur l'analyse Havana Club avec 7 parties structurées",
            total_slides=len(brand_overview_slides) + len(state_of_play_slides) + 
                        len(cultural_trends_slides) + len(tiktok_trends_slides) + 
                        len(societal_trends_slides) + len(timeline_slides) + len(budget_slides),
            sections={
                "1. Brand Overview": brand_overview_slides,
                "2. State of Play": state_of_play_slides,
                "3. Idea #1. Cultural Trends": cultural_trends_slides,
                "4. Idea #2. TikTok Trends": tiktok_trends_slides,
                "5. Idea #3. Societal Trends": societal_trends_slides,
                "6. Timeline": timeline_slides,
                "7. Budget": budget_slides
            },
            data_sources=[
                "brief_data",
                "veille_data", 
                "competitor_analysis",
                "trend_analysis",
                "market_research"
            ],
            ai_config={
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000,
                "prompt_template": "Tu es un expert en stratégie marketing. Analyse les données et génère du contenu pour {slide_type}."
            }
        )
        
        return template
    
    def save_template(self, template: RecommendationTemplate, filename: str = "reco_template_havana.json"):
        """Sauvegarde le template en JSON"""
        # Conversion en dict pour la sérialisation
        template_dict = {
            "name": template.name,
            "description": template.description,
            "total_slides": template.total_slides,
            "data_sources": template.data_sources,
            "ai_config": template.ai_config,
            "sections": {}
        }
        
        for section_name, slides in template.sections.items():
            template_dict["sections"][section_name] = []
            for slide in slides:
                slide_dict = {
                    "slide_type": slide.slide_type,
                    "title": slide.title,
                    "subtitle": slide.subtitle,
                    "layout": slide.layout,
                    "content_sections": slide.content_sections,
                    "visual_elements": slide.visual_elements,
                    "data_mappings": slide.data_mappings,
                    "ai_prompts": slide.ai_prompts
                }
                template_dict["sections"][section_name].append(slide_dict)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(template_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Template sauvegardé dans {filename}")
        return template_dict

def main():
    """Fonction principale"""
    builder = RecoTemplateBuilder()
    
    print("🏗️ Construction du template Havana Style...")
    template = builder.build_havana_style_template()
    
    print(f"✅ Template créé: {template.name}")
    print(f"📊 Total slides: {template.total_slides}")
    print(f"📋 Sections: {len(template.sections)}")
    
    # Sauvegarde
    template_dict = builder.save_template(template)
    
    # Affichage du résumé
    print("\n" + "="*60)
    print("📋 RÉSUMÉ DU TEMPLATE")
    print("="*60)
    
    for section_name, slides in template.sections.items():
        print(f"\n{section_name}:")
        for i, slide in enumerate(slides, 1):
            print(f"  {i}. {slide.slide_type} - {slide.title}")
            print(f"     Layout: {slide.layout}")
            print(f"     Mappings: {len(slide.data_mappings)}")
            print(f"     Prompts: {len(slide.ai_prompts)}")
    
    print(f"\n🎯 Sources de données: {', '.join(template.data_sources)}")
    print(f"🤖 Config AI: {template.ai_config['model']} (temp: {template.ai_config['temperature']})")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main() 