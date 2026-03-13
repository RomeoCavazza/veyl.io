"""
Revolver.bot - Assistant IA pour analyse de briefs et veille concurrentielle.
"""

# Imports principaux
from .parser.pdf_parser import extract_text_from_pdf, PdfParser
from .ai.brief_summarizer import summarize_brief
from .veille.veilleur import Veilleur
from .slides.builder import SlideBuilder, generate_presentation

# Modules avancés - à implémenter dans la phase MVP

__version__ = "1.0.0"
__all__ = [
    "extract_text_from_pdf",
    "PdfParser", 
    "summarize_brief",
    "Veilleur",
    "SlideBuilder",
    "generate_presentation"
]
