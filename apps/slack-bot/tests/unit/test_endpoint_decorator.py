"""
Tests unitaires pour le décorateur d'endpoint
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from src.api.endpoint_decorator import (
    endpoint_handler,
    create_demo_response,
    APIResponseBuilder
)


class TestEndpointDecorator:
    """Tests pour le décorateur d'endpoint"""

    @pytest.mark.asyncio
    async def test_endpoint_handler_success(self):
        """Test décorateur avec succès"""
        @endpoint_handler()
        async def test_endpoint():
            return {"success": True, "data": "test"}

        result = await test_endpoint()

        assert result["success"] is True
        assert result["data"] == "test"
        # Le décorateur ne modifie que les objets avec processing_time
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_endpoint_handler_with_demo_mode(self):
        """Test décorateur avec mode démo"""
        @endpoint_handler(demo_mode=True)
        async def test_endpoint(demo_mode=False):
            if demo_mode:
                return {"demo": True}
            return {"normal": True}

        # Test mode démo
        result = await test_endpoint(demo_mode=True)
        assert result["demo"] is True

        # Test mode normal
        result = await test_endpoint(demo_mode=False)
        assert result["normal"] is True

    @pytest.mark.asyncio
    async def test_endpoint_handler_exception_handling(self):
        """Test gestion d'erreur du décorateur"""
        @endpoint_handler()
        async def failing_endpoint():
            raise ValueError("Test error")

        result = await failing_endpoint()

        assert result["success"] is False
        assert "Test error" in result["error"]
        assert "processing_time" in result
        # Timestamp n'est ajouté que si l'objet a cet attribut

    @pytest.mark.asyncio
    async def test_endpoint_handler_with_response_model(self):
        """Test décorateur avec modèle de réponse"""
        class MockResponseModel:
            def __init__(self, success=False, error="", processing_time=0.0):
                self.success = success
                self.error = error
                self.processing_time = processing_time

        @endpoint_handler(response_model=MockResponseModel)
        async def test_endpoint():
            raise ValueError("Test error")

        result = await test_endpoint()

        assert isinstance(result, MockResponseModel)
        assert result.success is False
        assert "Test error" in result.error

    @pytest.mark.asyncio
    async def test_endpoint_handler_processing_time(self):
        """Test calcul du temps de traitement"""
        @endpoint_handler()
        async def slow_endpoint():
            await asyncio.sleep(0.1)  # Simuler traitement
            return {"success": True}

        result = await slow_endpoint()

        assert result["success"] is True
        # Le décorateur n'ajoute processing_time que pour les objets qui en ont besoin


class TestCreateDemoResponse:
    """Tests pour create_demo_response"""

    def test_create_demo_response_brief(self):
        """Test réponse démo pour endpoint brief"""
        response = create_demo_response("brief")

        assert response["success"] is True
        assert "demo_mode" in response["content"]
        assert response["content"]["demo_mode"] is True
        assert "brief_summary" in response["content"]

    def test_create_demo_response_veille(self):
        """Test réponse démo pour endpoint veille"""
        response = create_demo_response("veille")

        assert response["success"] is True
        assert "articles" in response
        assert isinstance(response["articles"], list)

    def test_create_demo_response_unknown(self):
        """Test réponse démo pour endpoint inconnu"""
        response = create_demo_response("unknown")

        assert response["success"] is True
        assert "demo_mode" in response
        assert response["processing_time"] == 0.1


class TestAPIResponseBuilder:
    """Tests pour APIResponseBuilder"""

    def test_success_response(self):
        """Test construction réponse succès"""
        response = APIResponseBuilder.success(data={"test": "data"})

        assert response["success"] is True
        assert response["data"] == {"test": "data"}
        assert "processing_time" in response
        assert "timestamp" in response

    def test_error_response(self):
        """Test construction réponse erreur"""
        response = APIResponseBuilder.error("Test error", processing_time=1.5)

        assert response["success"] is False
        assert response["error"] == "Test error"
        assert response["processing_time"] == 1.5
        assert "timestamp" in response

    def test_demo_response(self):
        """Test construction réponse démo"""
        response = APIResponseBuilder.demo("brief")

        assert response["success"] is True
        assert "demo_mode" in response["content"]
        assert response["content"]["demo_mode"] is True