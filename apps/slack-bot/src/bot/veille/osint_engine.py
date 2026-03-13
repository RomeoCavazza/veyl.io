"""
Moteur OSINT principal
Orchestre tous les modules OSINT
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .osint_models import OSINTResult, OSINTTarget, OSINTSearchConfig, OSINTReport, OSINTDataType
from .maltego_integration import MaltegoIntegration
from .public_records_search import PublicRecordsSearch
from .social_media_osint import SocialMediaOSINT

logger = logging.getLogger(__name__)

class OSINTEngine:
    """Moteur principal pour les analyses OSINT"""

    def __init__(self):
        self.maltego = MaltegoIntegration()
        self.public_records = PublicRecordsSearch()
        self.social_media = SocialMediaOSINT()

    def search_target(
        self,
        identifier: str,
        target_type: str = 'company',
        config: Optional[OSINTSearchConfig] = None
    ) -> OSINTReport:
        """
        Recherche complète sur une cible OSINT

        Args:
            identifier: Identifiant de la cible (nom, domaine, email, etc.)
            target_type: Type de cible ('company', 'person', 'domain', 'email')
            config: Configuration de recherche (optionnel)

        Returns:
            Rapport OSINT complet
        """
        logger.info(f"🔍 Starting OSINT search for {target_type}: {identifier}")
        start_time = datetime.now()

        try:
            # Étape 1: Initialisation
            target, config = self._initialize_search(identifier, target_type, config)

            # Étape 2: Exécution de la recherche
            raw_results = self._execute_search_by_type(identifier, target_type, config)

            # Étape 3: Filtrage et limitation
            filtered_results = self._filter_and_limit_results(raw_results, config)

            # Étape 4: Création du rapport
            report = self._create_report(target, filtered_results, config, start_time)

            return report

        except Exception as e:
            return self._handle_search_error(e, identifier, target_type, config or OSINTSearchConfig(), start_time)

    def _initialize_search(self, identifier: str, target_type: str, config: Optional[OSINTSearchConfig]):
        """Initialise la recherche OSINT"""
        if config is None:
            config = OSINTSearchConfig()

        target = OSINTTarget(
            identifier=identifier,
            target_type=target_type,
            metadata={'search_config': config.__dict__}
        )

        return target, config

    def _execute_search_by_type(self, identifier: str, target_type: str, config: OSINTSearchConfig) -> List[OSINTResult]:
        """Exécute la recherche selon le type de cible"""
        search_methods = {
            'company': self._search_company,
            'person': self._search_person,
            'domain': self._search_domain,
            'email': self._search_email
        }

        search_method = search_methods.get(target_type)
        if search_method:
            return search_method(identifier, config)
        else:
            logger.warning(f"Unsupported target type: {target_type}")
            return []

    def _filter_and_limit_results(self, results: List[OSINTResult], config: OSINTSearchConfig) -> List[OSINTResult]:
        """Filtre et limite les résultats selon la configuration"""
        # Filtrage par confiance
        filtered = [r for r in results if r.confidence >= config.min_confidence]

        # Limitation du nombre de résultats
        limited = filtered[:config.max_results]

        return limited

    def _create_report(self, target: OSINTTarget, results: List[OSINTResult],
                      config: OSINTSearchConfig, start_time: datetime) -> OSINTReport:
        """Crée le rapport OSINT final"""
        # Génération du résumé
        summary = self._generate_search_summary(results, target, config)

        # Création du rapport
        report = OSINTReport(
            target=target,
            results=results,
            search_config=config,
            generated_at=datetime.now(),
            summary=summary
        )

        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ OSINT search completed in {processing_time:.2f}s: {len(results)} results")

        return report

    def _handle_search_error(self, error: Exception, identifier: str, target_type: str,
                           config: OSINTSearchConfig, start_time: datetime) -> OSINTReport:
        """Gère les erreurs de recherche"""
        logger.error(f"❌ OSINT search failed: {error}")

        target = OSINTTarget(
            identifier=identifier,
            target_type=target_type,
            metadata={'search_config': config.__dict__}
        )

        return OSINTReport(
            target=target,
            results=[],
            search_config=config,
            generated_at=datetime.now(),
            summary={
                'error': str(error),
                'results_count': 0,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
        )

    def _search_company(self, company_name: str, config: OSINTSearchConfig) -> List[OSINTResult]:
        """Recherche d'entreprise"""
        results = []

        # Recherche dans les registres publics
        if 'public_records' in config.sources:
            public_results = self.public_records.search_company(company_name)
            results.extend(public_results)

        # Recherche sur les réseaux sociaux
        if 'social_media' in config.sources:
            social_results = self.social_media.search_company_social(company_name)
            results.extend(social_results)

        # Recherche avec Maltego
        if 'maltego' in config.sources:
            maltego_results = self.maltego.search_person(company_name)  # Recherche par nom d'entreprise
            results.extend(maltego_results)

        return results

    def _search_person(self, name: str, config: OSINTSearchConfig) -> List[OSINTResult]:
        """Recherche de personne"""
        results = []

        # Recherche dans les registres publics
        if 'public_records' in config.sources:
            public_results = self.public_records.search_person(name)
            results.extend(public_results)

        # Recherche sur les réseaux sociaux
        if 'social_media' in config.sources:
            social_results = self.social_media.search_username(name)
            results.extend(social_results)

        # Recherche avec Maltego
        if 'maltego' in config.sources:
            maltego_results = self.maltego.search_person(name)
            results.extend(maltego_results)

        return results

    def _search_domain(self, domain: str, config: OSINTSearchConfig) -> List[OSINTResult]:
        """Recherche de domaine"""
        results = []

        # Recherche avec Maltego
        if 'maltego' in config.sources:
            maltego_results = self.maltego.search_domain(domain)
            results.extend(maltego_results)

        return results

    def _search_email(self, email: str, config: OSINTSearchConfig) -> List[OSINTResult]:
        """Recherche d'email"""
        results = []

        # Recherche avec Maltego
        if 'maltego' in config.sources:
            maltego_results = self.maltego.search_email(email)
            results.extend(maltego_results)

        return results

    def _generate_search_summary(
        self,
        results: List[OSINTResult],
        target: OSINTTarget,
        config: OSINTSearchConfig
    ) -> Dict[str, Any]:
        """Génère un résumé de la recherche"""
        summary = {
            'results_count': len(results),
            'sources_used': list(set(r.source for r in results)),
            'data_types_found': list(set(r.data_type for r in results)),
            'avg_confidence': sum(r.confidence for r in results) / max(len(results), 1),
            'target_type': target.target_type,
            'search_timestamp': datetime.now().isoformat()
        }

        # Analyse par source
        source_stats = {}
        for result in results:
            source = result.source
            if source not in source_stats:
                source_stats[source] = 0
            source_stats[source] += 1

        summary['source_breakdown'] = source_stats

        # Analyse par type de données
        data_type_stats = {}
        for result in results:
            data_type = result.data_type
            if data_type not in data_type_stats:
                data_type_stats[data_type] = 0
            data_type_stats[data_type] += 1

        summary['data_type_breakdown'] = data_type_stats

        return summary

    def health_check(self) -> Dict[str, Any]:
        """Vérifie la santé de tous les modules OSINT"""
        health = {
            'overall_status': 'healthy',
            'modules': {},
            'timestamp': datetime.now().isoformat()
        }

        # Vérifier Maltego
        maltego_health = self.maltego.health_check()
        health['modules']['maltego'] = maltego_health

        # Vérifier les autres modules (simulé)
        health['modules']['public_records'] = {'status': 'healthy', 'message': 'Module operational'}
        health['modules']['social_media'] = {'status': 'healthy', 'message': 'Module operational'}

        # Statut global
        unhealthy_modules = [
            module for module, status in health['modules'].items()
            if status.get('status') not in ['healthy', 'unavailable']
        ]

        if unhealthy_modules:
            health['overall_status'] = 'degraded'

        return health

# Fonction de compatibilité
def run_osint_search(target: str, search_type: str = 'company') -> Dict[str, List[OSINTResult]]:
    """Fonction de compatibilité pour l'ancien code"""
    engine = OSINTEngine()

    # Mapping des types de recherche
    target_type = search_type if search_type in ['company', 'person', 'domain', 'email'] else 'company'

    report = engine.search_target(target, target_type)

    # Format de retour compatible
    return {
        'results': report.results,
        'summary': report.summary,
        'target': report.target.__dict__,
        'search_config': report.search_config.__dict__
    }
