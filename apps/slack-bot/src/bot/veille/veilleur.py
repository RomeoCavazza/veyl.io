"""
Module veilleur : récupération et analyse de veille concurrentielle.
Robuste, fonctionnel, avec gestion d'erreur stricte.
"""

import logging
import feedparser
import time
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from urllib.parse import urlparse

from ..ai.openai_client import get_ai_client, AIAnalysisResult

# Logger simple sans dépendance externe
logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter basique pour éviter la surcharge des APIs externes"""

    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.requests = []
        self.min_interval = 60.0 / requests_per_minute

    def wait_if_needed(self):
        """Attend si nécessaire pour respecter la limite de taux"""
        current_time = time.time()

        # Nettoyer les requêtes anciennes (> 1 minute)
        self.requests = [req_time for req_time in self.requests
                        if current_time - req_time < 60]

        if len(self.requests) >= self.requests_per_minute:
            # Attendre jusqu'à ce que la plus ancienne requête soit expirée
            wait_time = 60 - (current_time - self.requests[0])
            if wait_time > 0:
                logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
                time.sleep(wait_time)

        self.requests.append(current_time)

@dataclass
class Article:
    """Représentation standardisée d'un article."""
    title: str
    link: str
    description: str
    published_date: Optional[datetime] = None
    source: str = ""
    content: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'article en dictionnaire."""
        return {
            "title": self.title,
            "link": self.link,
            "description": self.description,
            "published_date": self.published_date.isoformat() if self.published_date else None,
            "source": self.source,
            "content": self.content,
            "tags": self.tags
        }

class VeilleError(Exception):
    """Exception pour les erreurs de veille."""
    pass

class Veilleur:
    """Veilleur concurrentiel robuste et fonctionnel."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le veilleur.

        Args:
            config: Configuration optionnelle
        """
        self.config = config or {}
        self.timeout = self.config.get("timeout", 30)
        self.max_articles = self.config.get("max_articles", 50)
        self.days_back = self.config.get("days_back", 7)
        self.ai_client = get_ai_client(mock=self.config.get("mock_ai", False))

        # Rate limiter pour éviter la surcharge des APIs
        self.rate_limiter = RateLimiter(requests_per_minute=self.config.get("requests_per_minute", 30))
        
    def fetch_rss_feeds(self, feed_urls: List[str]) -> List[Article]:
        """
        Récupère les articles depuis une liste de flux RSS.
        
        Args:
            feed_urls: Liste des URLs de flux RSS
            
        Returns:
            Liste d'articles récupérés
            
        Raises:
            VeilleError: Si erreur lors de la récupération
        """
        if not feed_urls:
            raise VeilleError("Aucune URL de flux fournie")
        
        all_articles = []
        cutoff_date = datetime.now() - timedelta(days=self.days_back)
        
        for url in feed_urls:
            try:
                # Respecter les limites de taux pour éviter la surcharge
                self.rate_limiter.wait_if_needed()

                logger.info(f"Récupération du flux RSS: {url}")
                articles = self._fetch_single_feed(url, cutoff_date)
                all_articles.extend(articles)
                logger.info(f"Récupéré {len(articles)} articles depuis {url}")
                
            except Exception as e:
                logger.error(f"Erreur lors de la récupération de {url}: {e}")
                continue
        
        # Trier par date et limiter
        all_articles.sort(key=lambda x: x.published_date or datetime.min, reverse=True)
        return all_articles[:self.max_articles]
    
    def _fetch_single_feed(self, url: str, cutoff_date: datetime) -> List[Article]:
        """Récupère les articles d'un seul flux RSS - refactorisé"""
        try:
            # Étape 1: Parsing du flux RSS
            feed_data = _parse_feed_source(url)
            if not feed_data:
                return []

            # Étape 2: Extraction des articles
            articles = []
            source_name = feed_data['feed'].feed.get("title", urlparse(url).netloc)

            for entry in feed_data['feed'].entries:
                try:
                    # Étape 3: Extraction et validation des données d'article
                    article_data = _extract_article_data(entry, cutoff_date)
                    if not article_data:
                        continue

                    # Étape 4: Création de l'objet Article
                    article = _create_article_object(article_data, source_name, entry)
                    articles.append(article)

                except Exception as e:
                    logger.error(f"Erreur lors du parsing d'un article: {e}")
                    continue

            return articles

        except Exception as e:
            return _handle_feed_error(url, e)

def _parse_feed_source(url: str) -> Optional[Dict[str, Any]]:
    """Parse le flux RSS source"""
    feed = feedparser.parse(url)

    if feed.bozo:
        logger.warning(f"Flux RSS malformé: {url}")

    if not hasattr(feed, 'entries') or not feed.entries:
        logger.warning(f"Aucun article trouvé dans le flux: {url}")
        return None

    return {'feed': feed}

