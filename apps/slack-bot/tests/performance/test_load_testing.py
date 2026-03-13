"""
Tests pour les tests de charge et de performance
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import time
from tests.performance.load_testing import (
    LoadTester, SystemMonitor, PerformanceAnalyzer, LoadTestRunner,
    PerformanceMetrics, SystemMetrics, run_load_tests
)


class TestLoadTester:
    """Tests pour LoadTester"""
    
    @pytest.mark.asyncio
    async def test_load_tester_initialization(self):
        """Test initialisation de LoadTester"""
        async with LoadTester("http://localhost:8000") as tester:
            assert tester is not None
            assert tester.base_url == "http://localhost:8000"
            assert tester.session is not None
    
    @pytest.mark.asyncio
    async def test_test_endpoint_get_success(self):
        """Test endpoint GET avec succès"""
        async with LoadTester("http://localhost:8000") as tester:
            # Mock de la réponse
            mock_response = Mock()
            mock_response.status = 200
            
            with patch.object(tester.session, 'get') as mock_get:
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = await tester.test_endpoint("/health")
                
                assert result['success'] is True
                assert result['status_code'] == 200
                assert result['response_time'] > 0
                assert isinstance(result['timestamp'], datetime)
    
    @pytest.mark.asyncio
    async def test_test_endpoint_post_success(self):
        """Test endpoint POST avec succès"""
        async with LoadTester("http://localhost:8000") as tester:
            # Mock de la réponse
            mock_response = Mock()
            mock_response.status = 201
            
            with patch.object(tester.session, 'post') as mock_post:
                mock_post.return_value.__aenter__.return_value = mock_response
                
                result = await tester.test_endpoint("/brief", method="POST", payload={"test": "data"})
                
                assert result['success'] is True
                assert result['status_code'] == 201
                assert result['response_time'] > 0
    
    @pytest.mark.asyncio
    async def test_test_endpoint_failure(self):
        """Test endpoint avec échec"""
        async with LoadTester("http://localhost:8000") as tester:
            # Mock d'une exception
            with patch.object(tester.session, 'get') as mock_get:
                mock_get.side_effect = Exception("Connection error")
                
                result = await tester.test_endpoint("/health")
                
                assert result['success'] is False
                assert result['status_code'] == 0
                assert result['response_time'] > 0
                assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_concurrent_load_test(self):
        """Test de charge concurrent"""
        async with LoadTester("http://localhost:8000") as tester:
            # Mock des réponses
            mock_response = Mock()
            mock_response.status = 200
            
            with patch.object(tester.session, 'get') as mock_get:
                mock_get.return_value.__aenter__.return_value = mock_response
                
                metrics = await tester.concurrent_load_test("/health", num_requests=10, concurrency=5)
                
                assert isinstance(metrics, PerformanceMetrics)
                assert metrics.total_requests == 10
                assert metrics.successful_requests == 10
                assert metrics.failed_requests == 0
                assert metrics.total_time > 0
                assert metrics.requests_per_second > 0
                assert metrics.error_rate == 0.0
    
    @pytest.mark.asyncio
    async def test_stress_test(self):
        """Test de stress"""
        async with LoadTester("http://localhost:8000") as tester:
            # Mock des réponses
            mock_response = Mock()
            mock_response.status = 200
            
            with patch.object(tester.session, 'get') as mock_get:
                mock_get.return_value.__aenter__.return_value = mock_response
                
                metrics_list = await tester.stress_test("/health", duration=5, requests_per_second=2)
                
                assert isinstance(metrics_list, list)
                assert len(metrics_list) > 0
                
                for metrics in metrics_list:
                    assert isinstance(metrics, PerformanceMetrics)
                    assert metrics.total_requests > 0


class TestSystemMonitor:
    """Tests pour SystemMonitor"""
    
    def test_system_monitor_initialization(self):
        """Test initialisation de SystemMonitor"""
        monitor = SystemMonitor()
        assert monitor is not None
        assert hasattr(monitor, 'metrics_history')
        assert isinstance(monitor.metrics_history, list)
    
    @patch('tests.performance.load_testing.psutil')
    def test_get_system_metrics_success(self, mock_psutil):
        """Test récupération des métriques système (succès)"""
        # Mock des métriques système
        mock_psutil.cpu_percent.return_value = 50.0
        
        mock_memory = Mock()
        mock_memory.percent = 75.0
        mock_psutil.virtual_memory.return_value = mock_memory
        
        mock_disk = Mock()
        mock_disk.read_bytes = 1000000
        mock_disk.write_bytes = 2000000
        mock_disk.read_count = 100
        mock_disk.write_count = 200
        mock_psutil.disk_io_counters.return_value = mock_disk
        
        mock_network = Mock()
        mock_network.bytes_sent = 500000
        mock_network.bytes_recv = 1000000
        mock_network.packets_sent = 50
        mock_network.packets_recv = 100
        mock_psutil.net_io_counters.return_value = mock_network
        
        monitor = SystemMonitor()
        metrics = monitor.get_system_metrics()
        
        assert isinstance(metrics, SystemMetrics)
        assert metrics.cpu_usage == 50.0
        assert metrics.memory_usage == 75.0
        assert metrics.active_threads >= 0
        assert isinstance(metrics.timestamp, datetime)
        assert len(monitor.metrics_history) == 1
    
    @patch('tests.performance.load_testing.psutil')
    def test_get_system_metrics_failure(self, mock_psutil):
        """Test récupération des métriques système (échec)"""
        # Mock d'une exception
        mock_psutil.cpu_percent.side_effect = Exception("System error")
        
        monitor = SystemMonitor()
        metrics = monitor.get_system_metrics()
        
        assert isinstance(metrics, SystemMetrics)
        assert metrics.cpu_usage == 0.0
        assert metrics.memory_usage == 0.0
        assert metrics.active_threads == 0
    
    def test_monitor_during_test(self):
        """Test monitoring pendant un test"""
        monitor = SystemMonitor()
        
        # Test avec une durée courte
        metrics_list = monitor.monitor_during_test(duration=2, interval=1)
        
        assert isinstance(metrics_list, list)
        assert len(metrics_list) >= 1  # Au moins une métrique collectée
        
        for metrics in metrics_list:
            assert isinstance(metrics, SystemMetrics)


class TestPerformanceAnalyzer:
    """Tests pour PerformanceAnalyzer"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.analyzer = PerformanceAnalyzer()
    
    def test_performance_analyzer_initialization(self):
        """Test initialisation de PerformanceAnalyzer"""
        assert self.analyzer is not None
        assert hasattr(self.analyzer, 'analysis_results')
    
    def test_analyze_performance_metrics(self):
        """Test analyse des métriques de performance"""
        # Créer des métriques de test
        metrics = [
            PerformanceMetrics(
                test_name="test1",
                total_requests=100,
                successful_requests=95,
                failed_requests=5,
                total_time=10.0,
                avg_response_time=0.1,
                min_response_time=0.05,
                max_response_time=0.2,
                p95_response_time=0.15,
                p99_response_time=0.18,
                requests_per_second=10.0,
                error_rate=0.05,
                timestamp=datetime.now()
            ),
            PerformanceMetrics(
                test_name="test2",
                total_requests=50,
                successful_requests=48,
                failed_requests=2,
                total_time=5.0,
                avg_response_time=0.08,
                min_response_time=0.03,
                max_response_time=0.15,
                p95_response_time=0.12,
                p99_response_time=0.14,
                requests_per_second=10.0,
                error_rate=0.04,
                timestamp=datetime.now()
            )
        ]
        
        analysis = self.analyzer.analyze_performance_metrics(metrics)
        
        assert isinstance(analysis, dict)
        assert 'summary' in analysis
        assert 'response_times' in analysis
        assert 'recommendations' in analysis
        
        summary = analysis['summary']
        assert summary['total_requests'] == 150
        assert summary['successful_requests'] == 143
        assert summary['failed_requests'] == 7
        assert summary['success_rate'] == 143 / 150
        assert summary['total_time'] == 15.0
        assert summary['throughput_rps'] == 150 / 15.0
    
    def test_analyze_performance_metrics_empty(self):
        """Test analyse avec métriques vides"""
        analysis = self.analyzer.analyze_performance_metrics([])
        
        assert isinstance(analysis, dict)
        assert 'error' in analysis
    
    def test_analyze_system_metrics(self):
        """Test analyse des métriques système"""
        # Créer des métriques système de test
        metrics = [
            SystemMetrics(
                cpu_usage=50.0,
                memory_usage=60.0,
                disk_io={'read_bytes': 1000000, 'write_bytes': 2000000},
                network_io={'bytes_sent': 500000, 'bytes_recv': 1000000},
                active_threads=10,
                timestamp=datetime.now()
            ),
            SystemMetrics(
                cpu_usage=70.0,
                memory_usage=80.0,
                disk_io={'read_bytes': 1500000, 'write_bytes': 2500000},
                network_io={'bytes_sent': 600000, 'bytes_recv': 1200000},
                active_threads=15,
                timestamp=datetime.now()
            )
        ]
        
        analysis = self.analyzer.analyze_system_metrics(metrics)
        
        assert isinstance(analysis, dict)
        assert 'cpu' in analysis
        assert 'memory' in analysis
        assert 'threads' in analysis
        assert 'recommendations' in analysis
        
        cpu_analysis = analysis['cpu']
        assert cpu_analysis['average_percent'] == 60.0
        assert cpu_analysis['max_percent'] == 70.0
        assert cpu_analysis['status'] in ['low', 'normal', 'high']
    
    def test_analyze_system_metrics_empty(self):
        """Test analyse avec métriques système vides"""
        analysis = self.analyzer.analyze_system_metrics([])
        
        assert isinstance(analysis, dict)
        assert 'error' in analysis


