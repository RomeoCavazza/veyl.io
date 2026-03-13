"""
Orchestrateur de cache avancé
Combine PostgreSQL et mémoire pour optimisation
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
import os

from .cache_models import CacheEntry, CacheStats
from .postgresql_cache import PostgreSQLCache
from .memory_cache import MemoryCache

logger = logging.getLogger(__name__)

class AdvancedCache:
    """Cache avancé avec hiérarchie mémoire/PostgreSQL"""

    def __init__(self,
                 connection_string: Optional[str] = None,
                 memory_size: int = 1000,
                 default_ttl: int = 3600):
        self.default_ttl = default_ttl

        # Cache mémoire (L1 - rapide)
        self.memory_cache = MemoryCache(max_size=memory_size)

        # Cache PostgreSQL (L2 - persistant)
        self.postgresql_cache = PostgreSQLCache(connection_string)

        # Statistiques combinées
        self.stats = CacheStats()

        logger.info("✅ Advanced cache initialized")

    def _generate_key(self, data: Any) -> str:
        """Génère une clé de cache à partir des données"""
        if isinstance(data, str):
            key_data = data
        elif isinstance(data, dict):
            # Trier les clés pour une cohérence
            key_data = json.dumps(data, sort_keys=True, default=str)
        else:
            key_data = str(data)

        # Hash pour limiter la longueur
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache (L1 puis L2)"""
        start_time = datetime.now()

        # Essayer d'abord le cache mémoire
        value = self.memory_cache.get(key)

        if value is not None:
            self.stats.hits += 1
            self.stats.total_access_time += (datetime.now() - start_time).total_seconds()
            return value

        # Essayer le cache PostgreSQL
        value = self.postgresql_cache.get(key)

        if value is not None:
            # Promouvoir en mémoire pour les accès futurs
            self.memory_cache.set(key, value, ttl=self.default_ttl)
            self.stats.hits += 1
        else:
            self.stats.misses += 1

        self.stats.total_access_time += (datetime.now() - start_time).total_seconds()
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None, metadata: Optional[Dict] = None):
        """Stocke une valeur dans le cache (L1 et L2)"""
        ttl = ttl or self.default_ttl

        # Stocker dans les deux niveaux
        self.memory_cache.set(key, value, ttl=ttl, metadata=metadata)
        self.postgresql_cache.set(key, value, ttl=ttl, metadata=metadata)

    def delete(self, key: str) -> bool:
        """Supprime une entrée du cache (L1 et L2)"""
        memory_deleted = self.memory_cache.delete(key)
        postgresql_deleted = self.postgresql_cache.delete(key)

        return memory_deleted or postgresql_deleted

    def clear(self):
        """Vide complètement le cache (L1 et L2)"""
        self.memory_cache.clear()
        self.postgresql_cache.clear()
        self.stats = CacheStats()

    def cleanup_expired(self) -> int:
        """Nettoie les entrées expirées dans les deux niveaux"""
        memory_cleaned = 0  # Le cache mémoire se nettoie automatiquement
        postgresql_cleaned = self.postgresql_cache.cleanup_expired()

        return memory_cleaned + postgresql_cleaned

    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques combinées"""
        memory_stats = self.memory_cache.get_stats()
        postgresql_stats = self.postgresql_cache.get_stats()

        combined_stats = {
            'combined': self.stats.to_dict(),
            'memory': memory_stats,
            'postgresql': postgresql_stats,
            'timestamp': datetime.now().isoformat(),
            'cache_levels': 2 if self.postgresql_cache.pool else 1
        }

        return combined_stats

    def backup_data(self, filename: str):
        """Sauvegarde les données des deux niveaux"""
        try:
            # Sauvegarder la mémoire
            memory_file = f"{filename}_memory.json"
            self.memory_cache.backup_data(memory_file)

            # Sauvegarder PostgreSQL
            postgresql_file = f"{filename}_postgresql.json"
            self.postgresql_cache.backup_data(postgresql_file)

            # Fichier d'index
            index_data = {
                'backup_timestamp': datetime.now().isoformat(),
                'files': [memory_file, postgresql_file],
                'stats': self.get_stats()
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, default=str)

            logger.info(f"✅ Advanced cache backed up to {filename}")

        except Exception as e:
            logger.error(f"Backup error: {e}")

    def restore_data(self, filename: str):
        """Restaure les données des deux niveaux"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                index_data = json.load(f)

            # Restaurer chaque fichier
            for backup_file in index_data.get('files', []):
                if 'memory' in backup_file:
                    self.memory_cache.restore_data(backup_file)
                elif 'postgresql' in backup_file:
                    self.postgresql_cache.restore_data(backup_file)

            logger.info(f"✅ Advanced cache restored from {filename}")

        except Exception as e:
            logger.error(f"Restore error: {e}")

    # Méthodes avancées
    def get_with_fallback(self, key: str, fallback_func, *args, **kwargs) -> Any:
        """Récupère avec fallback automatique"""
        value = self.get(key)

        if value is None:
            # Calculer la valeur
            value = fallback_func(*args, **kwargs)

            # Cacher pour les futures requêtes
            self.set(key, value)

        return value

    def preload_keys(self, keys: List[str], data_func):
        """Précharge plusieurs clés"""
        for key in keys:
            if self.get(key) is None:
                try:
                    value = data_func(key)
                    self.set(key, value)
                except Exception as e:
                    logger.error(f"Preload failed for {key}: {e}")

    def get_pattern(self, pattern: str) -> Dict[str, Any]:
        """Récupère toutes les clés correspondant à un pattern (PostgreSQL seulement)"""
        # Cette fonctionnalité nécessite PostgreSQL avec LIKE
        if not self.postgresql_cache.pool:
            return {}

        try:
            # Simulation d'une recherche par pattern
            # En pratique, nécessiterait une implémentation spécifique
            return {}
        except Exception as e:
            logger.error(f"Pattern search error: {e}")
            return {}

    def optimize_for_read(self):
        """Optimise le cache pour les lectures intensives"""
        # Augmenter la taille mémoire
        current_size = self.memory_cache.get_max_size()
        self.memory_cache.set_max_size(current_size * 2)

    def optimize_for_write(self):
        """Optimise le cache pour les écritures intensives"""
        # Réduire la taille mémoire pour éviter la surcharge
        current_size = self.memory_cache.get_max_size()
        self.memory_cache.set_max_size(max(100, current_size // 2))

    def health_check(self) -> Dict[str, Any]:
        """Vérifie la santé du cache"""
        health = {
            'overall_status': 'healthy',
            'memory_cache': 'healthy',
            'postgresql_cache': 'unavailable',
            'timestamp': datetime.now().isoformat()
        }

        # Vérifier le cache mémoire
        try:
            self.memory_cache.get('health_check_test')
            health['memory_cache'] = 'healthy'
        except Exception as e:
            health['memory_cache'] = f'unhealthy: {e}'

        # Vérifier PostgreSQL
        if self.postgresql_cache.pool:
            try:
                self.postgresql_cache.get('health_check_test')
                health['postgresql_cache'] = 'healthy'
            except Exception as e:
                health['postgresql_cache'] = f'unhealthy: {e}'

        # Statut global
        if health['memory_cache'] != 'healthy':
            health['overall_status'] = 'unhealthy'
        elif health['postgresql_cache'] == 'unavailable':
            health['overall_status'] = 'degraded'

        return health

# Fonction de compatibilité
def get_advanced_cache(connection_string: Optional[str] = None) -> AdvancedCache:
    """Fonction de compatibilité pour créer un cache avancé"""
    return AdvancedCache(connection_string)
