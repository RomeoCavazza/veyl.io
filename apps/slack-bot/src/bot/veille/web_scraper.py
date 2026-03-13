
"""
Web Scraper spécialisé pour la veille concurrentielle
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WebScraper:
    """Scraper web avancé"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Revolver-AI-Bot/1.0 (+https://revolver-ai.com/bot)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def check_robots_txt(self, url: str) -> bool:
        """
        Vérifie si le scraping est autorisé par robots.txt

        Args:
            url: URL du site à vérifier

        Returns:
            True si le scraping est autorisé, False sinon
        """
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

            response = self.session.get(robots_url, timeout=5)
            if response.status_code == 200:
                robots_content = response.text
                # Vérifier si notre User-Agent est autorisé
                if "Revolver-AI-Bot" in robots_content:
                    return "Disallow" not in robots_content
                # Vérifier les règles générales
                return "Disallow: /" not in robots_content

        except Exception as e:
            logger.warning(f"Impossible de vérifier robots.txt pour {url}: {e}")
            # En cas d'erreur, on suppose que c'est autorisé (principe de précaution)
            return True

        return True

    def scrape_competitor_websites(self, competitors: List[str]) -> List[Dict]:
        """Scrape les sites des concurrents"""
        results = []

        for competitor in competitors:
            try:
                # Recherche du site officiel
                search_url = f"https://www.google.com/search?q={competitor}+official+website"
                response = self.session.get(search_url)
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extraire l'URL du premier résultat
                first_result = soup.find('a', href=True)
                if first_result:
                    website_url = first_result['href']

                    # Vérifier robots.txt avant scraping
                    if not self.check_robots_txt(website_url):
                        logger.warning(f"Scraping non autorisé pour {website_url} selon robots.txt")
                        continue

                    # Scraper le contenu du site
                    site_content = self._scrape_website_content(website_url)
                    results.append({
                        'competitor': competitor,
                        'website_url': website_url,
                        'content': site_content,
                        'timestamp': datetime.now().isoformat()
                    })

            except Exception as e:
                logger.error(f"Erreur scraping {competitor}: {e}")
                results.append({
                    'competitor': competitor,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })

        return results

    def _scrape_website_content(self, url: str) -> Dict[str, Any]:
        """Scrape le contenu d'un site web"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            return {
                'title': soup.title.string if soup.title else '',
                'meta_description': soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else '',
                'headings': [h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])],
                'paragraphs': [p.get_text() for p in soup.find_all('p')][:10],  # Limiter à 10 paragraphes
                'links': [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')][:20]  # Limiter à 20 liens
            }
        except Exception as e:
            logger.error(f"Erreur scraping contenu {url}: {e}")
            return {'error': str(e)}
