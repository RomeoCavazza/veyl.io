#!/usr/bin/env python3
"""
Enhanced CLI for Revolver.bot
Provides comprehensive command-line interface for all bot functionalities
"""

# Standard library imports
import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Project imports
from core.config import Config
from core.cache import CacheManager
from bot.monitoring.production_monitor import ProductionMonitor
from bot.parser.pdf_parser import PdfParser
from bot.slides.canonical_generator import CanonicalGenerator
from bot.reco.generator import RecommendationGenerator

# Optional imports (may not be available)
try:
    from intelligence.veille.scraper import VeilleScraper
except ImportError:
    VeilleScraper = None


class RevolverCLI:
    """Enhanced CLI for Revolver.bot"""
    
    def __init__(self):
        self.config = Config()
        self.cache = CacheManager()
        self.monitor = ProductionMonitor()
        self.parser = PdfParser()
        self.scraper = VeilleScraper()
        self.slides_generator = CanonicalGenerator()
        self.reco_generator = RecommendationGenerator()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    async def process_brief(self, file_path: str, output_format: str = "json") -> Dict[str, Any]:
        """Process a brief PDF file"""
        try:
            self.logger.info(f"Processing brief: {file_path}")
            
            # Extract text from PDF
            text = self.parser.extract_text(file_path)
            if not text:
                raise ValueError("No text extracted from PDF")
                
            # Extract sections
            sections = self.parser.extract_sections(text)
            
            # Generate summary
            summary = {
                "file_path": file_path,
                "extracted_at": datetime.now().isoformat(),
                "sections": sections,
                "word_count": len(text.split()),
                "section_count": len(sections)
            }
            
            # Save output
            output_file = f"brief_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
            with open(output_file, 'w') as f:
                if output_format == "json":
                    json.dump(summary, f, indent=2)
                else:
                    f.write(str(summary))
                    
            self.logger.info(f"Brief analysis saved to: {output_file}")
            return summary
            
        except Exception as e:
            self.logger.error(f"Error processing brief: {e}")
            raise
            
    async def run_veille(self, 
                        competitors: List[str],
                        sources: List[str] = None,
                        output_file: str = None) -> Dict[str, Any]:
        """Run competitive intelligence veille"""
        try:
            self.logger.info(f"Starting veille for competitors: {competitors}")
            
            if sources is None:
                sources = ["instagram", "tiktok", "linkedin", "rss", "web"]
                
            results = {}
            
            # Instagram scraping
            if "instagram" in sources:
                self.logger.info("Scraping Instagram...")
                instagram_results = await self.scraper.scrape_instagram(competitors)
                results["instagram"] = instagram_results
                
            # TikTok scraping
            if "tiktok" in sources:
                self.logger.info("Scraping TikTok...")
                tiktok_results = await self.scraper.scrape_tiktok(competitors)
                results["tiktok"] = tiktok_results
                
            # LinkedIn scraping
            if "linkedin" in sources:
                self.logger.info("Scraping LinkedIn...")
                linkedin_results = await self.scraper.scrape_linkedin(competitors)
                results["linkedin"] = linkedin_results
                
            # RSS scraping
            if "rss" in sources:
                self.logger.info("Scraping RSS feeds...")
                rss_feeds = [
                    "https://feeds.feedburner.com/TechCrunch",
                    "https://rss.cnn.com/rss/edition.rss",
                    "https://feeds.bbci.co.uk/news/rss.xml"
                ]
                rss_results = await self.scraper.scrape_rss(rss_feeds)
                results["rss"] = rss_results
                
            # Web scraping
            if "web" in sources:
                self.logger.info("Scraping web sources...")
                web_urls = [f"https://www.{comp}.com" for comp in competitors]
                web_results = await self.scraper.scrape_web(web_urls)
                results["web"] = web_results
                
            # Save results
            if output_file is None:
                output_file = f"veille_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
                
            self.logger.info(f"Veille results saved to: {output_file}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error running veille: {e}")
            raise
            
    async def generate_slides(self, 
                            brief_file: str,
                            template: str = "canonical",
                            output_file: str = None) -> str:
        """Generate slides from brief"""
        try:
            self.logger.info(f"Generating slides from brief: {brief_file}")
            
            # Process brief first
            brief_data = await self.process_brief(brief_file)
            
            # Generate slides
            slides_data = await self.slides_generator.generate_canonical_slides(
                brief_data=brief_data,
                template_name=template
            )
            
            # Save slides
            if output_file is None:
                output_file = f"slides_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
                
            # Save as JSON for now (slides generation would need actual PPTX library)
            slides_json = f"{output_file}.json"
            with open(slides_json, 'w') as f:
                json.dump(slides_data, f, indent=2, default=str)
                
            self.logger.info(f"Slides data saved to: {slides_json}")
            return slides_json
            
        except Exception as e:
            self.logger.error(f"Error generating slides: {e}")
            raise
            
    async def generate_recommendation(self,
                                    brand_name: str,
                                    competitors: List[str],
                                    brief_file: str = None) -> Dict[str, Any]:
        """Generate recommendation report"""
        try:
            self.logger.info(f"Generating recommendation for {brand_name}")
            
            # Run veille first
            veille_data = await self.run_veille(competitors)
            
            # Generate recommendation
            recommendation = await self.reco_generator.generate_recommendation(
                brand_name=brand_name,
                competitors=competitors,
                veille_data=veille_data,
                brief_file=brief_file
            )
            
            # Save recommendation
            output_file = f"recommendation_{brand_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(recommendation, f, indent=2, default=str)
                
            self.logger.info(f"Recommendation saved to: {output_file}")
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Error generating recommendation: {e}")
            raise
            
    async def generate_newsletter(self,
                                veille_data: Dict[str, Any],
                                format_type: str = "weekly") -> Dict[str, Any]:
        """Generate newsletter from veille data"""
        try:
            self.logger.info(f"Generating {format_type} newsletter")
            
            # Create newsletter structure
            newsletter = {
                "type": format_type,
                "generated_at": datetime.now().isoformat(),
                "summary": {
                    "total_sources": len(veille_data),
                    "total_items": sum(len(items) for items in veille_data.values())
                },
                "highlights": [],
                "trends": [],
                "recommendations": []
            }
            
            # Process each source
            for source, items in veille_data.items():
                if items:
                    # Add highlights
                    for item in items[:3]:  # Top 3 items per source
                        newsletter["highlights"].append({
                            "source": source,
                            "title": item.title,
                            "content": item.content[:200] + "..." if len(item.content) > 200 else item.content,
                            "url": item.url
                        })
                        
            # Save newsletter
            output_file = f"newsletter_{format_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(newsletter, f, indent=2, default=str)
                
            self.logger.info(f"Newsletter saved to: {output_file}")
            return newsletter
            
        except Exception as e:
            self.logger.error(f"Error generating newsletter: {e}")
            raise
            
    async def run_complete_workflow(self,
                                  brief_file: str,
                                  brand_name: str,
                                  competitors: List[str]) -> Dict[str, Any]:
        """Run complete workflow: brief → veille → slides → recommendation → newsletter"""
        try:
            self.logger.info("Starting complete workflow")
            
            # Step 1: Process brief
            brief_data = await self.process_brief(brief_file)
            
            # Step 2: Run veille
            veille_data = await self.run_veille(competitors)
            
            # Step 3: Generate slides
            slides_file = await self.generate_slides(brief_file)
            
            # Step 4: Generate recommendation
            recommendation = await self.generate_recommendation(brand_name, competitors, brief_file)
            
            # Step 5: Generate newsletter
            newsletter = await self.generate_newsletter(veille_data, "weekly")
            
            # Compile results
            workflow_results = {
                "workflow_completed_at": datetime.now().isoformat(),
                "brief_analysis": brief_data,
                "veille_data": veille_data,
                "slides_file": slides_file,
                "recommendation": recommendation,
                "newsletter": newsletter
            }
            
            # Save complete workflow
            output_file = f"complete_workflow_{brand_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(workflow_results, f, indent=2, default=str)
                
            self.logger.info(f"Complete workflow saved to: {output_file}")
            return workflow_results
            
        except Exception as e:
            self.logger.error(f"Error in complete workflow: {e}")
            raise


