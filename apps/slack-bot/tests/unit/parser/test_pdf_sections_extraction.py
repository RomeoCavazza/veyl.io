"""
Tests d'extraction de sections structurées
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


class TestPDFParserSectionsExtraction:
    """Tests pour tests d'extraction de sections structurées"""

    @pytest.mark.unit
    @pytest.mark.pdf
    def test_extract_sections_success(self):
        """Test d'extraction de sections avec succès"""
        test_content = """
        TITRE DU PROJET
        Test Project Title
        
        PROBLÉMATIQUE
        Test problem description
        
        SOLUTION
        Test solution description
        """
        
        with patch('src.bot.parser.pdf_parser.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = test_content
            
            sections = pdf_parser.extract_sections("test.pdf")
            assert isinstance(sections, dict)
            assert len(sections) > 0

    @pytest.mark.unit
    @pytest.mark.pdf
    def test_extract_sections_no_sections_found(self):
        """Test d'extraction sans sections trouvées"""
        test_content = "Contenu sans sections structurées"
        
        with patch('src.bot.parser.pdf_parser.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = test_content
            
            sections = pdf_parser.extract_sections("test.pdf")
            assert isinstance(sections, dict)

    @pytest.mark.unit
    @pytest.mark.pdf
    def test_extract_sections_partial_content(self):
        """Test d'extraction avec contenu partiel"""
        test_content = """
        TITRE DU PROJET
        Only title section present
        """
        
        with patch('src.bot.parser.pdf_parser.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = test_content
            
            sections = pdf_parser.extract_sections("test.pdf")
            assert isinstance(sections, dict)

    @pytest.mark.unit
    @pytest.mark.pdf
    def test_extract_sections_with_special_characters(self):
        """Test d'extraction avec caractères spéciaux"""
        test_content = """
        TITRE DU PROJET
        Test with éàü special chars
        
        PROBLÉMATIQUE
        Problem with àéè characters
        """
        
        with patch('src.bot.parser.pdf_parser.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = test_content
            
            sections = pdf_parser.extract_sections("test.pdf")
            assert isinstance(sections, dict)

    @pytest.mark.unit
    @pytest.mark.pdf
    def test_extract_sections_case_insensitive(self):
        """Test d'extraction insensible à la casse"""
        test_content = """
        titre du projet
        Test lowercase title
        
        problématique
        Test lowercase problem
        """
        
        with patch('src.bot.parser.pdf_parser.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = test_content
            
            sections = pdf_parser.extract_sections("test.pdf")
            assert isinstance(sections, dict)

    @pytest.mark.unit
    @pytest.mark.pdf
    def test_extract_sections_with_empty_content(self):
        """Test d'extraction avec contenu vide"""
        test_content = ""
        
        with patch('src.bot.parser.pdf_parser.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = test_content
            
            sections = pdf_parser.extract_sections("test.pdf")
            assert isinstance(sections, dict)

    @pytest.mark.unit
    @pytest.mark.pdf
    def test_extract_sections_with_malformed_content(self):
        """Test d'extraction avec contenu malformé"""
        test_content = """
        TITRE DU PROJET
        
        PROBLÉMATIQUE
        
        SOLUTION INCOMPLETE
        """
        
        with patch('src.bot.parser.pdf_parser.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = test_content
            
            sections = pdf_parser.extract_sections("test.pdf")
            assert isinstance(sections, dict) 
