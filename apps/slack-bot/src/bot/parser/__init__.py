"""
Parser module for Revolver.bot
"""

from .pdf_parser import extract_text_from_pdf, PdfParser
from .nlp_utils import extract_brief_sections

__all__ = [
    "extract_text_from_pdf",
    "PdfParser",
    "extract_brief_sections"
]
