"""
Intégration Maltego pour analyse OSINT
"""

import os
import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .osint_models import OSINTResult, OSINTDataType

logger = logging.getLogger(__name__)

class MaltegoIntegration:
    """Intégration avec Maltego pour analyse OSINT"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv('MALTEGO_API_KEY')
        self.base_url = base_url or os.getenv('MALTEGO_BASE_URL', 'https://api.maltego.com')

        if not self.api_key:
            logger.warning("⚠️ Maltego API non configurée - utilisation du mode fallback")

    def search_domain(self, domain: str) -> List[OSINTResult]:
        """Recherche d'informations sur un domaine"""
        try:
            if not self.api_key:
                return self._search_domain_fallback(domain)

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            # Recherche de domaines liés
            response = requests.get(
                f"{self.base_url}/domains/{domain}/related",
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return self._parse_maltego_domain_results(data, domain)
            else:
                logger.error(f"Maltego API error: {response.status_code}")
                return self._search_domain_fallback(domain)

        except Exception as e:
            logger.error(f"Domain search failed: {e}")
            return self._search_domain_fallback(domain)

    def search_person(self, name: str, company: Optional[str] = None) -> List[OSINTResult]:
        """Recherche d'informations sur une personne"""
        try:
            if not self.api_key:
                return self._search_person_fallback(name, company)

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {'name': name}
            if company:
                payload['company'] = company

            response = requests.post(
                f"{self.base_url}/persons/search",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return self._parse_maltego_person_results(data, name)
            else:
                return self._search_person_fallback(name, company)

        except Exception as e:
            logger.error(f"Person search failed: {e}")
            return self._search_person_fallback(name, company)

    def search_email(self, email: str) -> List[OSINTResult]:
        """Recherche d'informations sur un email"""
        try:
            if not self.api_key:
                return self._search_email_fallback(email)

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            response = requests.get(
                f"{self.base_url}/emails/{email}/info",
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return self._parse_maltego_email_results(data, email)
            else:
                return self._search_email_fallback(email)

        except Exception as e:
            logger.error(f"Email search failed: {e}")
            return self._search_email_fallback(email)

    # Méthodes privées pour le parsing des résultats Maltego
    def _parse_maltego_domain_results(self, data: Dict, domain: str) -> List[OSINTResult]:
        """Parse les résultats de recherche de domaine Maltego"""
        results = []

        for item in data.get('related_domains', []):
            result = OSINTResult(
                source="maltego",
                data_type=OSINTDataType.DOMAIN.value,
                content=f"Related domain: {item.get('domain', 'N/A')}",
                url=item.get('url', ''),
                timestamp=datetime.now(),
                confidence=item.get('confidence', 0.7),
                metadata=item
            )
            results.append(result)

        return results

    def _parse_maltego_person_results(self, data: Dict, name: str) -> List[OSINTResult]:
        """Parse les résultats de recherche de personne Maltego"""
        results = []

        for item in data.get('persons', []):
            result = OSINTResult(
                source="maltego",
                data_type=OSINTDataType.ADDRESS.value,
                content=f"Person info: {item.get('name', name)}",
                url=item.get('profile_url', ''),
                timestamp=datetime.now(),
                confidence=item.get('confidence', 0.6),
                metadata=item
            )
            results.append(result)

        return results

    def _parse_maltego_email_results(self, data: Dict, email: str) -> List[OSINTResult]:
        """Parse les résultats de recherche d'email Maltego"""
        results = []

        for item in data.get('email_info', []):
            result = OSINTResult(
                source="maltego",
                data_type=OSINTDataType.EMAIL.value,
                content=f"Email info: {email}",
                url=item.get('validation_url', ''),
                timestamp=datetime.now(),
                confidence=item.get('confidence', 0.8),
                metadata=item
            )
            results.append(result)

        return results

    # Méthodes de fallback quand Maltego n'est pas disponible
    def _search_domain_fallback(self, domain: str) -> List[OSINTResult]:
        """Recherche de domaine en mode fallback"""
        return [
            OSINTResult(
                source="fallback",
                data_type=OSINTDataType.DOMAIN.value,
                content=f"Domain analysis for {domain} (simulated)",
                url=f"https://{domain}",
                timestamp=datetime.now(),
                confidence=0.5,
                metadata={'fallback': True, 'domain': domain}
            )
        ]

    def _search_person_fallback(self, name: str, company: Optional[str] = None) -> List[OSINTResult]:
        """Recherche de personne en mode fallback"""
        content = f"Person search for {name}"
        if company:
            content += f" at {company}"

        return [
            OSINTResult(
                source="fallback",
                data_type=OSINTDataType.ADDRESS.value,
                content=f"{content} (simulated)",
                url="",
                timestamp=datetime.now(),
                confidence=0.4,
                metadata={'fallback': True, 'name': name, 'company': company}
            )
        ]

    def _search_email_fallback(self, email: str) -> List[OSINTResult]:
        """Recherche d'email en mode fallback"""
        return [
            OSINTResult(
                source="fallback",
                data_type=OSINTDataType.EMAIL.value,
                content=f"Email validation for {email} (simulated)",
                url="",
                timestamp=datetime.now(),
                confidence=0.6,
                metadata={'fallback': True, 'email': email}
            )
        ]

    def health_check(self) -> Dict[str, Any]:
        """Vérifie la santé de l'intégration Maltego"""
        if not self.api_key:
            return {
                'status': 'unavailable',
                'message': 'Maltego API key not configured',
                'fallback_mode': True
            }

        try:
            # Test de connectivité
            response = requests.get(
                f"{self.base_url}/health",
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=5
            )

            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'message': 'Maltego API is responding',
                    'fallback_mode': False
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': f'Maltego API returned {response.status_code}',
                    'fallback_mode': True
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Connection failed: {e}',
                'fallback_mode': True
            }
