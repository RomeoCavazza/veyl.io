"""
Système de cache avancé refactorisé
Utilise des modules spécialisés pour éviter le spaghetti code
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Importer les modules spécialisés
from .cache_models import CacheEntry, CacheStats
from .postgresql_cache import PostgreSQLCache, POSTGRESQL_AVAILABLE
from .memory_cache import MemoryCache
from .advanced_cache_orchestrator import AdvancedCache, get_advanced_cache

# Fonctions de compatibilité pour l'ancien code
def get_cache(connection_string: Optional[str] = None) -> AdvancedCache:
    """Fonction de compatibilité"""
    return get_advanced_cache(connection_string)

# Classes de compatibilité pour l'ancien code
class CacheManager:
    """Wrapper de compatibilité pour AdvancedCache"""

    def __init__(self, connection_string: Optional[str] = None):
        self.cache = get_advanced_cache(connection_string)

    def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key)

    def set(self, key: str, value: Any, **kwargs):
        return self.cache.set(key, value, **kwargs)

    def delete(self, key: str) -> bool:
        return self.cache.delete(key)

    def clear(self):
        return self.cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        return self.cache.get_stats()

# Instance globale pour compatibilité
_default_cache = None

def get_default_cache() -> AdvancedCache:
    """Retourne le cache par défaut"""
    global _default_cache
    if _default_cache is None:
        _default_cache = get_advanced_cache()
    return _default_cache
