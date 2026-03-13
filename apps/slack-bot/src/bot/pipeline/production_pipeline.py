"""
Pipeline de production complet pour Revolver.bot
Orchestration : Veille → Analyse → Livrables → Distribution
"""

# Standard library imports
import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .data_collectors import DataCollectors
from .data_analyzer import DataAnalyzer
from .deliverable_generator import DeliverableGenerator

logger = logging.getLogger(__name__)

@dataclass
class PipelineConfig:
    """Configuration du pipeline de production"""
    # Sources
    instagram_competitors: List[str]
    linkedin_competitors: List[str]
    tiktok_hashtags: List[str]
    
    # Livrables
    generate_weekly: bool = True
    generate_monthly: bool = False
    generate_recommendation: bool = False
    generate_newsletter: bool = False
    
    # Limites
    posts_per_competitor: int = 10
    max_hashtag_posts: int = 25
    analysis_depth: str = "standard"  # basic, standard, deep
    
    # Output
    output_dir: str = "output"
    save_raw_data: bool = True
    save_analysis: bool = True

@dataclass
class PipelineResult:
    """Résultat du pipeline de production"""
    pipeline_id: str
    timestamp: datetime
    config: PipelineConfig
    
    # Data collectée
    instagram_data: Dict[str, Any]
    linkedin_data: Dict[str, Any]
    tiktok_data: Dict[str, Any]
    
    # Analysis
    insights: Dict[str, Any]
    trends: Dict[str, Any]
    competitive_analysis: Dict[str, Any]
    
    # Livrables générés
    weekly_report: Optional[str] = None
    monthly_report: Optional[str] = None
    recommendation_slides: Optional[str] = None
    newsletter: Optional[str] = None
    
    # Métriques
    execution_time: float = 0.0
    data_points_collected: int = 0
    success_rate: float = 0.0
    errors: List[str] = None
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        # Fix datetime serialization
        if hasattr(self, 'timestamp') and self.timestamp:
            result['timestamp'] = self.timestamp.isoformat()
        return result

class ProductionPipeline:
    """
    Pipeline de production complet pour Revolver.bot
    """
    
    def __init__(self, config: PipelineConfig):
        self.config = config

        # Initialiser les modules spécialisés
        self.data_collectors = DataCollectors(config)
        self.data_analyzer = DataAnalyzer(None, None)  # TODO: injecter les dépendances
        self.deliverable_generator = DeliverableGenerator(None, Path(config.output_dir))

        # Créer répertoire de sortie
        self.output_path = Path(config.output_dir)
        self.output_path.mkdir(exist_ok=True)
    
    async def run_full_pipeline(self, brief_path: Optional[str] = None) -> PipelineResult:
        """
        Exécute le pipeline complet de production
        
        Args:
            brief_path: Chemin vers brief PDF (optionnel)
        
        Returns:
            Résultat complet du pipeline
        """
        start_time = datetime.now()
        pipeline_id = f"pipeline_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"🚀 Démarrage pipeline {pipeline_id}")
        
        result = PipelineResult(
            pipeline_id=pipeline_id,
            timestamp=start_time,
            config=self.config,
            instagram_data={},
            linkedin_data={},
            tiktok_data={},
            insights={},
            trends={},
            competitive_analysis={},
            errors=[]
        )
        
        try:
            # 1. COLLECTE DE DONNÉES
            logger.info("📡 Phase 1: Collecte de données")
            await self._collect_data(result)
            
            # 2. ANALYSE IA
            logger.info("🧠 Phase 2: Analyse IA")
            await self._analyze_data(result, brief_path)
            
            # 3. GÉNÉRATION LIVRABLES
            logger.info("📊 Phase 3: Génération livrables")
            await self._generate_deliverables(result, brief_path)
            
            # 4. SAUVEGARDE
            logger.info("💾 Phase 4: Sauvegarde")
            await self._save_results(result)
            
            # Calcul métriques finales
            end_time = datetime.now()
            result.execution_time = (end_time - start_time).total_seconds()
            result.success_rate = self._calculate_success_rate(result)
            
            logger.info(f"✅ Pipeline {pipeline_id} terminé en {result.execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Erreur pipeline {pipeline_id}: {e}")
            result.errors.append(str(e))
            result.success_rate = 0.0
        
        return result
    
    async def _collect_data(self, result: PipelineResult):
        """Collecte les données depuis toutes les sources"""

        # Utiliser le module de collecte spécialisé
        try:
            result.instagram_data = await self.data_collectors.collect_instagram_data()
            result.linkedin_data = await self.data_collectors.collect_linkedin_data()
            result.tiktok_data = await self.data_collectors.collect_tiktok_data()

            # Compter les points de données
            total_instagram = sum(len(posts) for posts in result.instagram_data.values())
            total_linkedin = sum(len(posts) for posts in result.linkedin_data.values())
            total_tiktok = sum(len(posts) for posts in result.tiktok_data.values())

            result.data_points_collected = total_instagram + total_linkedin + total_tiktok
            logger.info(f"✅ Collecte terminée: {result.data_points_collected} points de données")

        except Exception as e:
            logger.error(f"❌ Erreur collecte: {e}")
            result.errors.append(f"Collecte: {e}")
    
    async def _analyze_data(self, result: PipelineResult, brief_path: Optional[str]):
        """Analyse les données collectées avec IA"""

        try:
            # Analyser le brief si fourni
            brief_analysis = {}
            if brief_path:
                logger.info(f"📄 Analyse brief: {brief_path}")
                brief_analysis = await self.data_analyzer.analyze_brief(brief_path)

            # Utiliser le module d'analyse pour tout le reste
            logger.info("🎯 Analyse complète des données")
            result.competitive_analysis = await self.data_analyzer.analyze_competitive_data(result)
            result.trends = self.data_analyzer.detect_trends(result)
            result.insights = await self.data_analyzer.generate_insights(result, brief_analysis)

        except Exception as e:
            logger.error(f"❌ Erreur analyse: {e}")
            result.errors.append(f"Analyse: {e}")
    
    async def _generate_deliverables(self, result: PipelineResult, brief_path: Optional[str]):
        """Génère tous les livrables demandés"""

        try:
            # Utiliser le module de génération spécialisé
            if self.config.generate_weekly:
                logger.info("📊 Génération Weekly Report")
                result.weekly_report = str(await self.deliverable_generator.generate_weekly_report(result))

            if self.config.generate_monthly:
                logger.info("📈 Génération Monthly Report")
                result.monthly_report = str(await self.deliverable_generator.generate_monthly_report(result))

            if self.config.generate_recommendation and brief_path:
                logger.info("🎨 Génération Recommendation Slides")
                result.recommendation_slides = str(await self.deliverable_generator.generate_recommendation_slides(result, brief_path))

            if self.config.generate_newsletter:
                logger.info("📧 Génération Newsletter")
                result.newsletter = str(await self.deliverable_generator.generate_newsletter(result))

        except Exception as e:
            logger.error(f"❌ Erreur génération livrables: {e}")
            result.errors.append(f"Livrables: {e}")
    
