"""
Simple unit tests for ProductionMonitor
Tests basic monitoring functionalities
"""

import pytest
from datetime import datetime
from src.bot.monitoring.production_monitor import ProductionMonitor, PerformanceMetrics, BusinessMetrics


class TestPerformanceMetrics:
    """Test PerformanceMetrics dataclass"""
    
    def test_performance_metrics_creation(self):
        """Test basic PerformanceMetrics creation"""
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            cpu_percent=75.5,
            memory_percent=60.2,
            disk_usage=45.8,
            api_response_time=250.0,
            active_requests=150,
            cache_hit_rate=0.85,
            error_rate=0.02
        )
        
        assert metrics.cpu_percent == 75.5
        assert metrics.memory_percent == 60.2
        assert metrics.disk_usage == 45.8
        assert metrics.api_response_time == 250.0
        assert metrics.active_requests == 150
        assert metrics.cache_hit_rate == 0.85
        assert metrics.error_rate == 0.02
        assert isinstance(metrics.timestamp, datetime)


class TestBusinessMetrics:
    """Test BusinessMetrics dataclass"""
    
    def test_business_metrics_creation(self):
        """Test basic BusinessMetrics creation"""
        metrics = BusinessMetrics(
            timestamp=datetime.now(),
            briefs_processed=10,
            veille_runs=5,
            reports_generated=3,
            slides_created=8,
            api_calls_total=1000,
            successful_workflows=95,
            failed_workflows=5
        )
        
        assert metrics.briefs_processed == 10
        assert metrics.veille_runs == 5
        assert metrics.reports_generated == 3
        assert metrics.slides_created == 8
        assert metrics.api_calls_total == 1000
        assert metrics.successful_workflows == 95
        assert metrics.failed_workflows == 5
        assert isinstance(metrics.timestamp, datetime)


class TestProductionMonitor:
    """Test ProductionMonitor class"""
    
    @pytest.fixture
    def monitor(self):
        """Create a ProductionMonitor instance for testing"""
        return ProductionMonitor()
    
    def test_monitor_initialization(self, monitor):
        """Test monitor initialization"""
        assert monitor.cache_hits == 0
        assert monitor.cache_misses == 0
        assert monitor.active_requests == 0
    
    def test_track_request_start(self, monitor):
        """Test tracking request start"""
        monitor.track_request_start("test_request")
        assert monitor.active_requests == 1
    
    def test_track_request_end_success(self, monitor):
        """Test tracking successful request end"""
        monitor.track_request_start("test_request")
        monitor.track_request_end("test_request", success=True)
        assert monitor.active_requests == 0
    
    def test_track_request_end_failure(self, monitor):
        """Test tracking failed request end"""
        monitor.track_request_start("test_request")
        monitor.track_request_end("test_request", success=False)
        assert monitor.active_requests == 0
    
    def test_get_cache_hit_rate(self, monitor):
        """Test cache hit rate calculation"""
        # No cache activity
        assert monitor.get_cache_hit_rate() == 0.0
        
        # Some cache activity
        monitor.cache_hits = 8
        monitor.cache_misses = 2
        assert monitor.get_cache_hit_rate() == 80.0  # Returns percentage 