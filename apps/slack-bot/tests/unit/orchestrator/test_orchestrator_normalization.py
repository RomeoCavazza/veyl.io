"""
Tests pour l'orchestrateur principal
Tests pour la normalisation
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
    """Tests pour la normalisation"""

    def test_normalize_keys_basic(self):
            """Test la normalisation basique des clés."""
            input_dict = {"title": "Test", "objectives": ["obj1", "obj2"]}
            expected = {"titre": "Test", "objectifs": ["obj1", "obj2"]}
            result = normalize_keys(input_dict)
            assert result == expected


    def test_normalize_keys_no_changes_needed(self):
            """Test quand aucun changement n'est nécessaire."""
            input_dict = {"titre": "Test", "objectifs": ["obj1"]}
            result = normalize_keys(input_dict)
            assert result == input_dict


    def test_normalize_keys_invalid_input(self):
            """Test avec une entrée invalide."""
            with pytest.raises(RuntimeError, match="sections doit être un dictionnaire"):
                normalize_keys("not a dict")


    def test_normalize_keys_mixed_keys(self):
            """Test avec un mélange de clés en français et en anglais."""
            input_dict = {
                "title": "Test",
                "objectifs": ["obj1"],
                "problem": "Issue",
                "kpis": ["KPI1"],
                "budget": "1000€"
            }
            expected = {
                "titre": "Test",
                "objectifs": ["obj1"],
                "problème": "Issue",
                "kpis": ["KPI1"],
                "budget": "1000€"
            }
            result = normalize_keys(input_dict)
            assert result == expected


    def test_normalize_keys_empty_dict(self):
            """Test avec un dictionnaire vide."""
            result = normalize_keys({})
            assert result == {}


    def test_normalize_keys_nested_dict(self):
            """Test avec un dictionnaire imbriqué."""
            input_dict = {
                "title": "Test",
                "objectives": {
                    "primary": ["obj1"],
                    "secondary": ["obj2"]
                }
            }
            expected = {
                "titre": "Test",
                "objectifs": {
                    "primary": ["obj1"],
                    "secondary": ["obj2"]
                }
            }
            result = normalize_keys(input_dict)
            assert result == expected


    def test_normalize_keys_with_none_values(self):
            """Test avec des valeurs None."""
            input_dict = {
                "title": None,
                "objectives": None
            }
            expected = {
                "titre": None,
                "objectifs": None
            }
            result = normalize_keys(input_dict)
            assert result == expected 


