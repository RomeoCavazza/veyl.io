"""
Processeur PDF principal
Orchestre tous les modules de parsing PDF
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import json

from .pdf_validator import PDFValidator
from .pdf_text_extractor import PDFTextExtractor
from .pdf_section_extractor import PDFSectionExtractor

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Processeur principal pour les fichiers PDF"""

    def __init__(self):
        self.validator = PDFValidator()
        self.text_extractor = PDFTextExtractor()
        self.section_extractor = PDFSectionExtractor()

    def process_pdf(
        self,
        pdf_path: str,
        extract_sections: bool = True,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Traitement complet d'un fichier PDF

        Args:
            pdf_path: Chemin vers le fichier PDF
            extract_sections: Si True, extrait aussi les sections spécialisées
            output_dir: Répertoire de sortie (optionnel)

        Returns:
            Dictionnaire avec tous les résultats du traitement
        """
        logger.info(f"🎯 Processing PDF: {pdf_path}")
        start_time = datetime.now()

        try:
            # Initialisation du résultat
            result = self._initialize_result(pdf_path, start_time)

            # Étape 1: Validation du fichier
            if not self._validate_pdf_file(pdf_path, result):
                return result

            # Étape 2: Extraction du texte
            if not self._extract_text_from_pdf(pdf_path, result):
                return result

            # Étape 3: Extraction des sections (optionnel)
            self._extract_sections_from_pdf(result, extract_sections)

            # Étape 4: Finalisation du traitement
            return self._finalize_processing(result, output_dir, pdf_path, start_time)

        except Exception as e:
            return self._handle_processing_error(e, result, start_time)

    def _initialize_result(self, pdf_path: str, start_time: datetime) -> Dict[str, Any]:
        """Initialise le dictionnaire de résultat"""
        return {
            'processing_success': False,
            'pdf_path': pdf_path,
            'processing_timestamp': start_time.isoformat(),
            'processing_time': 0
        }

    def _validate_pdf_file(self, pdf_path: str, result: Dict[str, Any]) -> bool:
        """Valide le fichier PDF et met à jour le résultat"""
        validation_result = self.validator.validate_file(pdf_path)
        result['validation'] = validation_result

        if not validation_result['is_valid']:
            result['error'] = 'PDF validation failed'
            return False

        return True

    def _extract_text_from_pdf(self, pdf_path: str, result: Dict[str, Any]) -> bool:
        """Extrait le texte du PDF et met à jour le résultat"""
        text_result = self.text_extractor.extract_text(pdf_path)
        result['text_extraction'] = text_result

        if not text_result['extraction_success']:
            result['error'] = 'Text extraction failed'
            return False

        return True

    def _extract_sections_from_pdf(self, result: Dict[str, Any], extract_sections: bool):
        """Extrait les sections du PDF si demandé"""
        if extract_sections:
            text_result = result['text_extraction']
            sections_result = self.section_extractor.extract_brief_sections(text_result['text'])
            result['sections_extraction'] = sections_result

    def _finalize_processing(self, result: Dict[str, Any], output_dir: str, pdf_path: str, start_time: datetime) -> Dict[str, Any]:
        """Finalise le traitement et retourne le résultat complet"""
        # Métadonnées générales
        sections_result = result.get('sections_extraction')
        result['metadata'] = self._generate_processing_metadata(
            result['validation'], result['text_extraction'], sections_result
        )

        # Sauvegarde si demandé
        if output_dir:
            self._save_processing_results(result, output_dir, pdf_path)

        result['processing_success'] = True
        result['processing_time'] = (datetime.now() - start_time).total_seconds()

        logger.info("✅ PDF processing completed successfully")
        return result

    def _handle_processing_error(self, error: Exception, result: Dict[str, Any], start_time: datetime) -> Dict[str, Any]:
        """Gère les erreurs de traitement"""
        logger.error(f"❌ PDF processing failed: {error}")
        result['error'] = str(error)
        result['processing_time'] = (datetime.now() - start_time).total_seconds()
        return result

    def process_pdf_batch(
        self,
        pdf_paths: List[str],
        extract_sections: bool = True,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Traitement par lot de plusieurs PDF

        Args:
            pdf_paths: Liste des chemins PDF
            extract_sections: Si True, extrait les sections
            output_dir: Répertoire de sortie

        Returns:
            Résultats du traitement par lot
        """
        logger.info(f"📦 Processing PDF batch: {len(pdf_paths)} files")

        batch_result = {
            'batch_size': len(pdf_paths),
            'processed_files': [],
            'failed_files': [],
            'start_time': datetime.now().isoformat()
        }

        for pdf_path in pdf_paths:
            try:
                result = self.process_pdf(pdf_path, extract_sections, output_dir)
                if result['processing_success']:
                    batch_result['processed_files'].append(pdf_path)
                else:
                    batch_result['failed_files'].append({
                        'path': pdf_path,
                        'error': result.get('error', 'Unknown error')
                    })
            except Exception as e:
                batch_result['failed_files'].append({
                    'path': pdf_path,
                    'error': str(e)
                })

        batch_result['end_time'] = datetime.now().isoformat()
        batch_result['success_rate'] = len(batch_result['processed_files']) / len(pdf_paths) * 100

        logger.info(f"✅ Batch processing completed: {len(batch_result['processed_files'])}/{len(pdf_paths)} successful")

        return batch_result

    def _generate_processing_metadata(
        self,
        validation: Dict,
        text_extraction: Dict,
        sections_extraction: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Génère les métadonnées du traitement"""
        metadata = {
            'file_info': validation.get('file_info', {}),
            'extraction_method': text_extraction.get('extraction_method'),
            'total_pages': text_extraction.get('total_pages', 0),
            'text_length': text_extraction.get('text_length', 0),
            'extraction_time': text_extraction.get('extraction_time', 0)
        }

        if sections_extraction:
            metadata.update({
                'sections_found': sections_extraction.get('extraction_metadata', {}).get('sections_found', 0),
                'completeness_score': sections_extraction.get('analysis', {}).get('completeness_score', 0)
            })

        return metadata

    def _save_processing_results(self, result: Dict, output_dir: str, original_path: str):
        """Sauvegarde les résultats du traitement"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)

            # Nom du fichier basé sur l'original
            original_name = Path(original_path).stem
            output_file = output_path / f"{original_name}_processed.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"💾 Processing results saved to: {output_file}")

        except Exception as e:
            logger.error(f"Failed to save processing results: {e}")

    def get_processing_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de traitement"""
        return {
            'text_extraction_stats': self.text_extractor.get_extraction_stats(),
            'processing_timestamp': datetime.now().isoformat()
        }

# Fonctions de compatibilité pour l'ancien code
def extract_text_from_pdf(pdf_path: str) -> str:
    """Fonction de compatibilité"""
    processor = PDFProcessor()
    result = processor.process_pdf(pdf_path, extract_sections=False)
    return result.get('text_extraction', {}).get('text', '')

def extract_brief_sections(text: str) -> Dict[str, Any]:
    """Fonction de compatibilité"""
    extractor = PDFSectionExtractor()
    return extractor.extract_brief_sections(text)

def validate_pdf_file(file_path: str) -> bool:
    """Fonction de compatibilité"""
    validator = PDFValidator()
    result = validator.validate_file(file_path)
    return result['is_valid']
