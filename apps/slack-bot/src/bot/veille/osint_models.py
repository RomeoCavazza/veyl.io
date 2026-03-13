"""
Modèles de données pour OSINT
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

@dataclass
class OSINTResult:
    """Résultat d'analyse OSINT"""
    source: str
    data_type: str
    content: str
    url: str
    timestamp: datetime
    confidence: float
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'source': self.source,
            'data_type': self.data_type,
            'content': self.content,
            'url': self.url,
            'timestamp': self.timestamp.isoformat(),
            'confidence': self.confidence,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OSINTResult':
        """Crée une instance depuis un dictionnaire"""
        return cls(
            source=data['source'],
            data_type=data['data_type'],
            content=data['content'],
            url=data['url'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            confidence=data.get('confidence', 0.5),
            metadata=data.get('metadata', {})
        )

class OSINTDataType(Enum):
    """Types de données OSINT"""
    DOMAIN = "domain"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    SOCIAL_MEDIA = "social_media"
    PUBLIC_RECORD = "public_record"
    FINANCIAL = "financial"
    LEGAL = "legal"

class OSINTSource(Enum):
    """Sources OSINT"""
    MALTEGO = "maltego"
    PUBLIC_RECORDS = "public_records"
    SOCIAL_MEDIA = "social_media"
    WEB_SCRAPING = "web_scraping"
    API_INTEGRATION = "api_integration"

@dataclass
class OSINTTarget:
    """Cible d'analyse OSINT"""
    identifier: str
    target_type: str  # company, person, domain, etc.
    metadata: Dict[str, Any]
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class OSINTSearchConfig:
    """Configuration de recherche OSINT"""
    max_results: int = 50
    timeout: int = 30
    sources: List[str] = None
    data_types: List[str] = None
    min_confidence: float = 0.3

    def __post_init__(self):
        if self.sources is None:
            self.sources = ["maltego", "public_records", "social_media"]
        if self.data_types is None:
            self.data_types = ["domain", "email", "social_media"]

@dataclass
class OSINTReport:
    """Rapport OSINT complet"""
    target: OSINTTarget
    results: List[OSINTResult]
    search_config: OSINTSearchConfig
    generated_at: datetime
    summary: Dict[str, Any]

    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            'target': {
                'identifier': self.target.identifier,
                'target_type': self.target.target_type,
                'metadata': self.target.metadata,
                'created_at': self.target.created_at.isoformat()
            },
            'results': [result.to_dict() for result in self.results],
            'search_config': {
                'max_results': self.search_config.max_results,
                'timeout': self.search_config.timeout,
                'sources': self.search_config.sources,
                'data_types': self.search_config.data_types,
                'min_confidence': self.search_config.min_confidence
            },
            'generated_at': self.generated_at.isoformat(),
            'summary': self.summary
        }
