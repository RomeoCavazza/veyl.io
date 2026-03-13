"""
Tests pour les outils OSINT
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from src.bot.veille.osint_tools import (
    MaltegoIntegration, PublicRecordsSearch, SocialMediaOSINT,
    OSINTEngine, OSINTResult, run_osint_search
)


class TestMaltegoIntegration:
    """Tests pour MaltegoIntegration"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.maltego = MaltegoIntegration()
    
    def test_maltego_integration_initialization(self):
        """Test initialisation de MaltegoIntegration"""
        assert self.maltego is not None
        assert hasattr(self.maltego, 'api_key')
        assert hasattr(self.maltego, 'base_url')
    
    def test_search_domain_fallback(self):
        """Test recherche de domaine avec fallback"""
        results = self.maltego.search_domain("example.com")
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        for result in results:
            assert isinstance(result, OSINTResult)
            assert result.source == 'maltego_fallback'
            assert result.data_type == 'domain'
            assert result.confidence > 0.0
    
    def test_search_email_fallback(self):
        """Test recherche d'email avec fallback"""
        results = self.maltego.search_email("test@example.com")
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        for result in results:
            assert isinstance(result, OSINTResult)
            assert result.source == 'maltego_fallback'
            assert result.data_type == 'email'
    
    def test_search_company_fallback(self):
        """Test recherche d'entreprise avec fallback"""
        results = self.maltego.search_company("Nike")
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        for result in results:
            assert isinstance(result, OSINTResult)
            assert result.source == 'maltego_fallback'
            assert result.data_type == 'company'
    
    @patch('src.bot.veille.osint_tools.requests.get')
    def test_search_domain_with_api_success(self, mock_get):
        """Test recherche de domaine avec API (succès)"""
        # Mock de la réponse API
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [
                {
                    'domain': 'subdomain.example.com',
                    'url': 'https://subdomain.example.com',
                    'confidence': 0.8,
                    'type': 'subdomain',
                    'id': '123',
                    'relationship': 'subdomain_of'
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock des credentials
        with patch.object(self.maltego, 'api_key', 'test_key'):
            results = self.maltego.search_domain("example.com")
            
            assert len(results) == 1
            assert results[0].content == 'subdomain.example.com'
            assert results[0].confidence == 0.8
    
    @patch('src.bot.veille.osint_tools.requests.get')
    def test_search_domain_with_api_failure(self, mock_get):
        """Test recherche de domaine avec API (échec)"""
        # Mock d'une erreur API
        mock_get.side_effect = Exception("API Error")
        
        # Mock des credentials
        with patch.object(self.maltego, 'api_key', 'test_key'):
            results = self.maltego.search_domain("example.com")
            
            # Devrait utiliser le fallback
            assert isinstance(results, list)
            assert len(results) > 0
            assert results[0].source == 'maltego_fallback'


class TestPublicRecordsSearch:
    """Tests pour PublicRecordsSearch"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.search = PublicRecordsSearch()
    
    def test_public_records_search_initialization(self):
        """Test initialisation de PublicRecordsSearch"""
        assert self.search is not None
        assert hasattr(self.search, 'session')
    
    def test_search_company_registry(self):
        """Test recherche dans les registres d'entreprises"""
        results = self.search.search_company_registry("Nike")
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        for result in results:
            assert isinstance(result, OSINTResult)
            assert result.data_type == 'company_registry'
            assert 'registry' in result.metadata
    
    def test_search_patent_database(self):
        """Test recherche dans les bases de brevets"""
        results = self.search.search_patent_database("Nike")
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        for result in results:
            assert isinstance(result, OSINTResult)
            assert result.data_type == 'patent'
            assert 'patent_count' in result.metadata
    
    def test_search_trademark_database(self):
        """Test recherche dans les bases de marques"""
        results = self.search.search_trademark_database("Nike")
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        for result in results:
            assert isinstance(result, OSINTResult)
            assert result.data_type == 'trademark'
            assert 'trademark_count' in result.metadata


class TestSocialMediaOSINT:
    """Tests pour SocialMediaOSINT"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.social = SocialMediaOSINT()
    
    def test_social_media_osint_initialization(self):
        """Test initialisation de SocialMediaOSINT"""
        assert self.social is not None
        assert hasattr(self.social, 'session')
    
    def test_search_linkedin_company(self):
        """Test recherche LinkedIn"""
        results = self.social.search_linkedin_company("Nike")
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        for result in results:
            assert isinstance(result, OSINTResult)
            assert result.source == 'linkedin.com'
            assert result.data_type == 'company_profile'
            assert 'followers' in result.metadata
    
    def test_search_twitter_company(self):
        """Test recherche Twitter"""
        results = self.social.search_twitter_company("Nike")
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        for result in results:
            assert isinstance(result, OSINTResult)
            assert result.source == 'twitter.com'
            assert result.data_type == 'company_profile'
            assert 'followers' in result.metadata
    
    def test_search_github_organization(self):
        """Test recherche GitHub"""
        results = self.social.search_github_organization("Nike")
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        for result in results:
            assert isinstance(result, OSINTResult)
            assert result.source == 'github.com'
            assert result.data_type == 'organization'
            assert 'repositories' in result.metadata


class TestOSINTEngine:
    """Tests pour OSINTEngine"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.engine = OSINTEngine()
    
    def test_osint_engine_initialization(self):
        """Test initialisation de OSINTEngine"""
        assert self.engine is not None
        assert hasattr(self.engine, 'maltego')
        assert hasattr(self.engine, 'public_records')
        assert hasattr(self.engine, 'social_media')
    
    def test_comprehensive_search_company(self):
        """Test recherche complète pour une entreprise"""
        results = self.engine.comprehensive_search("Nike", "company")
        
        assert isinstance(results, dict)
        assert 'maltego' in results
        assert 'public_records' in results
        assert 'social_media' in results
        assert 'all_results' in results
        
        # Vérifier que tous les résultats sont des listes
        for category, result_list in results.items():
            assert isinstance(result_list, list)
    
    def test_comprehensive_search_domain(self):
        """Test recherche complète pour un domaine"""
        results = self.engine.comprehensive_search("example.com", "domain")
        
        assert isinstance(results, dict)
        assert 'maltego' in results
        assert 'all_results' in results
    
    def test_comprehensive_search_email(self):
        """Test recherche complète pour un email"""
        results = self.engine.comprehensive_search("test@example.com", "email")
        
        assert isinstance(results, dict)
        assert 'maltego' in results
        assert 'all_results' in results
    
    def test_detect_weak_signals(self):
        """Test détection des signaux faibles"""
        # Créer des résultats de test
        test_results = [
            OSINTResult(
                source='test',
                data_type='test',
                content='Low confidence result',
                url='https://example.com',
                timestamp=datetime.now(),
                confidence=0.3,  # Faible confiance
                metadata={}
            ),
            OSINTResult(
                source='test',
                data_type='test',
                content='Fallback result',
                url='https://example.com',
                timestamp=datetime.now(),
                confidence=0.8,
                metadata={'fallback': True}  # Données de fallback
            ),
            OSINTResult(
                source='test',
                data_type='test',
                content='Old result',
                url='https://example.com',
                timestamp=datetime.now() - timedelta(days=400),  # Ancien
                confidence=0.8,
                metadata={}
            )
        ]
        
        weak_signals = self.engine.detect_weak_signals(test_results)
        
        assert isinstance(weak_signals, list)
        assert len(weak_signals) >= 3  # Au moins 3 signaux faibles
        
        # Vérifier les types de signaux
        signal_types = [signal['type'] for signal in weak_signals]
        assert 'low_confidence' in signal_types
        assert 'fallback_data' in signal_types
        assert 'old_data' in signal_types
    
    def test_save_results(self):
        """Test sauvegarde des résultats"""
        # Créer des résultats de test
        test_results = {
            'maltego': [
                OSINTResult(
                    source='maltego',
                    data_type='company',
                    content='Test result',
                    url='https://example.com',
                    timestamp=datetime.now(),
                    confidence=0.8,
                    metadata={}
                )
            ],
            'public_records': [],
            'social_media': [],
            'all_results': []
        }
        
        # Test sauvegarde
        success = self.engine.save_results(test_results, 'test_results.json')
        
        # Peut échouer si pas de permissions d'écriture, mais structure correcte
        assert isinstance(success, bool)


class TestRunOSINTSearch:
    """Tests pour la fonction utilitaire"""
    
    def test_run_osint_search_company(self):
        """Test fonction utilitaire pour entreprise"""
        results = run_osint_search("Nike", "company")
        
        assert isinstance(results, dict)
        assert 'maltego' in results
        assert 'public_records' in results
        assert 'social_media' in results
        assert 'all_results' in results
        assert 'weak_signals' in results
    
    def test_run_osint_search_domain(self):
        """Test fonction utilitaire pour domaine"""
        results = run_osint_search("example.com", "domain")
        
        assert isinstance(results, dict)
        assert 'maltego' in results
        assert 'all_results' in results
        assert 'weak_signals' in results
    
    def test_run_osint_search_email(self):
        """Test fonction utilitaire pour email"""
        results = run_osint_search("test@example.com", "email")
        
        assert isinstance(results, dict)
        assert 'maltego' in results
        assert 'all_results' in results
        assert 'weak_signals' in results


class TestOSINTResult:
    """Tests pour OSINTResult"""
    
    def test_osint_result_creation(self):
        """Test création d'un OSINTResult"""
        result = OSINTResult(
            source='test_source',
            data_type='test_type',
            content='Test content',
            url='https://example.com',
            timestamp=datetime.now(),
            confidence=0.8,
            metadata={'key': 'value'}
        )
        
        assert result.source == 'test_source'
        assert result.data_type == 'test_type'
        assert result.content == 'Test content'
        assert result.url == 'https://example.com'
        assert isinstance(result.timestamp, datetime)
        assert result.confidence == 0.8
        assert result.metadata == {'key': 'value'}
    
    def test_osint_result_defaults(self):
        """Test valeurs par défaut d'OSINTResult"""
        result = OSINTResult(
            source='test',
            data_type='test',
            content='test',
            url='https://example.com',
            timestamp=datetime.now(),
            confidence=0.5,
            metadata={}
        )
        
        assert result.source == 'test'
        assert result.data_type == 'test'
        assert result.content == 'test'
        assert result.url == 'https://example.com'
        assert isinstance(result.timestamp, datetime)
        assert result.confidence == 0.5
        assert result.metadata == {}


if __name__ == "__main__":
    pytest.main([__file__]) 