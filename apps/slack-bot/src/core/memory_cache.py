"""
Cache mémoire spécialisé
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import threading
import json

from .cache_models import CacheEntry, CacheStats

logger = logging.getLogger(__name__)

class MemoryCache:
    """Cache en mémoire avec nettoyage automatique"""

    def __init__(self, max_size: int = 1000, cleanup_interval: int = 300):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.stats = CacheStats()
        self.lock = threading.Lock()

        # Démarrer le nettoyage automatique
        self.cleanup_interval = cleanup_interval
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """Démarre le thread de nettoyage automatique"""
        def cleanup_worker():
            while True:
                try:
                    import time
                    time.sleep(self.cleanup_interval)
                    self._cleanup_expired()
                except Exception as e:
                    logger.error(f"Cleanup thread error: {e}")

        thread = threading.Thread(target=cleanup_worker, daemon=True)
        thread.start()

    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        with self.lock:
            entry = self.cache.get(key)

            if entry:
                if entry.is_expired():
                    # Supprimer l'entrée expirée
                    del self.cache[key]
                    self.stats.misses += 1
                    self.stats.evictions += 1
                    return None

                # Mettre à jour les statistiques
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                self.stats.hits += 1

                return entry.value

            self.stats.misses += 1
            return None

    def set(self, key: str, value: Any, ttl: int = 3600, metadata: Optional[Dict] = None):
        """Stocke une valeur dans le cache"""
        with self.lock:
            # Éviction si nécessaire
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_lru()

            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=datetime.now(),
                ttl=ttl,
                metadata=metadata or {}
            )

            self.cache[key] = entry

    def delete(self, key: str) -> bool:
        """Supprime une entrée du cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False

    def clear(self):
        """Vide complètement le cache"""
        with self.lock:
            self.cache.clear()
            self.stats = CacheStats()

    def _evict_lru(self):
        """Évince l'entrée la moins récemment utilisée"""
        if not self.cache:
            return

        # Trouver l'entrée la plus ancienne
        oldest_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_accessed or self.cache[k].timestamp
        )

        del self.cache[oldest_key]
        self.stats.evictions += 1

    def _cleanup_expired(self):
        """Nettoie les entrées expirées"""
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]

            for key in expired_keys:
                del self.cache[key]

            if expired_keys:
                self.stats.evictions += len(expired_keys)
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache"""
        with self.lock:
            self.stats.total_entries = len(self.cache)

        return self.stats.to_dict()

    def get_all_entries(self) -> List[CacheEntry]:
        """Retourne toutes les entrées du cache"""
        with self.lock:
            return list(self.cache.values())

    def get_entries_by_metadata(self, key: str, value: Any) -> List[CacheEntry]:
        """Retourne les entrées filtrées par métadonnées"""
        with self.lock:
            return [
                entry for entry in self.cache.values()
                if entry.metadata.get(key) == value
            ]

    def backup_data(self, filename: str):
        """Sauvegarde les données du cache"""
        try:
            with self.lock:
                data = {
                    'entries': [entry.to_dict() for entry in self.cache.values()],
                    'stats': self.stats.to_dict(),
                    'backup_timestamp': datetime.now().isoformat()
                }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"✅ Memory cache backed up to {filename}")

        except Exception as e:
            logger.error(f"Backup error: {e}")

    def restore_data(self, filename: str):
        """Restaure les données du cache"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            with self.lock:
                # Restaurer les entrées
                for entry_data in data.get('entries', []):
                    entry = CacheEntry.from_dict(entry_data)
                    self.cache[entry.key] = entry

                # Restaurer les statistiques
                stats_data = data.get('stats', {})
                self.stats = CacheStats(
                    total_entries=stats_data.get('total_entries', 0),
                    hits=stats_data.get('hits', 0),
                    misses=stats_data.get('misses', 0),
                    evictions=stats_data.get('evictions', 0)
                )

            logger.info(f"✅ Memory cache restored from {filename}")

        except Exception as e:
            logger.error(f"Restore error: {e}")

    def get_size(self) -> int:
        """Retourne la taille actuelle du cache"""
        with self.lock:
            return len(self.cache)

    def get_max_size(self) -> int:
        """Retourne la taille maximale du cache"""
        return self.max_size

    def set_max_size(self, max_size: int):
        """Modifie la taille maximale du cache"""
        self.max_size = max_size
        # Éviction immédiate si nécessaire
        with self.lock:
            while len(self.cache) > self.max_size:
                self._evict_lru()
