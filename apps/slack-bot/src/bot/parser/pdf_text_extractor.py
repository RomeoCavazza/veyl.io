"""
Extraction de texte des PDF
Module spécialisé pour l'extraction de texte
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import pypdf
    PDF_LIBRARY_AVAILABLE = True
except ImportError:
    PDF_LIBRARY_AVAILABLE = False

from .pdf_validator import PDFValidator

logger = logging.getLogger(__name__)

class PDFTextExtractor:
    """Extracteur de texte spécialisé pour les PDF"""

    def __init__(self):
        self.validator = PDFValidator()
        self.extraction_stats = {
            'total_pages': 0,
            'text_length': 0,
            'extraction_time': 0.0
        }

    def extract_text(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extraction complète du texte d'un PDF - refactorisé pour réduire la complexité

        Args:
            pdf_path: Chemin vers le fichier PDF

        Returns:
            Dictionnaire avec le texte extrait et les métadonnées
        """
        import time
        start_time = time.time()

        try:
            # Étape 1: Initialisation
            result = _initialize_extraction_result()

            # Étape 2: Validation du fichier
            if not _validate_pdf_file(self, pdf_path, result):
                return result

            # Étape 3: Détermination de la méthode d'extraction
            extraction_method = _determine_extraction_method()
            if not extraction_method:
                result['error'] = 'No PDF library available'
                return result

            # Étape 4: Exécution de l'extraction
            extraction_result = _perform_text_extraction(self, pdf_path, extraction_method)
            result.update(extraction_result)
            result['extraction_method'] = extraction_method

            # Étape 5: Finalisation
            return _finalize_extraction_result(result, start_time, self)

        except Exception as e:
            return _handle_extraction_error(e, result, start_time)

def _initialize_extraction_result() -> Dict[str, Any]:
    """Initialise le dictionnaire de résultat d'extraction"""
    return {
        'text': '',
        'pages': [],
        'total_pages': 0,
        'text_length': 0,
        'extraction_success': False,
        'extraction_method': None,
        'metadata': {}
    }

def _validate_pdf_file(extractor, pdf_path: str, result: Dict[str, Any]) -> bool:
    """Valide le fichier PDF"""
    validation = extractor.validator.validate_file(pdf_path)
    if not validation['is_valid']:
        result['error'] = 'File validation failed'
        result['validation_errors'] = validation['errors']
        return False
    return True

def _determine_extraction_method() -> Optional[str]:
    """Détermine la méthode d'extraction à utiliser"""
    if PDFPLUMBER_AVAILABLE:
        return 'pdfplumber'
    elif PDF_LIBRARY_AVAILABLE:
        return 'pypdf'
    return None

def _perform_text_extraction(extractor, pdf_path: str, method: str) -> Dict[str, Any]:
    """Exécute l'extraction du texte selon la méthode choisie"""
    if method == 'pdfplumber':
        return extractor._extract_with_pdfplumber(pdf_path)
    elif method == 'pypdf':
        return extractor._extract_with_pypdf(pdf_path)
    else:
        raise ValueError(f"Unsupported extraction method: {method}")

def _finalize_extraction_result(result: Dict[str, Any], start_time: float, extractor) -> Dict[str, Any]:
    """Finalise le résultat d'extraction"""
    import time
    result['extraction_success'] = True
    result['extraction_time'] = time.time() - start_time

    # Mise à jour des statistiques
    _update_extraction_stats(extractor, result)

    logger.info(f"✅ Text extraction completed: {result['total_pages']} pages, {result['text_length']} chars")
    return result

def _update_extraction_stats(extractor, result: Dict[str, Any]):
    """Met à jour les statistiques d'extraction"""
    extractor.extraction_stats['total_pages'] += result['total_pages']
    extractor.extraction_stats['text_length'] += result['text_length']
    extractor.extraction_stats['extraction_time'] += result['extraction_time']

def _handle_extraction_error(error: Exception, result: Dict[str, Any], start_time: float) -> Dict[str, Any]:
    """Gère les erreurs d'extraction"""
    import time
    result['error'] = str(error)
    result['extraction_time'] = time.time() - start_time
    logger.error(f"Text extraction failed: {error}")
    return result

    def _extract_with_pdfplumber(self, pdf_path: str) -> Dict[str, Any]:
        """Extraction avec pdfplumber"""
        pages_text = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                try:
                    text = page.extract_text()
                    if text:
                        pages_text.append(text.strip())
                    else:
                        pages_text.append("")
                except Exception as e:
                    logger.warning(f"Failed to extract text from page: {e}")
                    pages_text.append("")

        full_text = '\n\n'.join(pages_text)

        return {
            'text': full_text,
            'pages': pages_text,
            'total_pages': len(pages_text),
            'text_length': len(full_text)
        }

    def _extract_with_pypdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extraction avec pypdf"""
        pages_text = []

        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)

            for page in pdf_reader.pages:
                try:
                    text = page.extract_text()
                    if text:
                        pages_text.append(text.strip())
                    else:
                        pages_text.append("")
                except Exception as e:
                    logger.warning(f"Failed to extract text from page: {e}")
                    pages_text.append("")

        full_text = '\n\n'.join(pages_text)

        return {
            'text': full_text,
            'pages': pages_text,
            'total_pages': len(pages_text),
            'text_length': len(full_text)
        }

    def extract_page_range(self, pdf_path: str, start_page: int = 0, end_page: Optional[int] = None) -> Dict[str, Any]:
        """Extrait le texte d'une plage de pages spécifique"""
        try:
            full_result = self.extract_text(pdf_path)

            if not full_result['extraction_success']:
                return full_result

            pages = full_result['pages']
            if end_page is None:
                end_page = len(pages)

            selected_pages = pages[start_page:end_page]
            selected_text = '\n\n'.join(selected_pages)

            return {
                'text': selected_text,
                'pages': selected_pages,
                'total_pages': len(selected_pages),
                'text_length': len(selected_text),
                'page_range': f'{start_page}-{end_page-1}',
                'extraction_success': True
            }

        except Exception as e:
            logger.error(f"Page range extraction failed: {e}")
            return {
                'text': '',
                'error': str(e),
                'extraction_success': False
            }

    def get_extraction_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'extraction"""
        return self.extraction_stats.copy()

    def reset_stats(self):
        """Remet à zéro les statistiques"""
        self.extraction_stats = {
            'total_pages': 0,
            'text_length': 0,
            'extraction_time': 0.0
        }

# Fonction de compatibilité
def extract_text_from_pdf(pdf_path: str) -> str:
    """Fonction de compatibilité pour l'ancien code"""
    extractor = PDFTextExtractor()
    result = extractor.extract_text(pdf_path)
    return result['text']
