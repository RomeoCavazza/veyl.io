"""
Tests de nettoyage et normalisation du texte
Tests unitaires extraits de test_pdf_parser.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import tempfile

# Ajouter le chemin src au sys.path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from src.bot.parser import pdf_parser
from src.bot.parser.pdf_parser import PdfParser


class TestPDFParserTextProcessing:
    """Tests pour tests de nettoyage et normalisation du texte"""

    @pytest.mark.unit
    @pytest.mark.pdf
    def test_clean_text(self):
        """Test de nettoyage de texte"""
        dirty_text = "  Texte   avec   espaces   multiples  \n\n\n"
        clean_text = pdf_parser._clean_semantic(dirty_text)
        assert clean_text == "Texte avec espaces multiples"

    @pytest.mark.unit
    @pytest.mark.pdf
    def test_normalize_section_name(self):
        """Test de normalisation des noms de section"""
        # Test avec différents formats
        test_content = """
        TITRE: Test Project
        PROBLÉMATIQUE: Test Problem
        """
        sections = pdf_parser.extract_sections(test_content)
        assert "titre" in sections or "problème" in sections
