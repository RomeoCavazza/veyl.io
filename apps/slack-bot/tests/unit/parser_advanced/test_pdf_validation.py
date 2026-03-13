import pytest
import sys
import os
from unittest.mock import patch, Mock

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from src.bot.parser.pdf_parser import validate_pdf_file


class TestPDFValidation:
    """Tests pour la validation des fichiers PDF"""

    def test_validate_pdf_file_valid(self):
        """Test validation avec fichier PDF valide"""
        with patch('os.path.exists', return_value=True):
            result = validate_pdf_file("test.pdf")
            assert result is True
            print("✅ Test validate_pdf_file valid")

    def test_validate_pdf_file_not_exists(self):
        """Test validation avec fichier inexistant"""
        with patch('os.path.exists', return_value=False):
            result = validate_pdf_file("nonexistent.pdf")
            assert result is False
            print("✅ Test validate_pdf_file not exists")

    def test_validate_pdf_file_wrong_extension(self):
        """Test validation avec mauvaise extension"""
        with patch('os.path.exists', return_value=True):
            result = validate_pdf_file("test.txt")
            assert result is False
            print("✅ Test validate_pdf_file wrong extension")

    def test_validate_pdf_file_case_insensitive(self):
        """Test validation insensible à la casse"""
        with patch('os.path.exists', return_value=True):
            result = validate_pdf_file("test.PDF")
            assert result is True
            print("✅ Test validate_pdf_file case insensitive") 