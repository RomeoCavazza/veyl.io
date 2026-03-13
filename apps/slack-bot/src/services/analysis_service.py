"""
Service d'Analyse Unifié - Revolver AI Bot
Consolide tous les patterns d'analyse pour éviter la duplication
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re

# Import des dépendances d'analyse
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from textblob import TextBlob
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False

# Import des clients IA
try:
    from src.bot.ai.openai_client import get_ai_client, AIAnalysisResult
    HAS_AI_CLIENT = True
except ImportError:
    HAS_AI_CLIENT = False

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Résultat standardisé pour toutes les analyses"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    insights: Optional[List[str]] = None
    confidence: float = 0.0
    error_message: Optional[str] = None
    processing_time: float = 0.0
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AnalysisService:
    """
    Service unifié pour toutes les analyses du système.
    Consolidé les patterns répétitifs identifiés dans l'audit.
    """

    def __init__(self):
        """Initialise le service avec les analyseurs disponibles"""
        self.ai_client = get_ai_client() if HAS_AI_CLIENT else None

        # Initialisation des analyseurs de sentiment
        if HAS_NLTK:
            try:
                nltk.data.find('vader_lexicon')
            except LookupError:
                nltk.download('vader_lexicon')

            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        else:
            self.sentiment_analyzer = None
            logger.warning("NLTK non disponible - analyse de sentiment limitée")

    async def analyze_sentiment(self, text: str) -> AnalysisResult:
        """
        Analyse le sentiment d'un texte de manière unifiée.
        Consolidé depuis ultra_veille_engine.py et production_pipeline.py
        """
        start_time = datetime.now()

        try:
            if not text or not text.strip():
                return AnalysisResult(
                    success=False,
                    error_message="Texte vide ou invalide",
                    processing_time=(datetime.now() - start_time).total_seconds()
                )

            result_data = {}

            # Analyse NLTK VADER si disponible
            if self.sentiment_analyzer:
                vader_scores = self.sentiment_analyzer.polarity_scores(text)
                result_data.update({
                    'vader_compound': vader_scores['compound'],
                    'vader_positive': vader_scores['pos'],
                    'vader_negative': vader_scores['neg'],
                    'vader_neutral': vader_scores['neu']
                })

            # Analyse TextBlob si disponible
            try:
                blob = TextBlob(text)
                result_data.update({
                    'textblob_polarity': blob.sentiment.polarity,
                    'textblob_subjectivity': blob.sentiment.subjectivity
                })
            except:
                logger.warning("TextBlob non disponible pour l'analyse")

            # Détermination du sentiment global
            compound_score = result_data.get('vader_compound', 0)
            if compound_score > 0.1:
                overall_sentiment = 'positive'
                confidence = 0.8
            elif compound_score < -0.1:
                overall_sentiment = 'negative'
                confidence = 0.8
            else:
                overall_sentiment = 'neutral'
                confidence = 0.6

            result_data['overall_sentiment'] = overall_sentiment

            return AnalysisResult(
                success=True,
                data=result_data,
                confidence=confidence,
                processing_time=(datetime.now() - start_time).total_seconds()
            )

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de sentiment: {e}")
            return AnalysisResult(
                success=False,
                error_message=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )

    async def analyze_trends(self, texts: List[str]) -> AnalysisResult:
        """
        Analyse les tendances dans une liste de textes.
        Consolidé depuis ultra_veille_engine.py
        """
        start_time = datetime.now()

        try:
            if not texts:
                return AnalysisResult(
                    success=False,
                    error_message="Aucun texte à analyser",
                    processing_time=(datetime.now() - start_time).total_seconds()
                )

            # Analyse des mots-clés fréquents
            all_text = ' '.join(texts).lower()
            words = re.findall(r'\b\w+\b', all_text)

            # Filtrer les mots communs et courts
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
                'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
            }
            filtered_words = [
                word for word in words
                if word not in stop_words and len(word) > 3
            ]

            # Compter les occurrences
            word_counts = {}
            for word in filtered_words:
                word_counts[word] = word_counts.get(word, 0) + 1

            # Top tendances
            top_trends = sorted(
                word_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:20]

            trends_data = []
            for word, count in top_trends:
                trends_data.append({
                    'keyword': word,
                    'frequency': count,
                    'trending': count > len(texts) * 0.1  # 10% des textes
                })

            return AnalysisResult(
                success=True,
                data={'trends': trends_data},
                confidence=0.7,
                processing_time=(datetime.now() - start_time).total_seconds()
            )

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de tendances: {e}")
            return AnalysisResult(
                success=False,
                error_message=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )

    async def analyze_content(self, content: str) -> AnalysisResult:
        """
        Analyse générique de contenu.
        Consolidé depuis ultra_veille_engine.py et veilleur.py
        """
        start_time = datetime.now()

        try:
            if not content or not content.strip():
                return AnalysisResult(
                    success=False,
                    error_message="Contenu vide",
                    processing_time=(datetime.now() - start_time).total_seconds()
                )

            # Analyse de sentiment
            sentiment_result = await self.analyze_sentiment(content)

            # Analyse basique du contenu
            content_data = {
                'word_count': len(content.split()),
                'char_count': len(content),
                'sentence_count': len(content.split('.')),
                'sentiment': sentiment_result.data if sentiment_result.success else None
            }

            return AnalysisResult(
                success=True,
                data=content_data,
                confidence=sentiment_result.confidence,
                processing_time=(datetime.now() - start_time).total_seconds()
            )

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de contenu: {e}")
            return AnalysisResult(
                success=False,
                error_message=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )

    async def generate_insights(self, data: Dict[str, Any]) -> AnalysisResult:
        """
        Génère des insights basés sur les données d'analyse.
        Consolidé depuis ultra_veille_engine.py et production_pipeline.py
        """
        start_time = datetime.now()

        try:
            insights = []

            # Insights sur le sentiment
            if 'sentiment' in data and data['sentiment']:
                sentiment = data['sentiment']
                overall = sentiment.get('overall_sentiment')

                if overall == 'positive':
                    insights.append({
                        'type': 'sentiment',
                        'insight': 'Sentiment positif dominant détecté',
                        'confidence': 0.8,
                        'action': 'Capitaliser sur la perception positive'
                    })
                elif overall == 'negative':
                    insights.append({
                        'type': 'sentiment',
                        'insight': 'Sentiment négatif détecté',
                        'confidence': 0.8,
                        'action': 'Identifier et adresser les points de friction'
                    })

            # Insights sur les tendances
            if 'trends' in data and data['trends']:
                trending_keywords = [
                    t for t in data['trends']
                    if t.get('trending', False)
                ]

                if trending_keywords:
                    top_keywords = [t['keyword'] for t in trending_keywords[:3]]
                    insights.append({
                        'type': 'trends',
                        'insight': f'Tendances émergentes: {", ".join(top_keywords)}',
                        'confidence': 0.7,
                        'action': 'Intégrer ces tendances dans la stratégie marketing'
                    })

            # Insights sur la concurrence
            if 'competitors' in data and data['competitors']:
                competitor_count = len(data['competitors'])
                insights.append({
                    'type': 'competition',
                    'insight': f'{competitor_count} concurrents actifs identifiés',
                    'confidence': 0.9,
                    'action': 'Analyser les stratégies différenciatrices'
                })

            return AnalysisResult(
                success=True,
                data={'insights': insights},
                insights=[i['insight'] for i in insights],
                confidence=0.8,
                processing_time=(datetime.now() - start_time).total_seconds()
            )

        except Exception as e:
            logger.error(f"Erreur lors de la génération d'insights: {e}")
            return AnalysisResult(
                success=False,
                error_message=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )


# Instance globale du service
_analysis_service = None

def get_analysis_service() -> AnalysisService:
    """Factory pour obtenir l'instance du service d'analyse"""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service


# Fonctions de compatibilité supprimées - utiliser directement get_analysis_service()

# Toutes les fonctions de compatibilité ont été supprimées