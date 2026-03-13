"""
Tests pour l'orchestrateur principal
Tests pour les opérations d'analyse
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
    """Tests pour les opérations d'analyse"""

    def test_run_analyse_success(self, tmp_path):
            """Test l'analyse réussie des données de veille."""
            # Création du fichier CSV de test
            csv_path = tmp_path / "veille.csv"
            test_data = [{
                "title": "Test Article",
                "link": "http://test.com/article",  # URL de test
                "published": "2026-07-12",
                "source": "Test Source",
                "content": "Test content for analysis"
            }]
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["title", "link", "published", "source", "content"])
                writer.writeheader()
                writer.writerows(test_data)
        
            with patch("src.bot.orchestrator.summarize_items") as mock_summarize:
                with patch("src.bot.orchestrator.detect_trends") as mock_trends:
                    mock_summarize.return_value = "Test Summary"
                    mock_trends.return_value = ["Trend 1"]
                
                    result = run_analyse(str(csv_path))
                
                    mock_summarize.assert_called_once_with(test_data)
                    mock_trends.assert_called_once_with(test_data)
                    assert result["summary"] == "Test Summary"
                    assert result["trends"] == ["Trend 1"]
                    assert result["items"] == test_data


    def test_run_analyse_empty_file(self, tmp_path):
            """Test avec un fichier de veille vide."""
            # Création d'un fichier CSV vide
            csv_path = tmp_path / "empty_veille.csv"
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["title", "link", "published", "source", "content"])
                writer.writeheader()
        
            with patch("src.bot.orchestrator.summarize_items") as mock_summarize:
                with patch("src.bot.orchestrator.detect_trends") as mock_trends:
                    mock_summarize.return_value = "Empty Summary"
                    mock_trends.return_value = []
                
                    result = run_analyse(str(csv_path))
                
                    mock_summarize.assert_called_once_with([])
                    mock_trends.assert_called_once_with([])
                    assert result["summary"] == "Empty Summary"
                    assert result["trends"] == []
                    assert result["items"] == []


    def test_run_analyse_file_not_found(self):
            """Test avec un fichier de veille inexistant."""
            with pytest.raises(FileNotFoundError):
                run_analyse("nonexistent.csv")


    def test_run_analyse_invalid_csv(self, tmp_path):
            """Test avec un fichier CSV invalide."""
            csv_path = tmp_path / "invalid.csv"
            csv_path.write_text("invalid,csv,content\nwithout,proper,headers")
        
            with pytest.raises(RuntimeError, match="Format CSV invalide"):
                run_analyse(str(csv_path))


    def test_run_analyse_summarize_error(self, tmp_path):
            """Test avec une erreur lors de la génération du résumé."""
            csv_path = tmp_path / "veille.csv"
            test_data = [{
                "title": "Test Article",
                "link": "http://test.com/article",  # URL de test
                "published": "2026-07-12",
                "source": "Test Source",
                "content": "Test content for analysis"
            }]
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["title", "link", "published", "source", "content"])
                writer.writeheader()
                writer.writerows(test_data)
        
            with patch("src.bot.orchestrator.summarize_items") as mock_summarize:
                mock_summarize.side_effect = Exception("Erreur de résumé")
                with pytest.raises(RuntimeError, match="Erreur lors de la génération du résumé"):
                    run_analyse(str(csv_path))


    def test_run_analyse_trends_error(self, tmp_path):
            """Test avec une erreur lors de la détection des tendances."""
            csv_path = tmp_path / "veille.csv"
            test_data = [{
                "title": "Test Article",
                "link": "http://test.com/article",  # URL de test
                "published": "2026-07-12",
                "source": "Test Source",
                "content": "Test content for analysis"
            }]
            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["title", "link", "published", "source", "content"])
                writer.writeheader()
                writer.writerows(test_data)
        
            with patch("src.bot.orchestrator.summarize_items") as mock_summarize:
                with patch("src.bot.orchestrator.detect_trends") as mock_trends:
                    mock_summarize.return_value = "Test Summary"
                    mock_trends.side_effect = Exception("Erreur de tendances")
                    with pytest.raises(RuntimeError, match="Erreur lors de la génération du résumé"):
                        run_analyse(str(csv_path)) 


    def test_main_analyse_mode(self):
            """Test l'exécution en mode analyse."""
            mock_args = ["--analyse", "veille.csv"]
            with patch("src.bot.orchestrator.run_analyse") as mock_analyse:
                main(mock_args)
                mock_analyse.assert_called_once_with("veille.csv")


    def test_main_analyse_mode_error(self):
            """Test l'exécution en mode analyse avec une erreur."""
            mock_args = ["--analyse", "veille.csv"]
            with patch("src.bot.orchestrator.run_analyse") as mock_analyse:
                mock_analyse.side_effect = RuntimeError("Test error")
                with pytest.raises(SystemExit) as excinfo:
                    main(mock_args)
                assert "Test error" in str(excinfo.value)


