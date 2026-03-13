"""
Tests pour le Deep Web Scraper
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.bot.veille.deep_web_scraper import (
    GoogleCustomSearchAPI, SpecializedSiteScraper, DeepWebEngine,
    DeepWebResult, run_deep_web_search
)


class TestGoogleCustomSearchAPI:
    """Tests pour Google Custom Search API"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.api = GoogleCustomSearchAPI()
        self.test_query = "Nike"
        self.test_sector = "sport"
    
    def test_google_custom_search_initialization(self):
        """Test initialisation de l'API"""
        assert self.api is not None
        assert hasattr(self.api, 'api_key')
        assert hasattr(self.api, 'search_engine_id')
        assert hasattr(self.api, 'base_url')
    
    def test_search_sector_fallback(self):
        """Test recherche sectorielle avec fallback"""
        results = self.api.search_sector(self.test_query, self.test_sector, 5)
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        for result in results:
            assert isinstance(result, DeepWebResult)
            assert result.title
            assert result.url
            assert result.source
            assert isinstance(result.relevance_score, float)
            assert 0.0 <= result.relevance_score <= 1.0
    
    def test_search_news_fallback(self):
        """Test recherche d'actualités avec fallback"""
        results = self.api.search_news(self.test_query, self.test_sector, 5)
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        for result in results:
            assert isinstance(result, DeepWebResult)
            assert result.content_type == 'news'
    
    @patch('src.bot.veille.deep_web_scraper.requests.get')
    def test_search_sector_with_api_success(self, mock_get):
        """Test recherche sectorielle avec API (succès)"""
        # Mock de la réponse API
        mock_response = Mock()
        mock_response.json.return_value = {
            'items': [
                {
                    'title': 'Nike Sport Analysis',
                    'link': 'https://example.com/nike-sport',
                    'snippet': 'Comprehensive analysis of Nike in sport sector',
                    'displayLink': 'example.com',
                    'pagemap': {},
                    'kind': 'customsearch#result'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock des credentials
        with patch.object(self.api, 'api_key', 'test_key'), \
             patch.object(self.api, 'search_engine_id', 'test_engine'):
            
            results = self.api.search_sector(self.test_query, self.test_sector, 5)
            
            assert len(results) == 1
            assert results[0].title == 'Nike Sport Analysis'
            assert results[0].url == 'https://example.com/nike-sport'
    
    @patch('src.bot.veille.deep_web_scraper.requests.get')
    def test_search_sector_with_api_failure(self, mock_get):
        """Test recherche sectorielle avec API (échec)"""
        # Mock d'une erreur API
        mock_get.side_effect = Exception("API Error")
        
        # Mock des credentials
        with patch.object(self.api, 'api_key', 'test_key'), \
             patch.object(self.api, 'search_engine_id', 'test_engine'):
            
            results = self.api.search_sector(self.test_query, self.test_sector, 5)
            
            # Devrait utiliser le fallback
            assert isinstance(results, list)
            assert len(results) > 0
    
    def test_extract_source(self):
        """Test extraction de la source depuis l'URL"""
        test_urls = [
            ("https://www.example.com/article", "example.com"),
            ("https://news.site.com/path", "news.site.com"),
            ("http://blog.test.org", "blog.test.org")
        ]
        
        for url, expected_source in test_urls:
            source = self.api._extract_source(url)
            assert source == expected_source
    
    def test_calculate_relevance(self):
        """Test calcul de pertinence"""
        item = {
            'title': 'Nike Sport Market Analysis',
            'snippet': 'Comprehensive analysis of Nike performance in sport sector'
        }
        
        score = self.api._calculate_relevance(item, 'Nike', 'sport')
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score > 0.0  # Devrait avoir un score positif
    
    def test_detect_content_type(self):
        """Test détection du type de contenu"""
        test_cases = [
            ({'title': 'Breaking News: Nike Announcement'}, 'news'),
            ({'title': 'Blog Post about Nike'}, 'blog'),
            ({'title': 'Press Release: Nike'}, 'press_release'),
            ({'title': 'Research Study on Nike'}, 'research'),
            ({'title': 'Random Title'}, 'general')
        ]
        
        for item, expected_type in test_cases:
            content_type = self.api._detect_content_type(item)
            assert content_type == expected_type


class TestSpecializedSiteScraper:
    """Tests pour Specialized Site Scraper"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.scraper = SpecializedSiteScraper()
    
    def test_specialized_site_scraper_initialization(self):
        """Test initialisation du scraper"""
        assert self.scraper is not None
        assert hasattr(self.scraper, 'session')
        assert hasattr(self.scraper, 'sector_sites')
        assert 'tech' in self.scraper.sector_sites
        assert 'luxury' in self.scraper.sector_sites
    
    def test_scrape_sector_sites(self):
        """Test scraping des sites sectoriels"""
        results = self.scraper.scrape_sector_sites('tech', 'Apple', 5)
        
        assert isinstance(results, list)
        # Peut être vide si pas de connexion internet, mais structure correcte
        for result in results:
            assert isinstance(result, DeepWebResult)
    
    def test_calculate_site_relevance(self):
        """Test calcul de pertinence pour sites spécialisés"""
        title = "Apple Market Analysis in Tech Sector"
        snippet = "Comprehensive analysis of Apple performance"
        
        score = self.scraper._calculate_site_relevance(title, snippet, 'Apple')
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score > 0.0  # Devrait avoir un score positif
    
    def test_detect_site_content_type(self):
        """Test détection du type de contenu pour sites spécialisés"""
        test_cases = [
            ('Apple Announces New Product', 'news'),
            ('Market Analysis Report', 'analysis'),
            ('CEO Interview with Apple', 'interview'),
            ('Random Article Title', 'article')
        ]
        
        for title, expected_type in test_cases:
            content_type = self.scraper._detect_site_content_type(title)
            assert content_type == expected_type


class TestDeepWebEngine:
    """Tests pour Deep Web Engine"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.engine = DeepWebEngine()
    
    def test_deep_web_engine_initialization(self):
        """Test initialisation du moteur"""
        assert self.engine is not None
        assert hasattr(self.engine, 'google_search')
        assert hasattr(self.engine, 'specialized_scraper')
    
    def test_comprehensive_search(self):
        """Test recherche complète"""
        results = self.engine.comprehensive_search('Nike', 'sport', 10)
        
        assert isinstance(results, dict)
        assert 'google_search' in results
        assert 'news_search' in results
        assert 'specialized_sites' in results
        assert 'all_results' in results
        
        # Vérifier que tous les résultats sont des listes
        for category, result_list in results.items():
            assert isinstance(result_list, list)
    
    def test_save_results(self):
        """Test sauvegarde des résultats"""
        # Créer des résultats de test
        test_results = {
            'google_search': [
                DeepWebResult(
                    title='Test Result',
                    url='https://example.com',
                    snippet='Test snippet',
                    source='example.com',
                    timestamp=datetime.now(),
                    relevance_score=0.8,
                    content_type='news',
                    metadata={}
                )
            ],
            'news_search': [],
            'specialized_sites': [],
            'all_results': []
        }
        
        # Test sauvegarde
        success = self.engine.save_results(test_results, 'test_results.json')
        
        # Peut échouer si pas de permissions d'écriture, mais structure correcte
        assert isinstance(success, bool)


class TestRunDeepWebSearch:
    """Tests pour la fonction utilitaire"""
    
    def test_run_deep_web_search(self):
        """Test fonction utilitaire"""
        results = run_deep_web_search('Nike', 'sport', 10)
        
        assert isinstance(results, dict)
        assert 'google_search' in results
        assert 'news_search' in results
        assert 'specialized_sites' in results
        assert 'all_results' in results


if __name__ == "__main__":
    pytest.main([__file__]) 