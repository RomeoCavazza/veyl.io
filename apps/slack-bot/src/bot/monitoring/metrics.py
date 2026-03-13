import time
import psutil
from typing import Callable, Any, Dict
from src.utils.logger_v2 import logger
from functools import wraps
from prometheus_client import Counter, Histogram, REGISTRY

# Pattern singleton pour éviter la duplication des métriques
_metrics_initialized = False
_metrics = {}

def _get_or_create_metric(metric_type, name, description, labels=None):
    """Crée ou récupère une métrique Prometheus pour éviter les doublons"""
    global _metrics_initialized, _metrics
    
    if not _metrics_initialized:
        # Nettoyer le registre au premier appel
        try:
            for collector in list(REGISTRY._collector_to_names.keys()):
                if hasattr(collector, '_name') and collector._name in ['api_requests_total', 'api_errors_total', 'api_request_latency_seconds']:
                    REGISTRY.unregister(collector)
        except Exception:
            pass
        _metrics_initialized = True
    
    if name not in _metrics:
        if metric_type == 'counter':
            _metrics[name] = Counter(name, description, labels or [])
        elif metric_type == 'histogram':
            _metrics[name] = Histogram(name, description, labels or [])
    
    return _metrics[name]

# Métriques Prometheus avec gestion des doublons
API_REQUESTS = _get_or_create_metric('counter', 'api_requests_total', 'Total API requests', ['endpoint'])
API_ERRORS = _get_or_create_metric('counter', 'api_errors_total', 'Total API errors', ['endpoint', 'error_type'])
API_LATENCY = _get_or_create_metric('histogram', 'api_request_latency_seconds', 'API request latency', ['endpoint'])

def track_execution_time(func: Callable) -> Callable:
    """Décorateur pour suivre le temps d'exécution d'une fonction."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def get_system_metrics() -> Dict[str, Any]:
    """Récupère les métriques système."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available": memory.available,
            "disk_percent": disk.percent,
            "disk_free": disk.free
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métriques système: {e}")
        return {}

def export_prometheus() -> str:
    """Exporte les métriques au format Prometheus."""
    try:
        from prometheus_client import generate_latest
        return generate_latest(REGISTRY).decode('utf-8')
    except Exception as e:
        logger.error(f"Erreur lors de l'export Prometheus: {e}")
        return ""

def health_check() -> Dict[str, Any]:
    """Vérifie la santé du système."""
    system_metrics = get_system_metrics()
    
    # Seuils de santé
    cpu_threshold = 90
    memory_threshold = 90
    disk_threshold = 90
    
    is_healthy = (
        system_metrics.get("cpu_percent", 0) < cpu_threshold and
        system_metrics.get("memory_percent", 0) < memory_threshold and
        system_metrics.get("disk_percent", 0) < disk_threshold
    )
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": time.time(),
        "metrics": system_metrics,
        "thresholds": {
            "cpu": cpu_threshold,
            "memory": memory_threshold,
            "disk": disk_threshold
        }
    }

def reset_metrics():
    """Réinitialise toutes les métriques (pour les tests)."""
    global _metrics_initialized, _metrics
    _metrics_initialized = False
    _metrics.clear()
    
    # Nettoyer le registre
    try:
        for collector in list(REGISTRY._collector_to_names.keys()):
            if hasattr(collector, '_name') and collector._name in ['api_requests_total', 'api_errors_total', 'api_request_latency_seconds']:
                REGISTRY.unregister(collector)
    except Exception:
        pass
