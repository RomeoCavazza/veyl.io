"""
Traitement spécialisé de l'analyse
Module séparé pour éviter le spaghetti dans orchestrator.py
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AnalysisProcessor:
    """Classe spécialisée pour les analyses"""

    def __init__(self):
        pass

    async def run_analyse(
        self,
        data_path: str,
        analysis_type: str = 'comprehensive',
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Exécute une analyse complète sur les données

        Args:
            data_path: Chemin vers les données à analyser
            analysis_type: Type d'analyse ('sentiment', 'trends', 'comprehensive')
            output_dir: Répertoire de sortie (optionnel)

        Returns:
            Dictionnaire avec les résultats de l'analyse
        """
        logger.info(f"🧠 Running {analysis_type} analysis on: {data_path}")

        start_time = datetime.now()
        results = {
            'success': False,
            'analysis_type': analysis_type,
            'data_path': data_path,
            'start_time': start_time.isoformat(),
            'processing_time': 0
        }

        try:
            # Chargement des données
            data = self._load_analysis_data(data_path)

            # Analyse selon le type
            if analysis_type == 'sentiment':
                analysis_results = await self._analyze_sentiment(data)
            elif analysis_type == 'trends':
                analysis_results = await self._analyze_trends(data)
            elif analysis_type == 'comprehensive':
                analysis_results = await self._analyze_comprehensive(data)
            else:
                raise ValueError(f"Unsupported analysis type: {analysis_type}")

            results.update(analysis_results)
            results['success'] = True

            # Calcul du temps de traitement
            end_time = datetime.now()
            results['processing_time'] = (end_time - start_time).total_seconds()

            # Sauvegarde si demandé
            if output_dir:
                self._save_analysis_results(results, output_dir, data_path)

            logger.info(f"✅ Analysis completed in {results['processing_time']:.2f}s")
            return results

        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            results['error'] = str(e)
            return results

    def _load_analysis_data(self, data_path: str) -> Dict[str, Any]:
        """Charge les données d'analyse"""
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load data from {data_path}: {e}")
            return {}

    async def _analyze_sentiment(self, data: Dict) -> Dict[str, Any]:
        """Analyse de sentiment"""
        try:
            from src.services.analysis_service import get_analysis_service

            service = get_analysis_service()

            # Extraction de tous les textes
            texts = self._extract_texts_from_data(data)

            if not texts:
                return {'sentiment_analysis': {'error': 'No texts found'}}

            # Analyse groupée
            combined_text = ' '.join(texts[:10])  # Limiter pour performance
            sentiment_result = await service.analyze_sentiment(combined_text)

            return {
                'sentiment_analysis': {
                    'overall_sentiment': sentiment_result.data.get('sentiment', 'neutral'),
                    'confidence': sentiment_result.data.get('confidence', 0.5),
                    'texts_analyzed': len(texts)
                }
            }

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {'sentiment_analysis': {'error': str(e)}}

    async def _analyze_trends(self, data: Dict) -> Dict[str, Any]:
        """Analyse des tendances"""
        try:
            from src.services.analysis_service import get_analysis_service

            service = get_analysis_service()

            # Extraction de tous les textes
            texts = self._extract_texts_from_data(data)

            if not texts:
                return {'trends_analysis': {'error': 'No texts found'}}

            # Analyse des tendances
            trends_result = await service.analyze_trends(texts)

            return {
                'trends_analysis': {
                    'top_trends': trends_result.data.get('trends', []),
                    'trends_count': len(trends_result.data.get('trends', [])),
                    'texts_analyzed': len(texts)
                }
            }

        except Exception as e:
            logger.error(f"Trends analysis failed: {e}")
            return {'trends_analysis': {'error': str(e)}}

    async def _analyze_comprehensive(self, data: Dict) -> Dict[str, Any]:
        """Analyse complète"""
        sentiment_results = await self._analyze_sentiment(data)
        trends_results = await self._analyze_trends(data)

        # Analyse des métriques
        metrics_analysis = self._analyze_metrics(data)

        return {
            'comprehensive_analysis': {
                'sentiment': sentiment_results.get('sentiment_analysis', {}),
                'trends': trends_results.get('trends_analysis', {}),
                'metrics': metrics_analysis,
                'summary': self._generate_analysis_summary(sentiment_results, trends_results, metrics_analysis)
            }
        }

    def _extract_texts_from_data(self, data: Dict) -> List[str]:
        """Extrait tous les textes des données"""
        texts = []

        def extract_from_dict(d):
            for key, value in d.items():
                if isinstance(value, str) and len(value) > 10:
                    texts.append(value)
                elif isinstance(value, dict):
                    extract_from_dict(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            extract_from_dict(item)
                        elif isinstance(item, str) and len(item) > 10:
                            texts.append(item)

        extract_from_dict(data)
        return texts

    def _analyze_metrics(self, data: Dict) -> Dict[str, Any]:
        """Analyse des métriques de base"""
        total_items = 0
        total_text_length = 0
        sources_count = 0

        def count_metrics(d):
            nonlocal total_items, total_text_length, sources_count

            if isinstance(d, dict):
                if 'content' in d and isinstance(d['content'], str):
                    total_items += 1
                    total_text_length += len(d['content'])

                for value in d.values():
                    count_metrics(value)

            elif isinstance(d, list):
                for item in d:
                    count_metrics(item)

        count_metrics(data)

        return {
            'total_items': total_items,
            'average_text_length': total_text_length / max(total_items, 1),
            'total_text_length': total_text_length
        }

    def _generate_analysis_summary(self, sentiment, trends, metrics) -> Dict[str, Any]:
        """Génère un résumé de l'analyse"""
        return {
            'key_findings': [
                f"Analysé {metrics.get('total_items', 0)} éléments",
                f"Sentiment général: {sentiment.get('sentiment_analysis', {}).get('overall_sentiment', 'N/A')}",
                f"Tendances identifiées: {trends.get('trends_analysis', {}).get('trends_count', 0)}"
            ],
            'data_quality_score': min(100, metrics.get('total_items', 0) * 10),
            'processing_timestamp': datetime.now().isoformat()
        }

    def _save_analysis_results(self, results: Dict, output_dir: str, original_path: str):
        """Sauvegarde les résultats d'analyse"""
        try:
            from pathlib import Path
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)

            original_name = Path(original_path).stem
            output_file = output_path / f"{original_name}_analysis.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"💾 Analysis results saved to: {output_file}")

        except Exception as e:
            logger.error(f"Failed to save analysis results: {e}")

# Fonction de compatibilité
async def run_analyse(
    data_path: str,
    analysis_type: str = 'comprehensive',
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """Fonction de compatibilité pour l'ancien code"""
    processor = AnalysisProcessor()
    return await processor.run_analyse(data_path, analysis_type, output_dir)
