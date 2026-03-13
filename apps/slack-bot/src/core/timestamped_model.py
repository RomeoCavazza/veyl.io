"""
Classe de base pour les modèles avec timestamp automatique
Évite la duplication du code __post_init__ dans tous les dataclasses
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class TimestampedModel:
    """Classe de base pour les modèles avec timestamp automatique"""

    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Initialise automatiquement le timestamp si None"""
        if self.timestamp is None:
            self.timestamp = datetime.now()
