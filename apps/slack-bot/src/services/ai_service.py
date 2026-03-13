"""
Service IA Unifié - Revolver AI Bot
Standardise tous les appels OpenAI et patterns d'IA
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from src.core.timestamped_model import TimestampedModel

# Import des clients IA
try:
    from src.bot.ai.openai_client import get_ai_client, AIAnalysisResult
    HAS_OPENAI_CLIENT = True
except ImportError:
    HAS_OPENAI_CLIENT = False

logger = logging.getLogger(__name__)


class AnalysisType(Enum):
    """Types d'analyse supportés"""
    SENTIMENT = "sentiment"
    TRENDS = "trends"
    CONTENT = "content"
    BRIEF = "brief"
    VEILLE = "veille"
    PRESENTATION = "presentation"
    SLACK_RESPONSE = "slack_response"


@dataclass
class AIRequest(TimestampedModel):
    """Requête standardisée pour les appels IA"""
    content: str
    analysis_type: AnalysisType
    context: Optional[Dict[str, Any]] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    model: Optional[str] = None


@dataclass
class AIResponse:
    """Réponse standardisée des appels IA"""
    success: bool
    content: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    insights: Optional[List[str]] = None
    confidence: float = 0.0
    error_message: Optional[str] = None
    processing_time: float = 0.0
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AIService:
    """
    Service unifié pour tous les appels IA.
    Consolidé les patterns répétitifs identifiés dans l'audit.
    """

    def __init__(self):
        """Initialise le service avec les clients IA disponibles"""
        self.openai_client = get_ai_client() if HAS_OPENAI_CLIENT else None
        self.default_model = "gpt-4-turbo-preview"
        self.default_temperature = 0.7
        self.default_max_tokens = 4000

        if not HAS_OPENAI_CLIENT:
            logger.warning("Client OpenAI non disponible - mode mock activé")

    async def analyze(self, request: AIRequest) -> AIResponse:
        """
        Méthode principale pour analyser du contenu avec l'IA.
        Route automatiquement vers la bonne méthode selon le type d'analyse.
        """
        start_time = datetime.now()

        try:
            if not request.content or not request.content.strip():
                return AIResponse(
                    success=False,
                    error_message="Contenu vide ou invalide",
                    processing_time=(datetime.now() - start_time).total_seconds()
                )

            # Router vers la méthode appropriée
            if request.analysis_type == AnalysisType.SENTIMENT:
                return await self._analyze_sentiment(request)
            elif request.analysis_type == AnalysisType.TRENDS:
                return await self._analyze_trends(request)
            elif request.analysis_type == AnalysisType.CONTENT:
                return await self._analyze_content(request)
            elif request.analysis_type == AnalysisType.BRIEF:
                return await self._analyze_brief(request)
            elif request.analysis_type == AnalysisType.VEILLE:
                return await self._analyze_veille(request)
            elif request.analysis_type == AnalysisType.PRESENTATION:
                return await self._analyze_presentation(request)
            elif request.analysis_type == AnalysisType.SLACK_RESPONSE:
                return await self._analyze_slack_response(request)
            else:
                return AIResponse(
                    success=False,
                    error_message=f"Type d'analyse non supporté: {request.analysis_type}",
                    processing_time=(datetime.now() - start_time).total_seconds()
                )

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse IA: {e}")
            return AIResponse(
                success=False,
                error_message=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )

    async def _analyze_sentiment(self, request: AIRequest) -> AIResponse:
        """Analyse de sentiment via IA"""
        prompt = f"""
        Analyse le sentiment du texte suivant et retourne un JSON structuré :

        Texte: {request.content}

        Format de réponse JSON :
        {{
            "overall_sentiment": "positive|negative|neutral",
            "confidence": 0.0-1.0,
            "key_emotions": ["liste", "des", "émotions"],
            "intensity": "low|medium|high",
            "insights": ["insights principaux"]
        }}
        """

        return await self._call_ai(prompt, "sentiment_analysis")

    async def _analyze_trends(self, request: AIRequest) -> AIResponse:
        """Analyse de tendances via IA"""
        prompt = f"""
        Analyse les tendances dans le contenu suivant et retourne un JSON structuré :

        Contenu: {request.content}

        Format de réponse JSON :
        {{
            "trends": [
                {{
                    "keyword": "mot-clé",
                    "frequency": 5,
                    "trend_direction": "rising|stable|falling",
                    "relevance_score": 0.0-1.0
                }}
            ],
            "insights": ["insights sur les tendances"],
            "recommendations": ["recommandations"]
        }}
        """

        return await self._call_ai(prompt, "trends_analysis")

    async def _analyze_content(self, request: AIRequest) -> AIResponse:
        """Analyse de contenu générique via IA"""
        prompt = f"""
        Analyse le contenu suivant et retourne un JSON structuré :

        Contenu: {request.content}

        Format de réponse JSON :
        {{
            "summary": "résumé concis",
            "key_topics": ["sujet1", "sujet2"],
            "sentiment": "positive|negative|neutral",
            "readability_score": 0.0-1.0,
            "insights": ["insights principaux"],
            "action_items": ["actions recommandées"]
        }}
        """

        return await self._call_ai(prompt, "content_analysis")

    async def _analyze_brief(self, request: AIRequest) -> AIResponse:
        """Analyse de brief via IA (utilise le client existant)"""
        if not self.openai_client:
            return AIResponse(
                success=False,
                error_message="Client OpenAI non disponible"
            )

        try:
            result = self.openai_client.analyze_brief(request.content)

            return AIResponse(
                success=result.success,
                content=result.summary,
                structured_data=result.content,
                insights=result.insights,
                error_message=result.error_message,
                processing_time=result.processing_time,
                model_used=self.default_model
            )
        except Exception as e:
            return AIResponse(
                success=False,
                error_message=str(e)
            )

    async def _analyze_veille(self, request: AIRequest) -> AIResponse:
        """Analyse de veille via IA (utilise le client existant)"""
        if not self.openai_client:
            return AIResponse(
                success=False,
                error_message="Client OpenAI non disponible"
            )

        try:
            # Parser le contenu JSON des articles
            import json
            articles_data = json.loads(request.content) if isinstance(request.content, str) else request.content

            result = self.openai_client.generate_veille_insights(articles_data)

            return AIResponse(
                success=result.success,
                content=result.summary,
                structured_data=result.content,
                insights=result.insights,
                error_message=result.error_message,
                processing_time=result.processing_time,
                model_used=self.default_model
            )
        except Exception as e:
            return AIResponse(
                success=False,
                error_message=str(e)
            )

    async def _analyze_presentation(self, request: AIRequest) -> AIResponse:
        """Génération de présentation via IA (utilise le client existant)"""
        if not self.openai_client:
            return AIResponse(
                success=False,
                error_message="Client OpenAI non disponible"
            )

        try:
            # Parser les données du brief
            import json
            brief_data = json.loads(request.content) if isinstance(request.content, str) else request.content

            result = self.openai_client.generate_presentation_content(brief_data)

            return AIResponse(
                success=result.success,
                content=result.summary,
                structured_data=result.content,
                insights=result.insights,
                error_message=result.error_message,
                processing_time=result.processing_time,
                model_used=self.default_model
            )
        except Exception as e:
            return AIResponse(
                success=False,
                error_message=str(e)
            )

    async def _analyze_slack_response(self, request: AIRequest) -> AIResponse:
        """Génération de réponse Slack via IA (utilise le client existant)"""
        if not self.openai_client:
            return AIResponse(
                success=False,
                error_message="Client OpenAI non disponible"
            )

        try:
            context = request.context or {}
            result = self.openai_client.generate_slack_response(request.content, context)

            return AIResponse(
                success=True,
                content=str(result),
                model_used=self.default_model
            )
        except Exception as e:
            return AIResponse(
                success=False,
                error_message=str(e)
            )

    async def _call_ai(self, prompt: str, analysis_type: str) -> AIResponse:
        """
        Appel générique à l'IA avec gestion d'erreurs unifiée
        """
        if not self.openai_client:
            # Mode mock
            return AIResponse(
                success=True,
                content=f"Mock response for {analysis_type}",
                structured_data={"mock": True, "type": analysis_type},
                confidence=0.5,
                model_used="mock"
            )

        try:
            # Utiliser le client OpenAI existant pour les appels directs
            raw_response = self.openai_client._call_openai(prompt)

            if raw_response:
                # Essayer de parser le JSON si c'est une réponse structurée
                try:
                    import json
                    structured_data = json.loads(raw_response)
                    return AIResponse(
                        success=True,
                        content=raw_response,
                        structured_data=structured_data,
                        confidence=0.8,
                        model_used=self.default_model
                    )
                except json.JSONDecodeError:
                    return AIResponse(
                        success=True,
                        content=raw_response,
                        confidence=0.7,
                        model_used=self.default_model
                    )
            else:
                return AIResponse(
                    success=False,
                    error_message="Réponse vide de l'IA"
                )

        except Exception as e:
            return AIResponse(
                success=False,
                error_message=str(e)
            )


# Instance globale du service
_ai_service = None

def get_ai_service() -> AIService:
    """Factory pour obtenir l'instance du service IA"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


# Fonctions de compatibilité pour migration progressive
async def analyze_sentiment(text: str) -> AIResponse:
    """Fonction de compatibilité pour analyse de sentiment"""
    service = get_ai_service()
    request = AIRequest(content=text, analysis_type=AnalysisType.SENTIMENT)
    return await service.analyze(request)

async def analyze_trends(text: str) -> AIResponse:
    """Fonction de compatibilité pour analyse de tendances"""
    service = get_ai_service()
    request = AIRequest(content=text, analysis_type=AnalysisType.TRENDS)
    return await service.analyze(request)

async def analyze_content(content: str) -> AIResponse:
    """Fonction de compatibilité pour analyse de contenu"""
    service = get_ai_service()
    request = AIRequest(content=content, analysis_type=AnalysisType.CONTENT)
    return await service.analyze(request)