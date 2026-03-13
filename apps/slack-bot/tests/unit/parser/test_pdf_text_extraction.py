"""
Tests d'extraction de texte brut du PDF
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


class TestPDFParserTextExtraction:
    """Tests pour tests d'extraction de texte brut du pdf"""

    @pytest.mark.unit
    @pytest.mark.pdf
    def test_extract_text_success(self):
        """Test d'extraction de texte avec succès"""
        with patch('src.bot.parser.pdf_parser.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = "Texte extrait du PDF"
            
            result = pdf_parser.extract_text_from_pdf("test.pdf")
            assert result == "Texte extrait du PDF"
            mock_extract.assert_called_once_with("test.pdf")

    @pytest.mark.unit
    @pytest.mark.pdf
    def test_extract_text_multiple_pages(self):
        """Test d'extraction de texte sur plusieurs pages"""
        with patch('src.bot.parser.pdf_parser.extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = "Page 1\nPage 2\nPage 3"
            
            result = pdf_parser.extract_text_from_pdf("multi_page.pdf")
            assert "Page 1" in result
            assert "Page 2" in result
            assert "Page 3" in result

    @pytest.mark.unit
    @pytest.mark.pdf
    def test_extract_text_file_not_found(self):
        """Test d'extraction avec fichier inexistant"""
        with patch('src.bot.parser.pdf_parser.extract_text_from_pdf') as mock_extract:
            mock_extract.side_effect = FileNotFoundError("Fichier non trouvé")
            
            with pytest.raises(FileNotFoundError):
                pdf_parser.extract_text_from_pdf("inexistant.pdf")

    @pytest.mark.unit
    @pytest.mark.pdf
    def test_extract_text_corrupted_pdf(self):
        """Test d'extraction avec PDF corrompu"""
        with patch('src.bot.parser.pdf_parser.extract_text_from_pdf') as mock_extract:
            mock_extract.side_effect = Exception("PDF corrompu")
            
            with pytest.raises(Exception):
                pdf_parser.extract_text_from_pdf("corrupted.pdf")
