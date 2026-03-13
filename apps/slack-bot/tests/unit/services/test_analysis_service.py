"""
Tests unitaires pour le service d'analyse unifié
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.analysis_service import (
    AnalysisService,
    get_analysis_service,
    AnalysisResult,
    analyze_sentiment,
    analyze_trends,
    analyze_content,
    generate_insights
)


class TestAnalysisService:
    """Tests pour le service d'analyse unifié"""

    @pytest.fixture
    def analysis_service(self):
        """Fixture pour le service d'analyse"""
        return get_analysis_service()

    @pytest.mark.asyncio
    async def test_analyze_sentiment_success(self, analysis_service):
        """Test analyse de sentiment réussie"""
        text = "This is a great product! I love it!"

        result = await analysis_service.analyze_sentiment(text)

        assert result.success is True
        assert result.data is not None
        assert 'overall_sentiment' in result.data
        assert 'vader_compound' in result.data
        assert result.confidence > 0
        assert result.processing_time >= 0

    @pytest.mark.asyncio
    async def test_analyze_sentiment_empty_text(self, analysis_service):
        """Test analyse de sentiment avec texte vide"""
        result = await analysis_service.analyze_sentiment("")

        assert result.success is False
        assert "vide" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_analyze_trends_success(self, analysis_service):
        """Test analyse de tendances réussie"""
        texts = [
            "AI is the future of technology",
            "Machine learning is amazing",
            "Artificial intelligence will change everything"
        ]

        result = await analysis_service.analyze_trends(texts)

        assert result.success is True
        assert result.data is not None
        assert 'trends' in result.data
        assert isinstance(result.data['trends'], list)

    @pytest.mark.asyncio
    async def test_analyze_content_success(self, analysis_service):
        """Test analyse de contenu réussie"""
        content = "This is a sample content for analysis."

        result = await analysis_service.analyze_content(content)

        assert result.success is True
        assert result.data is not None
        assert 'word_count' in result.data
        assert 'char_count' in result.data

    @pytest.mark.asyncio
    async def test_generate_insights_success(self, analysis_service):
        """Test génération d'insights réussie"""
        data = {
            'sentiment': {'overall_sentiment': 'positive'},
            'trends': [{'keyword': 'test', 'frequency': 5, 'trending': True}]
        }

        result = await analysis_service.generate_insights(data)

        assert result.success is True
        assert result.data is not None
        assert 'insights' in result.data

    @pytest.mark.asyncio
    async def test_generate_insights_negative_sentiment(self, analysis_service):
        """Test génération d'insights avec sentiment négatif"""
        data = {
            'sentiment': {'overall_sentiment': 'negative'}
        }

        result = await analysis_service.generate_insights(data)

        assert result.success is True
        assert any("négatif" in insight.lower() for insight in result.insights)

    @pytest.mark.asyncio
    async def test_singleton_pattern(self):
        """Test que get_analysis_service retourne toujours la même instance"""
        service1 = get_analysis_service()
        service2 = get_analysis_service()

        assert service1 is service2


class TestAnalysisServiceFunctions:
    """Tests pour les fonctions de compatibilité"""

    @pytest.mark.asyncio
    async def test_analyze_sentiment_function(self):
        """Test fonction globale analyze_sentiment"""
        with patch('src.services.analysis_service.get_analysis_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.analyze_sentiment.return_value = AnalysisResult(
                success=True,
                data={'overall_sentiment': 'positive'},
                confidence=0.8
            )
            mock_get_service.return_value = mock_service

            result = await analyze_sentiment("test text")

            assert result.success is True
            assert result.data['overall_sentiment'] == 'positive'

    @pytest.mark.asyncio
    async def test_analyze_trends_function(self):
        """Test fonction globale analyze_trends"""
        with patch('src.services.analysis_service.get_analysis_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.analyze_trends.return_value = AnalysisResult(
                success=True,
                data={'trends': []}
            )
            mock_get_service.return_value = mock_service

            result = await analyze_trends(["test"])

            assert result.success is True
            assert 'trends' in result.data

    @pytest.mark.asyncio
    async def test_analyze_content_function(self):
        """Test fonction globale analyze_content"""
        with patch('src.services.analysis_service.get_analysis_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.analyze_content.return_value = AnalysisResult(
                success=True,
                data={'word_count': 5}
            )
            mock_get_service.return_value = mock_service

            result = await analyze_content("test content")

            assert result.success is True
            assert result.data['word_count'] == 5

    @pytest.mark.asyncio
    async def test_generate_insights_function(self):
        """Test fonction globale generate_insights"""
        with patch('src.services.analysis_service.get_analysis_service') as mock_get_service:
            mock_service = AsyncMock()
            mock_service.generate_insights.return_value = AnalysisResult(
                success=True,
                data={'insights': ['test insight']},
                insights=['test insight']
            )
            mock_get_service.return_value = mock_service

            result = await generate_insights({'test': 'data'})

            assert result.success is True
            assert 'test insight' in result.insights


class TestAnalysisResult:
    """Tests pour la classe AnalysisResult"""

    def test_analysis_result_creation(self):
        """Test création d'AnalysisResult"""
        result = AnalysisResult(
            success=True,
            data={'test': 'data'},
            confidence=0.9
        )

        assert result.success is True
        assert result.data == {'test': 'data'}
        assert result.confidence == 0.9
        assert result.timestamp is not None

    def test_analysis_result_defaults(self):
        """Test valeurs par défaut d'AnalysisResult"""
        result = AnalysisResult(success=False)

        assert result.success is False
        assert result.data is None
        assert result.insights is None
        assert result.confidence == 0.0
        assert result.error_message is None
        assert result.processing_time == 0.0