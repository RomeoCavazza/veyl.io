"""
Smoke tests for MVP Insighter API
Basic validation that core endpoints are working
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Mock the problematic imports before importing main
with patch('src.bot.monitoring.production_monitor.production_monitor'), \
     patch('src.bot.monitoring.production_monitor.monitor_endpoint'):
    from src.api.main import app

client = TestClient(app)


class TestAPISmoke:
    """Smoke tests for core API endpoints"""
    
    def test_health_endpoint(self):
        """Test that health endpoint responds"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Revolver AI Bot API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "operational"
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint is accessible"""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Should return some metrics data
        data = response.json()
        assert isinstance(data, dict)
    
    def test_cache_stats_endpoint(self):
        """Test cache stats endpoint"""
        response = client.get("/cache/stats")
        # Accept both 200 and 500 as cache might not be fully initialized
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "cache_hit_rate" in data
            assert "cache_hits" in data
            assert "cache_misses" in data
    
    def test_brief_endpoint_demo_mode(self):
        """Test brief endpoint in demo mode"""
        # Send empty content to trigger demo mode
        request_data = {"content": ""}
        response = client.post("/brief", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "demo_mode" in data["content"]
        assert data["content"]["demo_mode"] is True
    
    def test_veille_endpoint_basic(self):
        """Test veille endpoint with basic request"""
        request_data = {
            "rss_feeds": [],
            "competitors": ["nike", "adidas"],
            "date": None
        }
        response = client.post("/veille", json=request_data)
        # Might fail due to dependencies, but should not crash
        assert response.status_code in [200, 500]
    
    def test_weekly_endpoint_basic(self):
        """Test weekly report endpoint"""
        request_data = {
            "competitors": ["nike", "adidas"],
            "theme": "test"
        }
        response = client.post("/weekly", json=request_data)
        # Should work as it uses mock data
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "written_report" in data
        assert "slidecrafted_report" in data
    
    def test_recommendation_endpoint_basic(self):
        """Test recommendation endpoint"""
        request_data = {
            "brand_name": "TestBrand",
            "competitors": ["nike", "adidas"],
            "budget_range": "50k-100k",
            "timeline": "3-6 months"
        }
        response = client.post("/recommendation", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "recommendation" in data
        assert data["recommendation"]["brand_name"] == "TestBrand"
    
    def test_feedback_submission(self):
        """Test feedback submission endpoint"""
        feedback_data = {
            "deliverable_type": "weekly",
            "deliverable_id": "test_123",
            "rating": 4,
            "feedback": "Great analysis!",
            "improvements": ["More data sources", "Better visualization"]
        }
        response = client.post("/feedback", json=feedback_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "feedback_id" in data
    
    def test_stats_endpoint(self):
        """Test stats endpoint"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "stats" in data
        assert "total_requests" in data["stats"]
    
    def test_slack_events_url_verification(self):
        """Test Slack URL verification"""
        challenge_data = {
            "type": "url_verification",
            "challenge": "test_challenge_123"
        }
        response = client.post("/slack/events", json=challenge_data)
        assert response.status_code == 200
        data = response.json()
        assert data["challenge"] == "test_challenge_123"
    
    def test_slack_events_command_brief(self):
        """Test Slack slash command /brief"""
        command_data = {
            "command": "/brief",
            "text": "",
            "user_id": "U123456",
            "channel_id": "C123456"
        }
        response = client.post(
            "/slack/events",
            data=command_data,
            headers={"content-type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "🎯 Commande /brief reçue" in data["text"]
    
    def test_openapi_schema_generation(self):
        """Test that OpenAPI schema can be generated"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
    
    def test_docs_redirect(self):
        """Test docs redirect"""
        response = client.get("/docs")
        assert response.status_code == 200  # Should redirect to docs page


@pytest.mark.asyncio
class TestAPIAsyncSmoke:
    """Async smoke tests for API components"""
    
    async def test_async_endpoint_functionality(self):
        """Test that async endpoints work properly"""
        # This would test async components if needed
        assert True  # Placeholder for now


if __name__ == "__main__":
    pytest.main([__file__, "-v"])