def main():
    """Main CLI entry point - refactorisé pour réduire la complexité"""
    parser = argparse.ArgumentParser(description="Revolver.bot CLI - Competitive Intelligence Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Configuration des parsers pour chaque commande
    _setup_parsers(subparsers)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize CLI et exécution
    cli = RevolverCLI()
    await _execute_command(cli, args)

def _setup_parsers(subparsers):
    """Configure tous les parsers de sous-commandes"""
    _setup_brief_parser(subparsers)
    _setup_veille_parser(subparsers)
    _setup_slides_parser(subparsers)
    _setup_reco_parser(subparsers)
    _setup_newsletter_parser(subparsers)
    _setup_workflow_parser(subparsers)

def _setup_brief_parser(subparsers):
    """Configure le parser pour la commande brief"""
    brief_parser = subparsers.add_parser("brief", help="Process a brief PDF file")
    brief_parser.add_argument("file", help="Path to PDF file")
    brief_parser.add_argument("--format", default="json", choices=["json", "txt"], help="Output format")

def _setup_veille_parser(subparsers):
    """Configure le parser pour la commande veille"""
    veille_parser = subparsers.add_parser("veille", help="Run competitive intelligence veille")
    veille_parser.add_argument("competitors", nargs="+", help="List of competitors to analyze")
    veille_parser.add_argument("--sources", nargs="+",
                              choices=["instagram", "tiktok", "linkedin", "rss", "web", "deepweb", "osint"],
                              help="Sources to scrape")
    veille_parser.add_argument("--output", help="Output file path")

def _setup_slides_parser(subparsers):
    """Configure le parser pour la commande slides"""
    slides_parser = subparsers.add_parser("slides", help="Generate slides from brief")
    slides_parser.add_argument("brief", help="Path to brief PDF file")
    slides_parser.add_argument("--template", default="canonical", help="Template to use")
    slides_parser.add_argument("--output", help="Output file path")

def _setup_reco_parser(subparsers):
    """Configure le parser pour la commande recommendation"""
    reco_parser = subparsers.add_parser("recommendation", help="Generate recommendation report")
    reco_parser.add_argument("brand", help="Brand name")
    reco_parser.add_argument("competitors", nargs="+", help="List of competitors")
    reco_parser.add_argument("--brief", help="Path to brief PDF file")

def _setup_newsletter_parser(subparsers):
    """Configure le parser pour la commande newsletter"""
    newsletter_parser = subparsers.add_parser("newsletter", help="Generate newsletter")
    newsletter_parser.add_argument("veille_file", help="Path to veille results JSON file")
    newsletter_parser.add_argument("--format", default="weekly", choices=["weekly", "monthly"], help="Newsletter format")

def _setup_workflow_parser(subparsers):
    """Configure le parser pour la commande workflow"""
    workflow_parser = subparsers.add_parser("workflow", help="Run complete workflow")
    workflow_parser.add_argument("brief", help="Path to brief PDF file")
    workflow_parser.add_argument("brand", help="Brand name")
    workflow_parser.add_argument("competitors", nargs="+", help="List of competitors")

async def _execute_command(cli, args):
    """Exécute la commande demandée"""
    command_handlers = {
        "brief": lambda: cli.process_brief(args.file, args.format),
        "veille": lambda: cli.run_veille(args.competitors, args.sources, args.output),
        "slides": lambda: cli.generate_slides(args.brief, args.template, args.output),
        "recommendation": lambda: cli.generate_recommendation(args.brand, args.competitors, args.brief),
        "newsletter": lambda: _handle_newsletter_command(cli, args),
        "workflow": lambda: cli.run_complete_workflow(args.brief, args.brand, args.competitors)
    }

    try:
        handler = command_handlers.get(args.command)
        if handler:
            await handler()
        else:
            print(f"❌ Commande inconnue: {args.command}")
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")

async def _handle_newsletter_command(cli, args):
    """Gère la commande newsletter avec chargement du fichier"""
    with open(args.veille_file, 'r') as f:
        veille_data = json.load(f)
    await cli.generate_newsletter(veille_data, args.format)

# Point d'entrée pour l'exécution
if __name__ == "__main__":
    asyncio.run(main()) 