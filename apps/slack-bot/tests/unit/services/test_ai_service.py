"""
Tests unitaires pour le service IA unifié
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.ai_service import (
    AIService,
    get_ai_service,
    AIRequest,
    AIResponse,
    AnalysisType
)


class TestAIService:
    """Tests pour le service IA unifié"""

    @pytest.fixture
    def ai_service(self):
        """Fixture pour le service IA"""
        return get_ai_service()

    @pytest.mark.asyncio
    async def test_analyze_sentiment_type(self, ai_service):
        """Test analyse de sentiment via service IA"""
        request = AIRequest(
            content="This is great!",
            analysis_type=AnalysisType.SENTIMENT
        )

        with patch.object(ai_service, '_call_ai', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = AIResponse(
                success=True,
                content='{"overall_sentiment": "positive"}',
                structured_data={'overall_sentiment': 'positive'},
                model_used='gpt-4'
            )

            result = await ai_service.analyze(request)

            assert result.success is True
            assert result.structured_data['overall_sentiment'] == 'positive'
            mock_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_trends_type(self, ai_service):
        """Test analyse de tendances via service IA"""
        request = AIRequest(
            content="AI is great",
            analysis_type=AnalysisType.TRENDS
        )

        with patch.object(ai_service, '_call_ai', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = AIResponse(
                success=True,
                structured_data={'trends': [{'keyword': 'AI', 'frequency': 1}]}
            )

            result = await ai_service.analyze(request)

            assert result.success is True
            assert 'trends' in result.structured_data
            mock_call.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_unknown_type(self, ai_service):
        """Test type d'analyse inconnu"""
        request = AIRequest(
            content="test",
            analysis_type="unknown_type"  # Type invalide
        )

        result = await ai_service.analyze(request)

        assert result.success is False
        assert "non supporté" in result.error_message

    @pytest.mark.asyncio
    async def test_call_ai_with_openai_client(self, ai_service):
        """Test appel IA avec client OpenAI"""
        with patch.object(ai_service, 'openai_client') as mock_client:
            mock_client._call_openai.return_value = "Test response"

            result = await ai_service._call_ai("test prompt", "test_analysis")

            assert result.success is True
            assert result.content == "Test response"
            assert result.model_used == 'gpt-4-turbo-preview'

    @pytest.mark.asyncio
    async def test_call_ai_mock_mode(self, ai_service):
        """Test appel IA en mode mock"""
        ai_service.openai_client = None  # Simuler absence de client

        result = await ai_service._call_ai("test prompt", "test_analysis")

        assert result.success is True
        assert "Mock response" in result.content
        assert result.model_used == 'mock'

    @pytest.mark.asyncio
    async def test_call_ai_json_parsing(self, ai_service):
        """Test parsing JSON dans la réponse IA"""
        with patch.object(ai_service, 'openai_client') as mock_client:
            mock_client._call_openai.return_value = '{"test": "value"}'

            result = await ai_service._call_ai("test prompt", "test_analysis")

            assert result.success is True
            assert result.structured_data == {'test': 'value'}

    @pytest.mark.asyncio
    async def test_singleton_pattern(self):
        """Test que get_ai_service retourne toujours la même instance"""
        service1 = get_ai_service()
        service2 = get_ai_service()

        assert service1 is service2


class TestAIRequest:
    """Tests pour AIRequest"""

    def test_ai_request_creation(self):
        """Test création d'AIRequest"""
        request = AIRequest(
            content="test content",
            analysis_type=AnalysisType.SENTIMENT,
            context={'test': 'context'}
        )

        assert request.content == "test content"
        assert request.analysis_type == AnalysisType.SENTIMENT
        assert request.context == {'test': 'context'}
        assert request.timestamp is not None


class TestAIResponse:
    """Tests pour AIResponse"""

    def test_ai_response_creation(self):
        """Test création d'AIResponse"""
        response = AIResponse(
            success=True,
            content="test content",
            confidence=0.9,
            model_used='gpt-4'
        )

        assert response.success is True
        assert response.content == "test content"
        assert response.confidence == 0.9
        assert response.model_used == 'gpt-4'
        assert response.timestamp is not None

    def test_ai_response_defaults(self):
        """Test valeurs par défaut d'AIResponse"""
        response = AIResponse(success=False)

        assert response.success is False
        assert response.content is None
        assert response.structured_data is None
        assert response.confidence == 0.0
        assert response.error_message is None
        assert response.processing_time == 0.0


class TestAnalysisType:
    """Tests pour AnalysisType enum"""

    def test_analysis_type_values(self):
        """Test valeurs de l'enum AnalysisType"""
        assert AnalysisType.SENTIMENT.value == "sentiment"
        assert AnalysisType.TRENDS.value == "trends"
        assert AnalysisType.CONTENT.value == "content"
        assert AnalysisType.BRIEF.value == "brief"
        assert AnalysisType.VEILLE.value == "veille"
        assert AnalysisType.PRESENTATION.value == "presentation"
        assert AnalysisType.SLACK_RESPONSE.value == "slack_response"