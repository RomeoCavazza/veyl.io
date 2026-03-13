"""
PDF parsing refactorisé
Utilise des modules spécialisés pour éviter le spaghetti code
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Importer les modules spécialisés
from .pdf_validator import PDFValidator, validate_pdf_file
from .pdf_text_extractor import PDFTextExtractor, extract_text_from_pdf
from .pdf_section_extractor import PDFSectionExtractor, extract_brief_sections
from .pdf_processor import PDFProcessor

# Fonctions de compatibilité pour l'ancien code
def get_pdf_processor() -> PDFProcessor:
    """Retourne une instance du processeur PDF"""
    return PDFProcessor()

# Classes de compatibilité
class PdfParser:
    """Wrapper de compatibilité pour PDFProcessor"""

    def __init__(self, *args, **kwargs):
        self.processor = PDFProcessor()

    def process_pdf(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """Traite un PDF"""
        return self.processor.process_pdf(pdf_path, **kwargs)

# Instance globale pour compatibilité
_pdf_processor = None

def get_global_pdf_processor() -> PDFProcessor:
    """Retourne l'instance globale du processeur PDF"""
    global _pdf_processor
    if _pdf_processor is None:
        _pdf_processor = PDFProcessor()
    return _pdf_processor
