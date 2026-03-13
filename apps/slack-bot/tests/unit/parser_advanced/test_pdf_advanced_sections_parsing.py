import pytest
import sys
import os
from unittest.mock import patch, Mock

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from src.bot.parser.pdf_parser import extract_brief_sections, extract_sections


class TestPDFSectionsParsing:
    """Tests pour le parsing de sections PDF"""

    def test_extract_brief_sections_basic(self):
        """Test extraction de sections basique"""
        text = """
        CONTEXTE:
        Description du contexte
        
        OBJECTIFS:
        Liste des objectifs
        
        CIBLE:
        Audience cible
        """
        
        result = extract_brief_sections(text)
        
        assert isinstance(result, dict)
        print("✅ Test extract_brief_sections basic")

    def test_extract_brief_sections_empty_text(self):
        """Test extraction avec texte vide"""
        result = extract_brief_sections("")
        
        assert isinstance(result, dict)
        print("✅ Test extract_brief_sections empty text")

    def test_extract_sections_with_custom_markers(self):
        """Test extraction avec marqueurs personnalisés"""
        text = """
        SECTION A:
        Contenu de la section A
        
        SECTION B:
        Contenu de la section B
        """
        markers = ["SECTION A", "SECTION B"]
        
        result = extract_sections(text, markers)
        
        assert isinstance(result, dict)
        print("✅ Test extract_sections with custom markers")

    def test_extract_sections_default_markers(self):
        """Test extraction avec marqueurs par défaut"""
        text = """
        CONTEXTE:
        Description du contexte
        
        OBJECTIFS:
        Liste des objectifs
        """
        
        result = extract_sections(text)
        
        assert isinstance(result, dict)
        print("✅ Test extract_sections default markers") 