"""
Traitement spécialisé de la veille
Module séparé pour éviter le spaghetti dans orchestrator.py
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class VeilleProcessor:
    """Classe spécialisée pour le traitement de la veille"""

    def __init__(self):
        self.sources = []

    async def run_veille(
        self,
        sources: List[str],
        output_dir: Optional[str] = None,
        max_items: int = 50
    ) -> Dict[str, Any]:
        """
        Exécute une veille complète sur les sources spécifiées

        Args:
            sources: Liste des sources à surveiller
            output_dir: Répertoire de sortie (optionnel)
            max_items: Nombre maximum d'éléments par source

        Returns:
            Dictionnaire avec les résultats de la veille
        """
        logger.info(f"🔍 Running veille on {len(sources)} sources")

        start_time = datetime.now()
        results = {
            'success': False,
            'sources_processed': [],
            'total_items': 0,
            'start_time': start_time.isoformat(),
            'processing_time': 0
        }

        try:
            # Traitement parallèle des sources
            tasks = []
            for source in sources:
                task = self._process_source(source, max_items)
                tasks.append(task)

            source_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Agrégation des résultats
            successful_results = []
            for i, result in enumerate(source_results):
                if isinstance(result, Exception):
                    logger.error(f"❌ Source {sources[i]} failed: {result}")
                else:
                    successful_results.append(result)
                    results['sources_processed'].append(sources[i])

            # Consolidation des données
            consolidated_data = self._consolidate_veille_data(successful_results)
            results.update(consolidated_data)
            results['success'] = True

            # Calcul du temps de traitement
            end_time = datetime.now()
            results['processing_time'] = (end_time - start_time).total_seconds()

            logger.info(f"✅ Veille completed: {results['total_items']} items from {len(successful_results)} sources")
            return results

        except Exception as e:
            logger.error(f"❌ Veille failed: {e}")
            results['error'] = str(e)
            return results

    async def _process_source(self, source: str, max_items: int) -> Dict[str, Any]:
        """Traite une source individuelle"""
        try:
            logger.info(f"📡 Processing source: {source}")

            # Simulation du traitement (à remplacer par la vraie logique)
            if 'web' in source.lower():
                items = await self._scrape_web_source(source, max_items)
            elif 'social' in source.lower():
                items = await self._scrape_social_source(source, max_items)
            elif 'news' in source.lower():
                items = await self._scrape_news_source(source, max_items)
            else:
                items = []

            return {
                'source': source,
                'items': items,
                'items_count': len(items),
                'processing_timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Source processing failed for {source}: {e}")
            raise

    async def _scrape_web_source(self, source: str, max_items: int) -> List[Dict]:
        """Scrape une source web"""
        # Simulation - à remplacer par vraie logique de scraping
        return [
            {
                'title': f'Web Article {i+1}',
                'url': f'https://{source}/article{i+1}',
                'content': f'Content from {source}',
                'timestamp': datetime.now().isoformat(),
                'source_type': 'web'
            }
            for i in range(min(max_items, 5))
        ]

    async def _scrape_social_source(self, source: str, max_items: int) -> List[Dict]:
        """Scrape une source sociale"""
        # Simulation - à remplacer par vraie logique de scraping
        return [
            {
                'content': f'Social post {i+1} from {source}',
                'author': f'user_{i+1}',
                'engagement': {'likes': 10+i, 'comments': 2+i},
                'timestamp': datetime.now().isoformat(),
                'source_type': 'social'
            }
            for i in range(min(max_items, 10))
        ]

    async def _scrape_news_source(self, source: str, max_items: int) -> List[Dict]:
        """Scrape une source d'actualité"""
        # Simulation - à remplacer par vraie logique de scraping
        return [
            {
                'title': f'News {i+1}',
                'content': f'News content from {source}',
                'timestamp': datetime.now().isoformat(),
                'source_type': 'news'
            }
            for i in range(min(max_items, 8))
        ]

    def _consolidate_veille_data(self, source_results: List[Dict]) -> Dict[str, Any]:
        """Consolide les données de veille"""
        all_items = []
        total_items = 0

        for result in source_results:
            items = result.get('items', [])
            all_items.extend(items)
            total_items += result.get('items_count', 0)

        # Analyse basique des tendances
        trends = self._analyze_veille_trends(all_items)

        return {
            'total_items': total_items,
            'all_items': all_items,
            'trends': trends,
            'sources_count': len(source_results)
        }

    def _analyze_veille_trends(self, items: List[Dict]) -> Dict[str, Any]:
        """Analyse les tendances dans les données de veille"""
        if not items:
            return {'error': 'No items to analyze'}

        # Analyse simple des mots-clés
        keywords = {}
        for item in items:
            content = item.get('content', '') + item.get('title', '')
            words = content.lower().split()

            for word in words:
                if len(word) > 3:  # Mots significatifs
                    keywords[word] = keywords.get(word, 0) + 1

        # Top 10 mots-clés
        top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            'top_keywords': [{'word': k, 'count': v} for k, v in top_keywords],
            'total_unique_words': len(keywords),
            'analysis_timestamp': datetime.now().isoformat()
        }

# Fonction de compatibilité
async def run_veille(
    sources: List[str],
    output_dir: Optional[str] = None,
    max_items: int = 50
) -> Dict[str, Any]:
    """Fonction de compatibilité pour l'ancien code"""
    processor = VeilleProcessor()
    return await processor.run_veille(sources, output_dir, max_items)