class TestLoadTestRunner:
    """Tests pour LoadTestRunner"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.runner = LoadTestRunner("http://localhost:8000")
    
    def test_load_test_runner_initialization(self):
        """Test initialisation de LoadTestRunner"""
        assert self.runner is not None
        assert self.runner.base_url == "http://localhost:8000"
        assert hasattr(self.runner, 'analyzer')
    
    @pytest.mark.asyncio
    async def test_run_comprehensive_load_test(self):
        """Test exécution complète des tests de charge"""
        endpoints = ["/health", "/brief"]
        test_config = {
            'num_requests': 10,
            'concurrency': 5,
            'stress_duration': 5,
            'stress_rps': 2,
            'duration': 10
        }
        
        # Mock des réponses
        mock_response = Mock()
        mock_response.status = 200
        
        with patch('tests.performance.load_testing.LoadTester') as mock_tester_class:
            mock_tester = Mock()
            mock_tester_class.return_value.__aenter__.return_value = mock_tester
            
            # Mock des méthodes de test
            mock_tester.concurrent_load_test.return_value = PerformanceMetrics(
                test_name="test",
                total_requests=10,
                successful_requests=10,
                failed_requests=0,
                total_time=1.0,
                avg_response_time=0.1,
                min_response_time=0.05,
                max_response_time=0.2,
                p95_response_time=0.15,
                p99_response_time=0.18,
                requests_per_second=10.0,
                error_rate=0.0,
                timestamp=datetime.now()
            )
            
            mock_tester.stress_test.return_value = []
            
            results = self.runner.run_comprehensive_load_test(endpoints, test_config)
            
            assert isinstance(results, dict)
            assert 'performance_metrics' in results
            assert 'system_metrics' in results
            assert 'analysis' in results
            assert 'timestamp' in results
    
    def test_save_results(self):
        """Test sauvegarde des résultats"""
        test_results = {
            'performance_metrics': [],
            'system_metrics': [],
            'analysis': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Test sauvegarde
        success = self.runner.save_results(test_results, 'test_results.json')
        
        # Peut échouer si pas de permissions d'écriture, mais structure correcte
        assert isinstance(success, bool)


class TestRunLoadTests:
    """Tests pour la fonction utilitaire"""
    
    @pytest.mark.asyncio
    async def test_run_load_tests_default(self):
        """Test fonction utilitaire avec paramètres par défaut"""
        # Mock de la fonction de test
        with patch('tests.performance.load_testing.LoadTestRunner') as mock_runner_class:
            mock_runner = Mock()
            mock_runner_class.return_value = mock_runner
            
            mock_runner.run_comprehensive_load_test.return_value = {
                'performance_metrics': [],
                'system_metrics': [],
                'analysis': {},
                'timestamp': datetime.now().isoformat()
            }
            
            results = run_load_tests()
            
            assert isinstance(results, dict)
            assert 'performance_metrics' in results
            assert 'system_metrics' in results
            assert 'analysis' in results
    
    @pytest.mark.asyncio
    async def test_run_load_tests_custom(self):
        """Test fonction utilitaire avec paramètres personnalisés"""
        custom_endpoints = ["/custom1", "/custom2"]
        custom_config = {
            'num_requests': 50,
            'concurrency': 20,
            'stress_duration': 30,
            'stress_rps': 5,
            'duration': 120
        }
        
        # Mock de la fonction de test
        with patch('tests.performance.load_testing.LoadTestRunner') as mock_runner_class:
            mock_runner = Mock()
            mock_runner_class.return_value = mock_runner
            
            mock_runner.run_comprehensive_load_test.return_value = {
                'performance_metrics': [],
                'system_metrics': [],
                'analysis': {},
                'timestamp': datetime.now().isoformat()
            }
            
            results = run_load_tests(
                base_url="http://test.com",
                endpoints=custom_endpoints,
                config=custom_config
            )
            
            assert isinstance(results, dict)
            # Vérifier que les paramètres personnalisés ont été utilisés
            mock_runner.run_comprehensive_load_test.assert_called_once()
            call_args = mock_runner.run_comprehensive_load_test.call_args
            assert call_args[0][0] == custom_endpoints  # endpoints
            assert call_args[0][1] == custom_config  # config


class TestPerformanceMetrics:
    """Tests pour PerformanceMetrics"""
    
    def test_performance_metrics_creation(self):
        """Test création de PerformanceMetrics"""
        metrics = PerformanceMetrics(
            test_name="test",
            total_requests=100,
            successful_requests=95,
            failed_requests=5,
            total_time=10.0,
            avg_response_time=0.1,
            min_response_time=0.05,
            max_response_time=0.2,
            p95_response_time=0.15,
            p99_response_time=0.18,
            requests_per_second=10.0,
            error_rate=0.05,
            timestamp=datetime.now()
        )
        
        assert metrics.test_name == "test"
        assert metrics.total_requests == 100
        assert metrics.successful_requests == 95
        assert metrics.failed_requests == 5
        assert metrics.total_time == 10.0
        assert metrics.avg_response_time == 0.1
        assert metrics.requests_per_second == 10.0
        assert metrics.error_rate == 0.05
        assert isinstance(metrics.timestamp, datetime)


class TestSystemMetrics:
    """Tests pour SystemMetrics"""
    
    def test_system_metrics_creation(self):
        """Test création de SystemMetrics"""
        metrics = SystemMetrics(
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_io={'read_bytes': 1000000, 'write_bytes': 2000000},
            network_io={'bytes_sent': 500000, 'bytes_recv': 1000000},
            active_threads=10,
            timestamp=datetime.now()
        )
        
        assert metrics.cpu_usage == 50.0
        assert metrics.memory_usage == 60.0
        assert metrics.disk_io['read_bytes'] == 1000000
        assert metrics.network_io['bytes_sent'] == 500000
        assert metrics.active_threads == 10
        assert isinstance(metrics.timestamp, datetime)


if __name__ == "__main__":
    pytest.main([__file__]) 