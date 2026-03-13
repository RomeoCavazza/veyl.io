"""
Tests pour l'orchestrateur principal
Tests pour les opérations principales
"""

import csv
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import subprocess

import pytest
from jsonschema import ValidationError

from src.bot.schema.validator import load_schema
from src.bot.orchestrator import (
    normalize_keys,
    process_brief,
    run_veille,
    run_analyse,
    delegate_to_report,
    main,
)
from src.bot.utils.logger import logger


class TestOrchestrator:
    """Tests pour les opérations principales"""

    def test_main_brief_mode(self):
        """Test le mode brief."""
        test_pdf_path = "test_brief.pdf"
        mock_args = ["--brief", test_pdf_path]
        with patch("src.bot.orchestrator.process_brief") as mock_process, \
             patch("src.bot.orchestrator.delegate_to_report") as mock_delegate, \
             patch("src.bot.orchestrator.run_veille") as mock_veille, \
             patch("src.bot.orchestrator.run_analyse") as mock_analyse:
            mock_process.return_value = {"title": "Test"}
            main(mock_args)
            mock_process.assert_called_once_with(test_pdf_path)

    def test_main_no_mode_selected(self):
        """Test sans mode sélectionné."""
        mock_args = []
        with pytest.raises(RuntimeError, match="Aucun mode sélectionné"):
            main(mock_args)

    def test_main_multiple_modes(self):
        """Test avec plusieurs modes spécifiés."""
        test_pdf_path = "test_brief.pdf"
        mock_args = [
            "--brief", test_pdf_path,
            "--report", "report.pptx"
        ]
        with patch("src.bot.orchestrator.process_brief") as mock_process, \
             patch("src.bot.orchestrator.delegate_to_report") as mock_delegate, \
             patch("src.bot.orchestrator.run_veille") as mock_veille, \
             patch("src.bot.orchestrator.run_analyse") as mock_analyse:
            mock_process.return_value = {"title": "Test"}
            main(mock_args)
            mock_process.assert_called_once_with(test_pdf_path)
            mock_delegate.assert_called_once_with(test_pdf_path, "report.pptx")

    def test_main_brief_mode_error(self):
        """Test le mode brief avec erreur."""
        test_pdf_path = "test_brief.pdf"
        mock_args = ["--brief", test_pdf_path]
        with patch("src.bot.orchestrator.process_brief") as mock_process:
            mock_process.side_effect = RuntimeError("Test error")
            with pytest.raises(SystemExit) as excinfo:
                main(mock_args)
            assert "Test error" in str(excinfo.value)


    def test_main_invalid_file_paths(self):
        """Test avec chemins de fichiers invalides."""
        mock_args = ["--brief", "nonexistent.pdf"]
        with patch("src.bot.orchestrator.process_brief") as mock_process:
            mock_process.side_effect = FileNotFoundError("File not found")
            with pytest.raises(SystemExit):
                main(mock_args) 

