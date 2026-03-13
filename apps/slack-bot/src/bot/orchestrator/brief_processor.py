"""
Traitement spécialisé des briefs
Module séparé pour éviter le spaghetti dans orchestrator.py
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class BriefProcessor:
    """Classe spécialisée pour le traitement des briefs"""

    def __init__(self):
        pass

    def process_brief(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        schema_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Traite un brief PDF complet - refactorisé pour réduire la complexité

        Args:
            pdf_path: Chemin vers le fichier PDF
            output_dir: Répertoire de sortie (optionnel)
            schema_path: Chemin vers le schéma de validation (optionnel)

        Returns:
            Dictionnaire avec les résultats du traitement
        """
        logger.info(f"🎯 Processing brief: {pdf_path}")

        try:
            # Étape 1: Validation des entrées
            _validate_brief_inputs(pdf_path)

            # Étape 2: Traitement du texte
            text_result = _process_brief_text(self, pdf_path)

            # Étape 3: Traitement des sections
            sections_result = _process_brief_sections(self, text_result)

            # Étape 4: Validation du schéma
            validation_result = _validate_brief_schema(self, sections_result, schema_path)

            # Étape 5: Finalisation
            return _finalize_brief_processing(self, text_result, sections_result, validation_result, output_dir, pdf_path)

        except Exception as e:
            return _handle_brief_error(pdf_path, e)

def _validate_brief_inputs(pdf_path: str):
    """Valide les entrées du traitement de brief"""
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

def _process_brief_text(processor, pdf_path: str) -> Dict[str, Any]:
    """Traite le texte du brief"""
    return processor._extract_text(pdf_path)

def _process_brief_sections(processor, text_result: Dict[str, Any]) -> Dict[str, Any]:
    """Traite les sections du brief"""
    return processor._analyze_sections(text_result['text'])

def _validate_brief_schema(processor, sections_result: Dict[str, Any], schema_path: Optional[str]) -> Dict[str, Any]:
    """Valide le schéma du brief"""
    return processor._validate_schema(sections_result, schema_path)

def _finalize_brief_processing(processor, text_result: Dict[str, Any], sections_result: Dict[str, Any],
                              validation_result: Dict[str, Any], output_dir: Optional[str], pdf_path: str) -> Dict[str, Any]:
    """Finalise le traitement du brief"""
    # Structuration finale
    final_result = processor._structure_final_result(
        text_result, sections_result, validation_result
    )

    # Sauvegarde si demandé
    if output_dir:
        processor._save_results(final_result, output_dir, pdf_path)

    logger.info("✅ Brief processing completed successfully")
    return final_result

def _handle_brief_error(pdf_path: str, error: Exception) -> Dict[str, Any]:
    """Gère les erreurs de traitement de brief"""
    logger.error(f"❌ Brief processing failed: {error}")
    return {
        'success': False,
        'error': str(error),
        'pdf_path': pdf_path,
        'timestamp': datetime.now().isoformat()
    }

    def _extract_text(self, pdf_path: str) -> Dict[str, Any]:
        """Extrait le texte du PDF"""
        try:
            from ..parser import extract_text_from_pdf

            text = extract_text_from_pdf(pdf_path)

            return {
                'text': text,
                'text_length': len(text),
                'extraction_success': True
            }

        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return {
                'text': '',
                'text_length': 0,
                'extraction_success': False,
                'extraction_error': str(e)
            }

    def _analyze_sections(self, text: str) -> Dict[str, Any]:
        """Analyse les sections du brief"""
        try:
            from ..parser import extract_brief_sections

            sections = extract_brief_sections(text)

            return {
                'sections': sections,
                'sections_count': len(sections),
                'analysis_success': True
            }

        except Exception as e:
            logger.error(f"Sections analysis failed: {e}")
            return {
                'sections': {},
                'sections_count': 0,
                'analysis_success': False,
                'analysis_error': str(e)
            }

    def _validate_schema(self, sections_result: Dict, schema_path: Optional[str]) -> Dict[str, Any]:
        """Valide les sections contre le schéma"""
        if not schema_path:
            return {'validation_performed': False, 'validation_success': None}

        try:
            from .schema_validator import validate_brief_schema

            is_valid, errors = validate_brief_schema(sections_result['sections'], schema_path)

            return {
                'validation_performed': True,
                'validation_success': is_valid,
                'validation_errors': errors
            }

        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return {
                'validation_performed': True,
                'validation_success': False,
                'validation_errors': [str(e)]
            }

    def _structure_final_result(
        self,
        text_result: Dict,
        sections_result: Dict,
        validation_result: Dict
    ) -> Dict[str, Any]:
        """Structure le résultat final"""
        return {
            'success': True,
            'processing_timestamp': datetime.now().isoformat(),
            'text_extraction': text_result,
            'sections_analysis': sections_result,
            'schema_validation': validation_result,
            'summary': {
                'total_sections': sections_result.get('sections_count', 0),
                'validation_passed': validation_result.get('validation_success', None),
                'text_length': text_result.get('text_length', 0)
            }
        }

    def _save_results(self, result: Dict, output_dir: str, original_path: str):
        """Sauvegarde les résultats"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)

            # Nom du fichier basé sur l'original
            original_name = Path(original_path).stem
            output_file = output_path / f"{original_name}_processed.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"💾 Results saved to: {output_file}")

        except Exception as e:
            logger.error(f"Failed to save results: {e}")

# Fonction de compatibilité
def process_brief(
    pdf_path: str,
    output_dir: Optional[str] = None,
    schema_path: Optional[str] = None
) -> Dict[str, Any]:
    """Fonction de compatibilité pour l'ancien code"""
    processor = BriefProcessor()
    return processor.process_brief(pdf_path, output_dir, schema_path)
