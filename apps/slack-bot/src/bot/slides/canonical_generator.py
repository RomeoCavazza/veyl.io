"""
Générateur de Slides Canoniques - Version Refactorisée
Utilise des modules spécialisés pour éviter le spaghetti code
"""

import os
import logging
from typing import Dict, List
from datetime import datetime
import asyncio

from .data_preparation import PresentationDataPreparator
from .slide_generation import SlideGenerator
from .builder import SlideBuilder

logger = logging.getLogger(__name__)


class CanonicalSlideGenerator:
    """Générateur de slides utilisant les templates canoniques - Version refactorisée"""

    def __init__(self):
        # Utilisation des modules spécialisés
        self.data_preparator = PresentationDataPreparator()
        self.slide_generator = SlideGenerator()
        self.slide_builder = SlideBuilder()
    
    async def generate_canonical_presentation(
        self,
        presentation_data: Dict,
        output_format: str = 'pptx'
    ) -> str:
        """Génère une présentation complète basée sur les templates canoniques"""
        logger.info(f"📋 Generating canonical presentation for {presentation_data.get('brand_name', 'Unknown')}")

        try:
            # Simulation de détection de style (pour MVP)
            style = {'name': 'modern', 'colors': ['#2C3E50', '#3498DB']}

            # Utilisation du module de préparation des données
            processed_data = self.data_preparator.prepare_presentation_data(presentation_data, style)

            # Utilisation du module de génération des slides
            slides = await self.slide_generator.generate_slides(processed_data, style)

            # Création de la présentation
            presentation_path = await self._create_presentation(slides, presentation_data, output_format)

            logger.info(f"✅ Canonical presentation generated: {presentation_path}")
            return presentation_path

        except Exception as e:
            logger.error(f"❌ Error generating presentation: {e}")
            raise
    
    def _prepare_presentation_data(self, data: Dict, style: SlideStyle) -> Dict:
        """Prépare les données pour la génération - refactorisé pour réduire la complexité"""

        # Étape 1: Conversion du style guide
        style_guide = _convert_style_guide_object(data.get('style_guide', {}))

        # Étape 2: Initialisation des données traitées
        processed_data = _initialize_processed_data(data, style, style_guide)

        # Étape 3: Extraction des insights de veille
        _extract_veille_insights(self, processed_data, data.get('veille_data', {}))

        # Étape 4: Génération des éléments de présentation
        _generate_presentation_elements(self, processed_data)

        return processed_data

def _convert_style_guide_object(style_guide):
    """Convertit l'objet StyleGuide en dictionnaire"""
    if hasattr(style_guide, '__dict__'):
        return {
            'mood': getattr(style_guide, 'mood', 'Professional'),
            'primary_color': getattr(style_guide, 'primary_color', '#2C3E50'),
            'secondary_color': getattr(style_guide, 'secondary_color', '#34495E'),
            'accent_color': getattr(style_guide, 'accent_color', '#3498DB'),
            'background_color': getattr(style_guide, 'background_color', '#ECF0F1'),
            'visual_style': getattr(style_guide, 'visual_style', 'Modern')
        }
    return style_guide

def _initialize_processed_data(data: Dict, style: SlideStyle, style_guide) -> Dict:
    """Initialise les données traitées de base"""
    return {
        'brand_name': data.get('brand_name', 'Unknown Brand'),
        'sector': data.get('sector', 'general'),
        'project_type': data.get('project_type', 'campaign'),
        'target_audience': data.get('target_audience', 'general audience'),
        'brand_story': data.get('brand_story', ''),
        'core_values': data.get('core_values', []),
        'positioning': data.get('positioning', ''),
        'style': style.value,
        'style_guide': style_guide,
        'veille_data': data.get('veille_data', {}),
        'image_prompts': data.get('image_prompts', [])
    }

def _extract_veille_insights(generator, processed_data: Dict, veille_data: Dict):
    """Extrait les insights de veille"""
    if veille_data:
        processed_data.update({
            'market_insights': generator._extract_market_insights(veille_data),
            'competitive_landscape': generator._extract_competitive_landscape(veille_data),
            'consumer_trends': generator._extract_consumer_trends(veille_data),
            'opportunities': generator._extract_opportunities(veille_data)
        })

