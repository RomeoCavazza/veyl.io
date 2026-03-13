"""
Modèles de données pour le système de cache
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CacheEntry:
    """Entrée de cache standardisée"""
    key: str
    value: Any
    timestamp: datetime
    ttl: int  # Time to live en secondes
    metadata: Dict[str, Any]
    access_count: int = 0
    last_accessed: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Vérifie si l'entrée est expirée"""
        if self.ttl <= 0:
            return False
        return (datetime.now() - self.timestamp).total_seconds() > self.ttl

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'key': self.key,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'ttl': self.ttl,
            'metadata': self.metadata,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Crée une instance depuis un dictionnaire"""
        return cls(
            key=data['key'],
            value=data['value'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            ttl=data['ttl'],
            metadata=data.get('metadata', {}),
            access_count=data.get('access_count', 0),
            last_accessed=datetime.fromisoformat(data['last_accessed']) if data.get('last_accessed') else None
        )

@dataclass
class CacheStats:
    """Statistiques du cache"""
    total_entries: int = 0
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_access_time: float = 0.0

    @property
    def hit_rate(self) -> float:
        """Calcule le taux de succès"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'total_entries': self.total_entries,
            'hits': self.hits,
            'misses': self.misses,
            'evictions': self.evictions,
            'hit_rate': self.hit_rate,
            'total_access_time': self.total_access_time
        }
