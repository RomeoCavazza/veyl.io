"""
Génération des slides individuels
Crée chaque type de slide selon les templates canoniques
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SlideGenerator:
    """Génère les slides individuels"""

    def __init__(self):
        pass

    async def generate_slides(self, data: Dict, style: Any) -> List[Dict]:
        """Génère tous les slides de la présentation"""
        logger.info("🎨 Generating presentation slides")

        slides = []

        # Slide de couverture
        slides.append(self._generate_cover_slide(data, style))

        # Slide des priorités
        slides.append(self._generate_priorities_slide(data, style))

        # Slide du brief
        slides.append(self._generate_brief_slide(data, style))

        # Slide de veille
        slides.append(self._generate_veille_slide(data, style))

        # Slide des idées
        slides.append(self._generate_ideas_slide(data, style))

        # Slide du budget
        slides.append(self._generate_budget_slide(data, style))

        # Slide du calendrier
        slides.append(self._generate_timeline_slide(data, style))

        # Slide de conclusion
        slides.append(self._generate_conclusion_slide(data, style))

        logger.info(f"✅ Generated {len(slides)} slides")
        return slides

    def _generate_cover_slide(self, data: Dict, style: Any) -> Dict:
        """Génère le slide de couverture"""
        return {
            'type': 'cover',
            'title': data.get('brand_name', 'Présentation'),
            'subtitle': data.get('project_type', 'Projet Marketing'),
            'date': datetime.now().strftime('%d/%m/%Y'),
            'style': style,
            'layout': 'title_slide'
        }

    def _generate_priorities_slide(self, data: Dict, style: Any) -> Dict:
        """Génère le slide des priorités stratégiques"""
        return {
            'type': 'priorities',
            'title': 'Priorités Stratégiques',
            'content': data.get('strategic_priorities', []),
            'style': style,
            'layout': 'content_slide'
        }

    def _generate_brief_slide(self, data: Dict, style: Any) -> Dict:
        """Génère le slide du brief"""
        return {
            'type': 'brief',
            'title': 'Brief du Projet',
            'content': {
                'objectives': data.get('objectives', []),
                'target_audience': data.get('target_audience', ''),
                'challenges': data.get('challenges', [])
            },
            'style': style,
            'layout': 'content_slide'
        }

    def _generate_veille_slide(self, data: Dict, style: Any) -> Dict:
        """Génère le slide de veille"""
        return {
            'type': 'veille',
            'title': 'Analyse de Veille',
            'content': {
                'market_insights': data.get('market_insights', ''),
                'competitive_landscape': data.get('competitive_landscape', ''),
                'consumer_trends': data.get('consumer_trends', '')
            },
            'style': style,
            'layout': 'content_slide'
        }

    def _generate_ideas_slide(self, data: Dict, style: Any) -> Dict:
        """Génère le slide des idées"""
        return {
            'type': 'ideas',
            'title': 'Idées Créatives',
            'content': data.get('ideas', []),
            'style': style,
            'layout': 'content_slide'
        }

    def _generate_budget_slide(self, data: Dict, style: Any) -> Dict:
        """Génère le slide du budget"""
        budget = data.get('budget', 0)
        return {
            'type': 'budget',
            'title': 'Budget et Ressources',
            'content': {
                'total_budget': budget,
                'allocation': self._calculate_budget_allocation(budget)
            },
            'style': style,
            'layout': 'chart_slide'
        }

    def _generate_timeline_slide(self, data: Dict, style: Any) -> Dict:
        """Génère le slide du calendrier"""
        return {
            'type': 'timeline',
            'title': 'Calendrier du Projet',
            'content': {
                'timeline': data.get('timeline', ''),
                'milestones': self._generate_milestones(data)
            },
            'style': style,
            'layout': 'timeline_slide'
        }

    def _generate_conclusion_slide(self, data: Dict, style: Any) -> Dict:
        """Génère le slide de conclusion"""
        return {
            'type': 'conclusion',
            'title': 'Conclusion et Prochaines Étapes',
            'content': {
                'key_takeaways': self._extract_key_takeaways(data),
                'next_steps': ['Validation du concept', 'Développement', 'Lancement']
            },
            'style': style,
            'layout': 'content_slide'
        }

    def _calculate_budget_allocation(self, total_budget: float) -> Dict[str, float]:
        """Calcule l'allocation budgétaire"""
        if total_budget == 0:
            return {'production': 0, 'marketing': 0, 'other': 0}

        return {
            'production': total_budget * 0.4,
            'marketing': total_budget * 0.35,
            'other': total_budget * 0.25
        }

    def _generate_milestones(self, data: Dict) -> List[Dict]:
        """Génère les jalons du projet"""
        return [
            {'phase': 'Analyse', 'duration': '2 semaines'},
            {'phase': 'Conception', 'duration': '3 semaines'},
            {'phase': 'Développement', 'duration': '4 semaines'},
            {'phase': 'Tests & Lancement', 'duration': '2 semaines'}
        ]

    def _extract_key_takeaways(self, data: Dict) -> List[str]:
        """Extrait les points clés"""
        return [
            "Stratégie claire définie",
            "Opportunités identifiées",
            "Plan d'action établi"
        ]
