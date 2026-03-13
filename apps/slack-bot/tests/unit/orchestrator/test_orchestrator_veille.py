"""
Tests pour l'orchestrateur principal
Tests pour les opérations de veille
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
    """Tests pour les opérations de veille"""

    def test_run_veille_success(self, tmp_path):
            """Test l'exécution réussie de la veille."""
            test_items = [{"title": "Test", "url": "http://test.com"}]  # URL de test
            output_path = str(tmp_path / "test_veille.csv")
        
            with patch("src.bot.orchestrator.fetch_all_sources") as mock_fetch:
                mock_fetch.return_value = test_items
                result = run_veille(output_path)
            
                assert result == test_items
                assert Path(output_path).exists()
            
                # Vérification du contenu CSV
                with open(output_path, newline="") as f:
                    reader = csv.DictReader(f)
                    saved_items = list(reader)
                    assert len(saved_items) == 1
                    assert saved_items[0]["title"] == "Test"
                    assert saved_items[0]["url"] == "http://test.com"  # URL de test


    def test_run_veille_empty_results(self, tmp_path):
            """Test avec aucun résultat de veille."""
            output_path = str(tmp_path / "empty_veille.csv")
        
            with patch("src.bot.orchestrator.fetch_all_sources") as mock_fetch:
                mock_fetch.return_value = []
                result = run_veille(output_path)
            
                assert result == []
                assert Path(output_path).exists()
            
                with open(output_path, newline="") as f:
                    reader = csv.DictReader(f)
                    assert list(reader) == []


    def test_run_veille_permission_error(self, tmp_path):
            """Test avec une erreur de permission lors de l'écriture."""
            test_items = [{"title": "Test", "url": "http://test.com"}]  # URL de test
            output_path = str(tmp_path / "test_veille.csv")
        
            with patch("src.bot.orchestrator.fetch_all_sources") as mock_fetch:
                mock_fetch.return_value = test_items
                with patch("builtins.open", side_effect=PermissionError):
                    with pytest.raises(RuntimeError, match="Erreur lors de l'écriture"):
                        run_veille(output_path)


    def test_run_veille_fetch_error(self, tmp_path):
            """Test avec une erreur lors de la récupération des sources."""
            output_path = str(tmp_path / "test_veille.csv")
        
            with patch("src.bot.orchestrator.fetch_all_sources") as mock_fetch:
                mock_fetch.side_effect = Exception("Erreur de récupération")
                with pytest.raises(RuntimeError, match="Erreur lors de la récupération"):
                    run_veille(output_path)



    def test_main_veille_mode(self):
            """Test l'exécution en mode veille."""
            mock_args = ["--veille", "veille.csv"]
            with patch("src.bot.orchestrator.run_veille") as mock_veille:
                main(mock_args)
                mock_veille.assert_called_once_with("veille.csv")


    def test_main_veille_mode_error(self):
            """Test l'exécution en mode veille avec une erreur."""
            mock_args = ["--veille", "veille.csv"]
            with patch("src.bot.orchestrator.run_veille") as mock_veille:
                mock_veille.side_effect = RuntimeError("Test error")
                with pytest.raises(SystemExit) as excinfo:
                    main(mock_args)
                assert "Test error" in str(excinfo.value)