def _generate_presentation_elements(generator, processed_data: Dict):
    """Génère les éléments de présentation"""
    processed_data['priorities'] = generator._generate_strategic_priorities(processed_data)
    processed_data['ideas'] = generator._generate_ideas(processed_data)
    processed_data['timeline'] = generator._generate_timeline(processed_data)
    processed_data['budget'] = generator._generate_budget(processed_data)
    
    def _extract_market_insights(self, veille_data: Dict) -> str:
        """Extrait les insights de marché"""
        insights = veille_data.get('insights', [])
        if insights:
            return '; '.join([insight.get('insight', '') for insight in insights[:3]])
        return "Market analysis shows significant opportunities for growth and engagement."
    
    def _extract_competitive_landscape(self, veille_data: Dict) -> str:
        """Extrait l'analyse concurrentielle"""
        competitors = veille_data.get('competitors', [])
        if competitors:
            competitor_names = [comp.get('brand', '') for comp in competitors[:3]]
            return f"Key competitors include {', '.join(competitor_names)}."
        return "Competitive landscape analysis reveals opportunities for differentiation."
    
    def _extract_consumer_trends(self, veille_data: Dict) -> str:
        """Extrait les tendances consommateurs"""
        trends = veille_data.get('trends', [])
        if trends:
            trend_keywords = [trend.get('keyword', '') for trend in trends[:3]]
            return f"Emerging trends: {', '.join(trend_keywords)}."
        return "Consumer behavior analysis shows evolving preferences and needs."
    
    def _extract_opportunities(self, veille_data: Dict) -> str:
        """Extrait les opportunités"""
        market_data = veille_data.get('market_data', {})
        if market_data:
            growth_rate = market_data.get('growth_rate', 0)
            return f"Market growing at {growth_rate*100:.1f}% annually."
        return "Significant opportunities for market expansion and brand growth."
    
    def _generate_strategic_priorities(self, data: Dict) -> List[str]:
        """Génère les priorités stratégiques"""
        sector = data.get('sector', 'general')
        priorities_map = {
            'luxury': ["Increase brand awareness", "Drive consideration", "Generate leads", "Build community"],
            'tech': ["User acquisition", "Product adoption", "Retention", "Virality"],
            'fashion': ["Brand awareness", "Desire", "Purchase intent", "Loyalty"],
            'food': ["Trial", "Repeat purchase", "Recommendation", "Brand love"],
            'automotive': ["Awareness", "Consideration", "Test drive", "Purchase"],
            'general': ["Increase awareness", "Drive engagement", "Generate leads", "Build loyalty"]
        }
        return priorities_map.get(sector, priorities_map['general'])
    
    def _generate_ideas(self, data: Dict) -> List[Dict]:
        """Génère les idées créatives - refactorisé pour réduire la complexité"""
        brand_name = data.get('brand_name', 'Brand')

        # Import des templates séparés
        from .idea_templates import get_idea_templates, customize_template

        # Récupération et personnalisation des templates
        templates = get_idea_templates()
        ideas = []

        for template in templates:
            customized_idea = customize_template(template, brand_name)
            ideas.append(customized_idea)

        return ideas
    
    def _generate_timeline(self, data: Dict) -> Dict:
        """Génère le timeline"""
        return {
            'phases': [
                {
                    'phase': 'PHASE 1',
                    'name': 'PLANNING & PREPARATION',
                    'duration': '2-3 months',
                    'activities': ['Strategy development', 'Team assembly', 'Resource planning'],
                    'milestones': ['Strategy approved', 'Team in place', 'Budget allocated']
                },
                {
                    'phase': 'PHASE 2',
                    'name': 'EXECUTION & LAUNCH',
                    'duration': '3-4 months',
                    'activities': ['Creative development', 'Production', 'Launch campaign'],
                    'milestones': ['Creative approved', 'Production complete', 'Campaign live']
                },
                {
                    'phase': 'PHASE 3',
                    'name': 'OPTIMIZATION & SCALE',
                    'duration': '2-3 months',
                    'activities': ['Performance monitoring', 'Optimization', 'Scale successful elements'],
                    'milestones': ['KPIs met', 'Optimizations implemented', 'Scale plan ready']
                }
            ]
        }
    
    def _generate_budget(self, data: Dict) -> Dict:
        """Génère le budget"""
        total_budget = 500000  # Budget de base - peut être paramétré  # Budget de base
        return {
            'total_budget': f"€{total_budget:,}",
            'categories': [
                {
                    'category': 'CREATIVE & PRODUCTION',
                    'amount': f"€{total_budget * 0.4:,}",
                    'percentage': '40%',
                    'breakdown': ['Creative development', 'Production costs', 'Asset creation']
                },
                {
                    'category': 'MEDIA & DISTRIBUTION',
                    'amount': f"€{total_budget * 0.35:,}",
                    'percentage': '35%',
                    'breakdown': ['Paid media', 'Social advertising', 'Influencer partnerships']
                },
                {
                    'category': 'TECHNOLOGY & PLATFORMS',
                    'amount': f"€{total_budget * 0.15:,}",
                    'percentage': '15%',
                    'breakdown': ['Platform development', 'Analytics tools', 'Technical support']
                },
                {
                    'category': 'PARTNERSHIPS & ACTIVATIONS',
                    'amount': f"€{total_budget * 0.1:,}",
                    'percentage': '10%',
                    'breakdown': ['Event activations', 'Partnership fees', 'Contingency']
                }
            ]
        }
    
    async def _generate_slides(self, data: Dict, style: SlideStyle) -> List[Dict]:
        """Génère les slides individuelles"""
        slides = []
        
        # Slide 1: Cover
        slides.append(self._generate_cover_slide(data, style))
        
        # Slide 2: Strategic Priorities
        slides.append(self._generate_priorities_slide(data, style))
        
        # Slide 3: Sommaire
        slides.append(self._generate_sommaire_slide(data, style))
        
        # Slide 4: Brand Overview
        slides.append(self._generate_brand_overview_slide(data, style))
        
        # Slide 5: State of Play
        slides.append(self._generate_state_of_play_slide(data, style))
        
        # Slides 6-14: Ideas (3 ideas x 3 slides each)
        idea_slides = self._generate_idea_slides(data, style)
        slides.extend(idea_slides)
        
        # Slide 15: Timeline
        slides.append(self._generate_timeline_slide(data, style))
        
        # Slide 16: Budget
        slides.append(self._generate_budget_slide(data, style))
        
        return slides
    
    def _generate_cover_slide(self, data: Dict, style: SlideStyle) -> Dict:
        """Génère la slide de couverture"""
        self.templates.get('cover', {})
        return {
            'type': 'cover',
            'content': {
                'title': data.get('brand_name', 'Unknown Brand'),
                'subtitle': f"{data.get('project_type', 'Campaign')} Campaign",
                'agency': 'REVOLVR',
                'tagline': 'KILLING IT SINCE 2010'
            },
            'style': {
                'layout': 'centered_minimal',
                'primary_color': data.get('style_guide', {}).get('primary_color', '#2C3E50'),
                'secondary_color': data.get('style_guide', {}).get('secondary_color', '#34495E'),
                'accent_color': data.get('style_guide', {}).get('accent_color', '#3498DB'),
                'background_color': data.get('style_guide', {}).get('background_color', '#ECF0F1')
            }
        }
    
    def _generate_priorities_slide(self, data: Dict, style: SlideStyle) -> Dict:
        """Génère la slide des priorités stratégiques"""
        priorities = data.get('priorities', [])
        return {
            'type': 'strategic_priorities',
            'content': {
                'title': 'STRATEGIC PRIORITIES',
                'priorities': [
                    {'text': priority, 'icon': '🎯', 'color': '#2C3E50'} 
                    for priority in priorities
                ]
            },
            'style': {
                'layout': 'grid_2x2',
                'primary_color': data.get('style_guide', {}).get('primary_color', '#2C3E50')
            }
        }
    
    def _generate_sommaire_slide(self, data: Dict, style: SlideStyle) -> Dict:
        """Génère la slide de sommaire"""
        return {
            'type': 'sommaire',
            'content': {
                'title': 'SOMMAIRE',
                'sections': [
                    {'number': '01', 'title': 'BRAND OVERVIEW', 'subtitle': 'Understanding the brand'},
                    {'number': '02', 'title': 'STATE OF PLAY', 'subtitle': 'Market analysis & insights'},
                    {'number': '03', 'title': 'STRATEGIC IDEAS', 'subtitle': 'Creative concepts & execution'},
                    {'number': '04', 'title': 'PLANNING & BUDGET', 'subtitle': 'Timeline & investment'}
                ]
            },
            'style': {
                'layout': 'vertical_list',
                'primary_color': data.get('style_guide', {}).get('primary_color', '#2C3E50')
            }
        }
    
    def _generate_brand_overview_slide(self, data: Dict, style: SlideStyle) -> Dict:
        """Génère la slide de brand overview"""
        return {
            'type': 'brand_overview',
            'content': {
                'title': 'BRAND OVERVIEW',
                'brand_story': data.get('brand_story', ''),
                'core_values': data.get('core_values', []),
                'positioning': data.get('positioning', ''),
                'target_audience': data.get('target_audience', ''),
                'key_messages': ['Authenticity', 'Quality', 'Innovation']
            },
            'style': {
                'layout': 'two_columns',
                'primary_color': data.get('style_guide', {}).get('primary_color', '#2C3E50')
            }
        }
    
    def _generate_state_of_play_slide(self, data: Dict, style: SlideStyle) -> Dict:
        """Génère la slide de state of play"""
        return {
            'type': 'state_of_play',
            'content': {
                'title': 'STATE OF PLAY',
                'sections': [
                    {
                        'title': 'MARKET INSIGHTS',
                        'content': data.get('market_insights', ''),
                        'data_points': ['Market growth', 'Consumer trends', 'Competitive landscape']
                    },
                    {
                        'title': 'COMPETITIVE LANDSCAPE',
                        'content': data.get('competitive_landscape', ''),
                        'data_points': ['Key competitors', 'Market positioning', 'Differentiation opportunities']
                    },
                    {
                        'title': 'CONSUMER TRENDS',
                        'content': data.get('consumer_trends', ''),
                        'data_points': ['Behavioral shifts', 'Preferences', 'Needs']
                    },
                    {
                        'title': 'OPPORTUNITIES',
                        'content': data.get('opportunities', ''),
                        'data_points': ['Market gaps', 'Growth potential', 'Innovation areas']
                    }
                ]
            },
            'style': {
                'layout': 'grid_2x2',
                'primary_color': data.get('style_guide', {}).get('primary_color', '#2C3E50')
            }
        }
    
    def _generate_idea_slides(self, data: Dict, style: SlideStyle) -> List[Dict]:
        """Génère les slides d'idées - refactorisé pour réduire la complexité"""
        slides = []
        ideas = data.get('ideas', [])

        for i, idea in enumerate(ideas, 1):
            # Slide d'en-tête d'idée
            slides.append(_create_idea_header_slide(i, idea, data))

            # Slide d'exécution
            slides.append(_create_idea_execution_slide(i, idea, data))

            # Slide de résultats
            slides.append(_create_idea_results_slide(i, idea, data))

        return slides

