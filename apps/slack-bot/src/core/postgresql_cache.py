"""
Cache PostgreSQL spécialisé
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import hashlib

try:
    from psycopg2.extras import RealDictCursor
    from psycopg2.pool import SimpleConnectionPool
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

from .cache_models import CacheEntry, CacheStats

logger = logging.getLogger(__name__)

class PostgreSQLCache:
    """Cache PostgreSQL avec indexation temporelle"""

    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string
        self.pool = None
        self.table_name = 'cache_entries'
        self.stats = CacheStats()

        if POSTGRESQL_AVAILABLE and self.connection_string:
            try:
                self._initialize_database()
                logger.info("✅ Cache PostgreSQL initialized")
            except Exception as e:
                logger.error(f"❌ PostgreSQL initialization failed: {e}")
                self.pool = None
        else:
            logger.warning("⚠️ PostgreSQL not available, using fallback mode")

    def _initialize_database(self):
        """Initialise la base de données PostgreSQL"""
        if not self.pool:
            self.pool = SimpleConnectionPool(
                1, 20, self.connection_string
            )

        # Créer la table si elle n'existe pas
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            key VARCHAR(255) PRIMARY KEY,
            value JSONB,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            ttl INTEGER DEFAULT 3600,
            metadata JSONB DEFAULT '{{}}',
            access_count INTEGER DEFAULT 0,
            last_accessed TIMESTAMP WITH TIME ZONE
        );

        CREATE INDEX IF NOT EXISTS idx_cache_timestamp
        ON {self.table_name} (timestamp);

        CREATE INDEX IF NOT EXISTS idx_cache_ttl
        ON {self.table_name} (timestamp, ttl);
        """

        with self.pool.getconn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_table_sql)
                conn.commit()

    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        if not self.pool:
            return None

        try:
            with self.pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Récupérer et vérifier l'expiration
                    cursor.execute(f"""
                        SELECT * FROM {self.table_name}
                        WHERE key = %s
                        AND (ttl = 0 OR timestamp + INTERVAL '1 second' * ttl > NOW())
                    """, (key,))

                    result = cursor.fetchone()

                    if result:
                        # Mettre à jour les statistiques d'accès
                        cursor.execute(f"""
                            UPDATE {self.table_name}
                            SET access_count = access_count + 1,
                                last_accessed = NOW()
                            WHERE key = %s
                        """, (key,))

                        conn.commit()
                        self.stats.hits += 1

                        # Convertir la valeur JSON
                        return json.loads(result['value']) if isinstance(result['value'], str) else result['value']

                    self.stats.misses += 1
                    return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600, metadata: Optional[Dict] = None):
        """Stocke une valeur dans le cache"""
        if not self.pool:
            return

        try:
            with self.pool.getconn() as conn:
                with conn.cursor() as cursor:
                    # Convertir la valeur en JSON
                    json_value = json.dumps(value, default=str)

                    # Insérer ou mettre à jour
                    cursor.execute(f"""
                        INSERT INTO {self.table_name} (key, value, ttl, metadata)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (key) DO UPDATE SET
                            value = EXCLUDED.value,
                            timestamp = NOW(),
                            ttl = EXCLUDED.ttl,
                            metadata = EXCLUDED.metadata,
                            access_count = 0,
                            last_accessed = NULL
                    """, (key, json_value, ttl, json.dumps(metadata or {})))

                    conn.commit()

        except Exception as e:
            logger.error(f"Cache set error: {e}")

    def delete(self, key: str) -> bool:
        """Supprime une entrée du cache"""
        if not self.pool:
            return False

        try:
            with self.pool.getconn() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"DELETE FROM {self.table_name} WHERE key = %s", (key,))
                    deleted = cursor.rowcount > 0
                    conn.commit()
                    return deleted

        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def clear(self):
        """Vide complètement le cache"""
        if not self.pool:
            return

        try:
            with self.pool.getconn() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"TRUNCATE TABLE {self.table_name}")
                    conn.commit()

        except Exception as e:
            logger.error(f"Cache clear error: {e}")

    def cleanup_expired(self) -> int:
        """Nettoie les entrées expirées"""
        if not self.pool:
            return 0

        try:
            with self.pool.getconn() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"""
                        DELETE FROM {self.table_name}
                        WHERE ttl > 0 AND timestamp + INTERVAL '1 second' * ttl < NOW()
                    """)
                    deleted_count = cursor.rowcount
                    conn.commit()
                    self.stats.evictions += deleted_count
                    return deleted_count

        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache"""
        try:
            with self.pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(f"SELECT COUNT(*) as total FROM {self.table_name}")
                    result = cursor.fetchone()
                    self.stats.total_entries = result['total'] if result else 0

        except Exception as e:
            logger.error(f"Stats retrieval error: {e}")

        return self.stats.to_dict()

    def backup_data(self, filename: str):
        """Sauvegarde les données du cache"""
        if not self.pool:
            return

        try:
            with self.pool.getconn() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(f"SELECT * FROM {self.table_name}")

                    data = []
                    for row in cursor.fetchall():
                        data.append(dict(row))

                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, default=str)

                    logger.info(f"✅ Cache backed up to {filename}")

        except Exception as e:
            logger.error(f"Backup error: {e}")

    def restore_data(self, filename: str):
        """Restaure les données du cache"""
        if not self.pool:
            return

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            with self.pool.getconn() as conn:
                with conn.cursor() as cursor:
                    for entry in data:
                        cursor.execute(f"""
                            INSERT INTO {self.table_name}
                            (key, value, timestamp, ttl, metadata, access_count, last_accessed)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (key) DO NOTHING
                        """, (
                            entry['key'],
                            entry['value'],
                            entry['timestamp'],
                            entry.get('ttl', 3600),
                            json.dumps(entry.get('metadata', {})),
                            entry.get('access_count', 0),
                            entry.get('last_accessed')
                        ))

                    conn.commit()

            logger.info(f"✅ Cache restored from {filename}")

        except Exception as e:
            logger.error(f"Restore error: {e}")