def _extract_article_data(entry: Any, cutoff_date: datetime) -> Optional[Dict[str, Any]]:
    """Extrait les données d'un article individuel"""
    # Extraire les données de base
    title = entry.get("title", "Sans titre")
    link = entry.get("link", "")
    description = entry.get("summary", "")

    # Parser la date
    published_date = _parse_article_date(entry)

    # Filtrer par date
    if published_date and published_date < cutoff_date:
        return None

    return {
        'title': title,
        'link': link,
        'description': description,
        'published_date': published_date
    }

def _parse_article_date(entry: Any) -> Optional[datetime]:
    """Parse la date de publication d'un article"""
    # Essayer différentes sources de date
    date_sources = [
        getattr(entry, "published_parsed", None),
        getattr(entry, "updated_parsed", None),
        entry.get("published_parsed"),
        entry.get("updated_parsed")
    ]

    for date_source in date_sources:
        if date_source:
            try:
                return datetime(*date_source[:6])
            except (TypeError, ValueError):
                continue

    return None

def _create_article_object(article_data: Dict[str, Any], source_name: str, entry: Any) -> Article:
    """Crée un objet Article à partir des données extraites"""
    return Article(
        title=article_data['title'],
        link=article_data['link'],
        description=article_data['description'],
        published_date=article_data['published_date'],
        source=source_name,
        content=article_data['description'],  # Pour l'instant, on utilise la description
        tags=entry.get("tags", [])
    )

def _handle_feed_error(url: str, error: Exception) -> List[Article]:
    """Gère les erreurs de récupération de flux"""
    logger.error(f"Erreur lors de la récupération du flux {url}: {error}")
    return []
    
    def extract_articles(self, raw_feed: Any) -> List[Article]:
        """
        Extrait les articles d'un flux brut (pour compatibilité).
        
        Args:
            raw_feed: Flux RSS brut
            
        Returns:
            Liste d'articles extraits
        """
        # Cette méthode est maintenue pour compatibilité
        # Elle délègue à _fetch_single_feed
        if hasattr(raw_feed, 'href'):
            return self._fetch_single_feed(raw_feed.href, datetime.now() - timedelta(days=self.days_back))
        else:
            return []
    
    async def analyze_articles(self, articles: List[Article]) -> AIAnalysisResult:
        """
        Analyse les articles pour extraire des insights.
        Utilise le service d'analyse unifié pour éviter la duplication.

        Args:
            articles: Liste d'articles à analyser

        Returns:
            Résultat d'analyse avec insights
        """
        if not articles:
            return AIAnalysisResult(
                success=False,
                error_message="Aucun article à analyser"
            )

        try:
            # Utiliser le service d'analyse unifié
            from src.services.analysis_service import get_analysis_service
            analysis_service = get_analysis_service()

            # Analyser chaque article individuellement
            analysis_results = []
            for article in articles:
                content_result = await analysis_service.analyze_content(article.content or article.title)
                analysis_results.append(content_result)

            # Générer des insights globaux
            combined_data = {
                'articles_count': len(articles),
                'sentiment_scores': [
                    r.data.get('sentiment', {}).get('vader_compound', 0)
                    for r in analysis_results if r.success and r.data
                ]
            }

            insights_result = await analysis_service.generate_insights(combined_data)

            # Convertir vers AIAnalysisResult pour compatibilité
            return AIAnalysisResult(
                success=True,
                insights=insights_result.insights or [],
                summary=f"Analyse de {len(articles)} articles terminée",
                processing_time=sum(r.processing_time for r in analysis_results)
            )

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des articles: {e}")
            return AIAnalysisResult(
                success=False,
                error_message=str(e)
            )
    
    async def run_veille(self, feed_urls: List[str]) -> Dict[str, Any]:
        """
        Exécute une veille complète.
        
        Args:
            feed_urls: Liste des URLs de flux RSS
            
        Returns:
            Résultat complet de la veille
        """
        start_time = datetime.now()
        
        try:
            # Récupérer les articles
            articles = self.fetch_rss_feeds(feed_urls)
            
            if not articles:
                return {
                    "success": False,
                    "error": "Aucun article récupéré",
                    "articles": [],
                    "analysis": None,
                    "processing_time": (datetime.now() - start_time).total_seconds()
                }
            
            # Analyser les articles
            analysis = await self.analyze_articles(articles)
            
            return {
                "success": True,
                "articles": [article.to_dict() for article in articles],
                "analysis": analysis.to_dict() if analysis.success else None,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "article_count": len(articles)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la veille: {e}")
            return {
                "success": False,
                "error": str(e),
                "articles": [],
                "analysis": None,
                "processing_time": (datetime.now() - start_time).total_seconds()
            }

# Toutes les fonctions de compatibilité ont été supprimées
# Utiliser directement les méthodes de classe : Veilleur().fetch_rss_feeds(), etc.