def _create_idea_header_slide(idea_index: int, idea: Dict, data: Dict) -> Dict:
    """Crée la slide d'en-tête d'une idée"""
    return {
        'type': f'idea_{idea_index}_header',
        'content': {
            'title': f'IDEA {idea_index}',
            'concept_name': idea.get('name', ''),
            'trend_context': idea.get('trend', ''),
            'opportunity': idea.get('opportunity', '')
        },
        'style': _get_slide_style('centered_title', data)
    }

def _create_idea_execution_slide(idea_index: int, idea: Dict, data: Dict) -> Dict:
    """Crée la slide d'exécution d'une idée"""
    return {
        'type': f'idea_{idea_index}_execution',
        'content': {
            'title': 'EXECUTION',
            'implementation': idea.get('implementation', ''),
            'channels': idea.get('channels', []),
            'timeline': idea.get('timeline', ''),
            'resources': idea.get('resources', '')
        },
        'style': _get_slide_style('execution_details', data)
    }

def _create_idea_results_slide(idea_index: int, idea: Dict, data: Dict) -> Dict:
    """Crée la slide de résultats d'une idée"""
    return {
        'type': f'idea_{idea_index}_results',
        'content': {
            'title': 'EXPECTED RESULTS',
            'outcomes': idea.get('outcomes', []),
            'kpis': idea.get('kpis', []),
            'roi': idea.get('roi', '')
        },
        'style': _get_slide_style('results_kpis', data)
    }

