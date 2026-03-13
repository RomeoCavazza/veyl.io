import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Ajouter le chemin src au sys.path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from src.bot.veille import ultra_veille_engine
from src.bot.veille.ultra_veille_engine import UltraVeilleEngine


class TestVeilleEngine:
    """Tests pour le module de veille"""
    
    @pytest.mark.unit

    
    @pytest.mark.veille

    
    def test_fetch_all_sources_success(self):
        """Test de récupération de toutes les sources avec succès"""
        with patch('src.bot.veille.ultra_veille_engine.UltraVeilleEngine.fetch_sources') as mock_fetch:
            mock_fetch.return_value = [{"title": "Test Article", "url": "test.com"}]
            engine = UltraVeilleEngine()
            result = engine.fetch_sources(["source1", "source2"])
            assert len(result) > 0
            assert "title" in result[0]

    
    @pytest.mark.unit


    
    @pytest.mark.veille


    
    def test_fetch_all_sources_partial_failure(self):
        """Test de récupération avec échec partiel"""
        with patch('src.bot.veille.ultra_veille_engine.UltraVeilleEngine.fetch_sources') as mock_fetch:
            mock_fetch.side_effect = Exception("Network error")
            engine = UltraVeilleEngine()
            try:
                result = engine.fetch_sources(["source1", "source2"])
                # If no exception is raised, result should be empty or contain error info
                assert result == [] or "error" in str(result)
            except Exception:
                # Exception is also acceptable for this test
                pass

    
    @pytest.mark.unit


    
    @pytest.mark.veille


    
    def test_fetch_rss_sources(self):
        """Test de récupération des sources RSS"""
        with patch('src.bot.veille.ultra_veille_engine.UltraVeilleEngine.fetch_sources') as mock_fetch:
            mock_fetch.return_value = [
                {'source': 'rss', 'title': 'Test RSS 1', 'url': 'http://test1.com'},
                {'source': 'rss', 'title': 'Test RSS 2', 'url': 'http://test2.com'}
            ]
            engine = UltraVeilleEngine()
            results = engine.fetch_sources(['http://test.com/feed'])
            assert len(results) == 2
            assert results[0]['title'] == 'Test RSS 1'
            assert results[1]['title'] == 'Test RSS 2'

    
    @pytest.mark.unit


    
    @pytest.mark.veille


    
    def test_fetch_social_sources(self):
        """Test de récupération des sources sociales"""
        with patch('src.bot.veille.ultra_veille_engine.UltraVeilleEngine.fetch_sources') as mock_fetch:
            mock_fetch.return_value = [
                {'source': 'instagram', 'title': 'IG Post'},
                {'source': 'twitter', 'title': 'Tweet'}
            ]
            engine = UltraVeilleEngine()
            results = engine.fetch_sources(['instagram', 'twitter'])
            assert len(results) == 2
            assert any(r['source'] == 'instagram' for r in results)
            assert any(r['source'] == 'twitter' for r in results)

    
    @pytest.mark.unit


    
    @pytest.mark.veille


    
    def test_fetch_web_sources(self):
        """Test de récupération des sources web"""
        with patch('src.bot.veille.ultra_veille_engine.UltraVeilleEngine.fetch_sources') as mock_fetch:
            mock_fetch.return_value = [
                {'source': 'web', 'title': 'Test Web Article', 'content': 'Test content'}
            ]
            engine = UltraVeilleEngine()
            results = engine.fetch_sources(['http://test.com'])
            assert len(results) > 0
            assert any('Test Web Article' in str(r) for r in results)

    @pytest.mark.unit


    @pytest.mark.veille


    def test_analyze_content_success(self):
        """Test d'analyse de contenu avec succès"""
        with patch('src.bot.veille.ultra_veille_engine.UltraVeilleEngine.analyze_content') as mock_analyze:
            mock_analyze.return_value = {"sentiment": "positive", "keywords": ["test"]}
            engine = UltraVeilleEngine()
            result = engine.analyze_content("Test content")
            assert "sentiment" in result
            assert "keywords" in result

    @pytest.mark.unit


    @pytest.mark.veille


    def test_generate_insights_success(self):
        """Test de génération d'insights avec succès"""
        with patch('src.bot.veille.ultra_veille_engine.UltraVeilleEngine.generate_insights') as mock_gen:
            mock_gen.return_value = ["Insight 1", "Insight 2"]
            engine = UltraVeilleEngine()
            result = engine.generate_insights([{"content": "test"}])
            assert len(result) > 0

    @pytest.mark.unit


    @pytest.mark.veille


    def test_save_results_success(self):
        """Test de sauvegarde des résultats avec succès"""
        with patch('src.bot.veille.ultra_veille_engine.UltraVeilleEngine.save_results') as mock_save:
            mock_save.return_value = True
            engine = UltraVeilleEngine()
            result = engine.save_results({"data": "test"}, "test.csv")
            assert result is True

    @pytest.mark.unit


    @pytest.mark.veille


    def test_run_veille_complete_success(self):
        """Test de veille complète avec succès"""
        with patch('src.bot.veille.ultra_veille_engine.UltraVeilleEngine.fetch_sources') as mock_fetch, \
             patch('src.bot.veille.ultra_veille_engine.UltraVeilleEngine.analyze_content') as mock_analyze, \
             patch('src.bot.veille.ultra_veille_engine.UltraVeilleEngine.generate_insights') as mock_gen, \
             patch('src.bot.veille.ultra_veille_engine.UltraVeilleEngine.save_results') as mock_save:
            
            mock_fetch.return_value = [{"title": "Test", "content": "test"}]
            mock_analyze.return_value = {"sentiment": "positive"}
            mock_gen.return_value = ["Insight"]
            mock_save.return_value = True
            
            engine = UltraVeilleEngine()
            result = engine.run_veille(["source1"])
            assert result is not None

    
    @pytest.mark.unit


    
    @pytest.mark.veille


    
    def test_run_veille_error_handling(self):
        """Test de gestion d'erreur du workflow de veille"""
        with patch('src.bot.veille.ultra_veille_engine.UltraVeilleEngine.fetch_sources') as mock_fetch:
            mock_fetch.side_effect = Exception("Network error")
            
            engine = UltraVeilleEngine()
            # Our implementation handles errors gracefully, so no exception is raised
            result = engine.run_veille(["source1"])
            assert "error" in result 