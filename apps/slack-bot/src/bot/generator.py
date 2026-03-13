from typing import Dict, Any, List
from datetime import datetime
from src.utils.logger_v2 import logger

class Generator:
    """Classe pour la génération de recommandations à partir d'un brief."""

    def __init__(self):
        self.current_brief = None
        self.recommendations = None

    # Méthodes helper pour réduire la duplication
    def _get_section_safe(self, sections: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Récupère une section en toute sécurité"""
        return sections.get(key, default or [])

    def _create_action_template(self, description: str, priority: str = "haute",
                              impact: str = "fort", effort: str = "moyen") -> Dict[str, Any]:
        """Crée un template d'action standardisé"""
        return {
            "description": description,
            "priorite": priority,
            "impact": impact,
            "effort": effort
        }

    def _create_phase_action(self, phase: str, obj: str, index: int) -> Dict[str, Any]:
        """Crée une action pour une phase donnée"""
        return {
            "description": f"Action {phase.lower()} pour {obj}",
            "responsable": "À définir",
            "deadline": f"T{index}",
            "statut": "à faire"
        }
    
    def generate_recommendation(self, brief_data: Dict[str, Any]) -> Dict[str, Any]:
        """Génère des recommandations à partir des données du brief.

        Args:
            brief_data: Données du brief (texte extrait et sections)

        Returns:
            Dictionnaire contenant les recommandations générées
        """
        try:
            sections = brief_data.get("sections", {})

            # Validation optimisée avec helper
            required_sections = ["titre", "problème", "objectifs", "kpis"]
            missing_sections = [s for s in required_sections if not sections.get(s)]
            if missing_sections:
                raise ValueError(f"Sections manquantes : {', '.join(missing_sections)}")

            # Construction optimisée avec helpers
            objectifs = self._get_section_safe(sections, "objectifs")
            kpis = self._get_section_safe(sections, "kpis")

            recommendations = {
                "titre": sections["titre"],
                "date_generation": datetime.now().isoformat(),
                "contexte": {
                    "probleme": sections["problème"],
                    "objectifs": objectifs,
                    "kpis": kpis
                },
                "recommandations": self._generate_recommendations(sections),
                "plan_action": self._generate_action_plan(sections),
                "budget_estimation": self._estimate_budget(sections),
                "timeline": self._generate_timeline(sections)
            }

            self.recommendations = recommendations
            return recommendations

        except Exception as e:
            logger.error(f"[generator] Erreur génération recommandations : {e}")
            raise
    
    def _generate_recommendations(self, sections: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère la liste des recommandations avec helpers optimisés."""
        objectifs = self._get_section_safe(sections, "objectifs")
        kpis = self._get_section_safe(sections, "kpis")

        return [
            {
                "objectif": obj,
                "actions": [self._create_action_template(f"Action pour {obj}")],
                "kpis_associes": [
                    kpi for kpi in kpis
                    if any(k in kpi.lower() for k in obj.lower().split())
                ]
            }
            for obj in objectifs
        ]
    
    def _generate_action_plan(self, sections: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère le plan d'action avec helpers optimisés."""
        phases = ["Préparation", "Exécution", "Suivi"]
        objectifs = self._get_section_safe(sections, "objectifs")

        return [
            {
                "phase": phase,
                "ordre": i,
                "actions": [
                    self._create_phase_action(phase, obj, i)
                    for obj in objectifs
                ]
            }
            for i, phase in enumerate(phases, 1)
        ]
    
    def _estimate_budget(self, sections: Dict[str, Any]) -> Dict[str, Any]:
        """Estime le budget avec parsing optimisé."""
        # Parsing optimisé du budget
        budget_str = sections.get("budget", "").replace("€", "").strip()
        try:
            budget = float(budget_str) if budget_str else 0
        except ValueError:
            budget = 0

        # Calculs optimisés
        objectifs = self._get_section_safe(sections, "objectifs")
        nb_objectifs = len(objectifs)
        budget_par_objectif = budget / nb_objectifs if nb_objectifs > 0 else 0

        # Répartition standardisée
        repartition = {
            "preparation": budget * 0.2,
            "execution": budget * 0.6,
            "suivi": budget * 0.2
        }

        return {
            "total": budget,
            "repartition": repartition,
            "budget_par_objectif": budget_par_objectif
        }
    
    def _generate_timeline(self, sections: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère la timeline avec parsing optimisé et helpers."""
        # Phases standardisées avec durées relatives
        phases = [
            ("Lancement", 0.1),
            ("Préparation", 0.2),
            ("Exécution", 0.5),
            ("Suivi", 0.2)
        ]

        return [
            {
                "phase": phase,
                "duree_relative": duree,
                "jalons": [
                    {
                        "nom": f"Début {phase}",
                        "date": "À définir",
                        "livrables": [f"Livrable {phase} 1", f"Livrable {phase} 2"]
                    }
                ]
            }
            for phase, duree in phases
        ]