def _get_slide_style(layout: str, data: Dict) -> Dict:
    """Récupère le style de base pour une slide"""
    return {
        'layout': layout,
        'primary_color': data.get('style_guide', {}).get('primary_color', '#2C3E50')
    }
    
    def _generate_timeline_slide(self, data: Dict, style: SlideStyle) -> Dict:
        """Génère la slide de timeline"""
        timeline = data.get('timeline', {})
        return {
            'type': 'timeline',
            'content': {
                'title': 'TIMELINE',
                'phases': timeline.get('phases', [])
            },
            'style': {
                'layout': 'horizontal_timeline',
                'primary_color': data.get('style_guide', {}).get('primary_color', '#2C3E50')
            }
        }
    
    def _generate_budget_slide(self, data: Dict, style: SlideStyle) -> Dict:
        """Génère la slide de budget"""
        budget = data.get('budget', {})
        return {
            'type': 'budget',
            'content': {
                'title': 'BUDGET',
                'total_budget': budget.get('total_budget', ''),
                'categories': budget.get('categories', [])
            },
            'style': {
                'layout': 'table',
                'primary_color': data.get('style_guide', {}).get('primary_color', '#2C3E50')
            }
        }
    
    async def _create_presentation(self, slides: List[Dict], data: Dict, output_format: str) -> str:
        """Crée la présentation finale"""
        try:
            if output_format.lower() == 'pptx':
                return await self._create_pptx_presentation(slides, data)
            elif output_format.lower() == 'google_slides':
                return await self._create_google_slides_presentation(slides, data)
            else:
                raise ValueError(f"Format non supporté: {output_format}")
        except Exception as e:
            print(f"❌ Erreur création présentation: {e}")
            raise
    
