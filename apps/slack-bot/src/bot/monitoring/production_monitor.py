"""
Monitoring Production pour Revolver AI Bot
Métriques, alertes et health checks
"""

import time
import asyncio
import psutil
from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Métriques de performance système"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    api_response_time: float
    active_requests: int
    cache_hit_rate: float
    error_rate: float

@dataclass
class BusinessMetrics:
    """Métriques business critiques"""
    timestamp: datetime
    briefs_processed: int
    veille_runs: int
    reports_generated: int
    slides_created: int
    api_calls_total: int
    successful_workflows: int
    failed_workflows: int

class ProductionMonitor:
    """Monitoring complet pour production"""
    
    def __init__(self):
        self.performance_history: deque = deque(maxlen=1000)
        self.business_history: deque = deque(maxlen=1000)
        self.error_counts: defaultdict = defaultdict(int)
        self.alert_thresholds = {
            'cpu_threshold': 80.0,
            'memory_threshold': 85.0,
            'disk_threshold': 90.0,
            'error_rate_threshold': 5.0,
            'response_time_threshold': 2.0
        }
        self.active_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.endpoint_metrics = {}
        self.start_time = datetime.now()
        
    def track_request_start(self, endpoint: str = None) -> str:
        """Tracker début de requête"""
        request_id = f"req_{int(time.time() * 1000)}"
        self.active_requests += 1
        if endpoint:
            self.endpoint_metrics[endpoint] = self.endpoint_metrics.get(endpoint, 0) + 1
        return request_id

    def get_cache_hit_rate(self) -> float:
        """Calculer taux de cache hit"""
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total > 0 else 0.0
    
    def get_error_rate(self) -> float:
        """Calculer taux d'erreur dernière heure"""
        current_hour = datetime.now().hour
        last_hour_errors = sum(
            count for hour, count in self.error_counts.items()
            if abs(hour - current_hour) <= 1
        )
        return last_hour_errors
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return {
            "performance": asdict(self.collect_performance_metrics()),
            "business": asdict(self.collect_business_metrics()),
            "cache": {
                "hit_rate": self.get_cache_hit_rate(),
                "hits": self.cache_hits,
                "misses": self.cache_misses
            },
            "requests": {
                "active": self.active_requests,
                "endpoints": self.endpoint_metrics
            },
            "uptime": (datetime.now() - self.start_time).total_seconds()
        }
    
    async def collect_performance_metrics(self) -> PerformanceMetrics:
        """Collecter métriques de performance"""
        try:
            # Métriques système
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Métriques applicatives
            start_time = time.time()
            # Simuler appel API pour mesurer temps de réponse
            await asyncio.sleep(0.01)
            response_time = time.time() - start_time
            
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage=(disk.used / disk.total) * 100,
                api_response_time=response_time,
                active_requests=self.active_requests,
                cache_hit_rate=self.get_cache_hit_rate(),
                error_rate=self.get_error_rate()
            )
            
            self.performance_history.append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte métriques: {e}")
            return None
    
    async def collect_business_metrics(self) -> BusinessMetrics:
        """Collecter métriques business"""
        try:
            # Ces valeurs seraient récupérées depuis la DB en production
            metrics = BusinessMetrics(
                timestamp=datetime.now(),
                briefs_processed=self._get_counter('briefs_processed'),
                veille_runs=self._get_counter('veille_runs'),
                reports_generated=self._get_counter('reports_generated'),
                slides_created=self._get_counter('slides_created'),
                api_calls_total=self._get_counter('api_calls_total'),
                successful_workflows=self._get_counter('successful_workflows'),
                failed_workflows=self._get_counter('failed_workflows')
            )
            
            self.business_history.append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur métriques business: {e}")
            return None
    
    def _get_counter(self, counter_name: str) -> int:
        """Récupérer compteur (mock pour démo)"""
        # En production, ceci viendrait de Redis/DB
        return len(self.performance_history) * 2
    
    def check_health(self) -> Dict[str, Any]:
        """Health check complet refactorisé"""
        try:
            # Étape 1: Collecte des métriques système
            metrics = self._collect_system_metrics()
            if not metrics:
                return self._create_error_response("Unable to collect metrics")

            # Étape 2: Vérification des seuils d'alerte
            alerts = self._check_alerts(metrics)

            # Étape 3: Construction de la réponse
            return self._build_health_response(metrics, alerts)

        except Exception as e:
            return self._handle_health_error(e)

    def _collect_system_metrics(self):
        """Collecte les métriques système"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return type('Metrics', (), {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_usage': (disk.used / disk.total) * 100,
                'api_response_time': 0.1,
                'active_requests': self.active_requests,
                'cache_hit_rate': self.get_cache_hit_rate(),
                'error_rate': self.get_error_rate()
            })()

        except ImportError:
            # Fallback si psutil non disponible
            return type('Metrics', (), {
                'cpu_percent': 10.0,
                'memory_percent': 50.0,
                'disk_usage': 30.0,
                'api_response_time': 0.1,
                'active_requests': self.active_requests,
                'cache_hit_rate': self.get_cache_hit_rate(),
                'error_rate': self.get_error_rate()
            })()

    def _check_alerts(self, metrics) -> List[str]:
        """Vérifie les seuils d'alerte et retourne la liste des alertes"""
        alerts = []

        alert_checks = [
            ('cpu_percent', 'cpu_threshold', "CPU usage high: {value:.1f}%"),
            ('memory_percent', 'memory_threshold', "Memory usage high: {value:.1f}%"),
            ('disk_usage', 'disk_threshold', "Disk usage high: {value:.1f}%"),
            ('error_rate', 'error_rate_threshold', "Error rate high: {value}")
        ]

        for metric_name, threshold_name, message_template in alert_checks:
            value = getattr(metrics, metric_name)
            threshold = self.alert_thresholds[threshold_name]

            if value > threshold:
                alerts.append(message_template.format(value=value))

        return alerts

    def _build_health_response(self, metrics, alerts: List[str]) -> Dict[str, Any]:
        """Construit la réponse de health check"""
        status = "healthy" if not alerts else "warning"
        uptime = datetime.now() - self.start_time

        return {
            "status": status,
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_human": str(uptime),
            "alerts": alerts,
            "metrics": {
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "disk_usage": metrics.disk_usage,
                "api_response_time": metrics.api_response_time,
                "active_requests": metrics.active_requests,
                "cache_hit_rate": metrics.cache_hit_rate,
                "error_rate": metrics.error_rate
            },
            "thresholds": self.alert_thresholds,
            "last_check": datetime.now().isoformat()
        }

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Crée une réponse d'erreur"""
        return {
            "status": "unhealthy",
            "error": error_message,
            "last_check": datetime.now().isoformat()
        }

    def _handle_health_error(self, error: Exception) -> Dict[str, Any]:
        """Gère les erreurs du health check"""
        logger.error(f"❌ Health check failed: {error}")
        return {
            "status": "unhealthy",
            "error": str(error),
            "last_check": datetime.now().isoformat()
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Données pour dashboard monitoring"""
        try:
            # Dernières métriques
            latest_perf = self.performance_history[-1] if self.performance_history else None
            latest_business = self.business_history[-1] if self.business_history else None
            
            # Tendances (dernières 10 mesures)
            recent_perf = list(self.performance_history)[-10:]
            recent_business = list(self.business_history)[-10:]
            
            return {
                "current": {
                    "performance": asdict(latest_perf) if latest_perf else None,
                    "business": asdict(latest_business) if latest_business else None
                },
                "trends": {
                    "performance": [asdict(m) for m in recent_perf],
                    "business": [asdict(m) for m in recent_business]
                },
                "summary": {
                    "total_requests": len(self.performance_history),
                    "cache_hit_rate": self.get_cache_hit_rate(),
                    "error_rate": self.get_error_rate(),
                    "uptime": (datetime.now() - self.start_time).total_seconds()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Dashboard data error: {e}")
            return {"error": str(e)}

# Instance globale
production_monitor = ProductionMonitor()

def monitor_endpoint(func):
    """Décorateur pour monitorer les endpoints"""
    async def wrapper(*args, **kwargs):
        request_id = production_monitor.track_request_start()
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            production_monitor.track_request_end(request_id, success=True)
            return result
            
        except Exception:
            production_monitor.track_request_end(request_id, success=False)
            raise
        
        finally:
            duration = time.time() - start_time
            logger.info(f"📊 {func.__name__} executed in {duration:.3f}s")
    
    return wrapper
