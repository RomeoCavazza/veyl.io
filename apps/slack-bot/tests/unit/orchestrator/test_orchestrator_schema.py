"""
Tests pour l'orchestrateur principal
Tests pour les opérations de schéma
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
    """Tests pour les opérations de schéma"""

    def test_load_schema_success(self, tmp_path):
            """Test le chargement réussi du schéma."""
            schema_dir = tmp_path / "schema"
            schema_dir.mkdir()
            schema_file = schema_dir / "brief_schema.json"
        
            # Use the actual schema format instead of the test schema
            actual_schema = {
                "type": "object",
                "required": ["titre", "problème", "objectifs", "kpis"],
                "properties": {
                    "titre": {
                        "type": "string",
                        "minLength": 1
                    },
                    "problème": {
                        "type": "string",
                        "minLength": 1
                    },
                    "objectifs": {
                        "oneOf": [
                            {
                                "type": "string",
                                "minLength": 1
                            },
                            {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "minLength": 1
                                },
                                "minItems": 1
                            }
                        ]
                    },
                    "kpis": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "minLength": 1
                        },
                        "minItems": 1
                    },
                    "budget": {
                        "type": "string"
                    },
                    "deadline": {
                        "type": "string"
                    },
                    "contexte": {
                        "type": "string"
                    },
                    "contraintes": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "additionalProperties": False
            }
        
            schema_file.write_text(json.dumps(actual_schema))
        
            mock_parents = MagicMock()
            mock_parents.__getitem__.return_value = tmp_path
        
            with patch("pathlib.Path.resolve") as mock_resolve:
                mock_resolve.return_value.parents = mock_parents
                result = load_schema()
                assert result == actual_schema


    def test_load_schema_file_not_found(self):
            """Test la gestion d'un fichier de schéma manquant."""
            with patch("pathlib.Path.exists", return_value=False):
                with pytest.raises(FileNotFoundError):
                    load_schema()


    def test_load_schema_invalid_json(self, tmp_path):
            """Test la gestion d'un fichier JSON invalide."""
            with patch("pathlib.Path.exists", return_value=True), \
                 patch("builtins.open", mock_open(read_data="invalid json")):
                with pytest.raises(json.JSONDecodeError):
                    load_schema()


    def test_load_schema_empty_file(self, tmp_path):
            """Test la gestion d'un fichier vide."""
            with patch("pathlib.Path.exists", return_value=True), \
                 patch("builtins.open", mock_open(read_data="")):
                with pytest.raises(json.JSONDecodeError):
                    load_schema()


    def test_load_schema_permission_error(self, tmp_path):
            """Test la gestion d'une erreur de permission."""
            with patch("pathlib.Path.exists", return_value=True), \
                 patch("builtins.open", side_effect=PermissionError):
                with pytest.raises(PermissionError):
                    load_schema()



