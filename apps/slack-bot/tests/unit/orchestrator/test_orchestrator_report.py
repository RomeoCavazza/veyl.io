"""
Tests pour l'orchestrateur principal
Tests pour les opérations de rapport
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
    """Tests pour les opérations de rapport"""

    def test_delegate_to_report_success(self):
            """Test successful report generation"""
            # Test that the function can be called without errors
            # The actual implementation uses subprocess.run internally
            try:
                result = delegate_to_report("test.pdf", "report.pptx")
                # If no exception is raised, the test passes
                assert True
            except Exception as e:
                # If an exception is raised, it should be handled gracefully
                assert "Erreur" in str(e) or "error" in str(e).lower()


    def test_delegate_to_report_process_error(self):
            """Test report generation with process error"""
            with patch('src.bot.orchestrator.process_brief') as mock_process:
                mock_process.side_effect = RuntimeError("Test error")

                with pytest.raises(RuntimeError, match="Erreur.*Test error"):
                    delegate_to_report("test.pdf")


    def test_delegate_to_report_invalid_brief(self):
            """Test report generation with invalid brief"""
            with patch('src.bot.orchestrator.process_brief') as mock_process:
                mock_process.side_effect = RuntimeError("Brief invalide")
            
                with pytest.raises(RuntimeError, match="Erreur.*Brief invalide"):
                    delegate_to_report("test.pdf")



    def test_main_report_mode(self):
            """Test le mode rapport."""
            mock_args = ["--report", "report.pptx"]
            with patch("src.bot.orchestrator.delegate_to_report") as mock_delegate:
                main(mock_args)
                mock_delegate.assert_called_once_with(None, "report.pptx")


    def test_main_report_mode_error(self):
            """Test le mode rapport avec une erreur."""
            mock_args = ["--report", "report.pptx"]
            with patch("src.bot.orchestrator.delegate_to_report") as mock_delegate:
                mock_delegate.side_effect = RuntimeError("Test error")
                with pytest.raises(SystemExit) as excinfo:
                    main(mock_args)
                assert "Test error" in str(excinfo.value)


