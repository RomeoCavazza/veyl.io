"""
Tests pour l'orchestrateur principal
Tests pour le traitement des briefs
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
    """Tests pour le traitement des briefs"""

    def test_process_brief_success(self):
        """Test le traitement réussi d'un brief."""
        sample_schema = {"type": "object", "properties": {"title": {"type": "string"}}}
        sample_brief_sections = {
            "title": "Test Brief",
            "problème": "Test Problem", 
            "objectives": ["Obj1", "Obj2"],
            "kpis": ["KPI1", "KPI2"]
        }
        
        with patch("src.bot.orchestrator.extract_text_from_pdf") as mock_extract, \
             patch("src.bot.orchestrator.extract_brief_sections") as mock_sections, \
             patch("src.bot.orchestrator.load_schema") as mock_load_schema:
        
            mock_extract.return_value = "Test text"
            mock_sections.return_value = sample_brief_sections
            mock_load_schema.return_value = sample_schema
            
            result = process_brief("test.pdf")
            
            # Vérifier que la fonction retourne un résultat
            assert result is not None
            assert isinstance(result, dict)
            mock_extract.assert_called_once_with("test.pdf")
            mock_sections.assert_called_once_with("Test text")
            # load_schema peut être appelé plusieurs fois, on vérifie juste qu'il est appelé
            assert mock_load_schema.called

    def test_process_brief_empty_pdf(self):
            """Test le traitement d'un PDF vide."""
            with patch("src.bot.orchestrator.extract_text_from_pdf", return_value=""):
                with pytest.raises(RuntimeError, match="document vide ou illisible"):
                    process_brief("test.pdf")

    def test_process_brief_no_sections(self):
        """Test le traitement d'un brief sans sections."""
        sample_schema = {"type": "object", "properties": {"title": {"type": "string"}}}
        
        with patch("src.bot.orchestrator.extract_text_from_pdf") as mock_extract, \
             patch("src.bot.orchestrator.extract_brief_sections") as mock_sections, \
             patch("src.bot.orchestrator.load_schema") as mock_load_schema:
        
            mock_extract.return_value = "Test text"
            mock_sections.return_value = {}
            mock_load_schema.return_value = sample_schema
            
            result = process_brief("test.pdf")
            
            # La fonction retourne des valeurs par défaut quand aucune section n'est trouvée
            assert result is not None
            assert isinstance(result, dict)

    def test_process_brief_validation_error(self):
        """Test le traitement d'un brief avec erreur de validation."""
        sample_brief_sections = {"title": "Test Brief"}
        
        with patch("src.bot.orchestrator.extract_text_from_pdf") as mock_extract, \
             patch("src.bot.orchestrator.extract_brief_sections") as mock_sections, \
             patch("src.bot.orchestrator.load_schema") as mock_load_schema, \
             patch("jsonschema.validate") as mock_validate:
        
            mock_extract.return_value = "Test text"
            mock_sections.return_value = sample_brief_sections
            mock_load_schema.return_value = {"type": "object"}
            mock_validate.side_effect = ValidationError("Validation failed")
            
            # La fonction peut gérer l'erreur de validation gracieusement
            result = process_brief("test.pdf")
            assert result is not None
            assert isinstance(result, dict)

    def test_process_brief_extraction_error(self):
            """Test l'échec de l'extraction du texte."""
            with patch("src.bot.orchestrator.extract_text_from_pdf", side_effect=Exception("Erreur d'extraction")):
                with pytest.raises(RuntimeError, match="Extraction PDF échouée"):
                    process_brief("test.pdf")

    def test_process_brief_with_validation(self):
        """Test le traitement d'un brief avec validation réussie."""
        sample_schema = {"type": "object", "properties": {"title": {"type": "string"}}}
        sample_brief_sections = {
            "title": "Test Brief",
            "problème": "Test Problem",
            "objectives": ["Obj1", "Obj2"],
            "kpis": ["KPI1", "KPI2"]
        }
        
        with patch("src.bot.orchestrator.extract_text_from_pdf") as mock_extract, \
             patch("src.bot.orchestrator.extract_brief_sections") as mock_sections, \
             patch("src.bot.orchestrator.load_schema") as mock_load_schema, \
             patch("jsonschema.validate") as mock_validate:
        
            mock_extract.return_value = "Test text"
            mock_sections.return_value = sample_brief_sections
            mock_load_schema.return_value = sample_schema
            mock_validate.return_value = None  # Validation réussie
            
            result = process_brief("test.pdf")
            
            assert result is not None
            assert isinstance(result, dict)


    def test_process_brief_empty_text(self, caplog):
            """Test avec un texte extrait vide."""
            with patch("src.bot.orchestrator.extract_text_from_pdf") as mock_extract:
                mock_extract.return_value = ""
                with pytest.raises(RuntimeError, match="document vide ou illisible"):
                    process_brief("test.pdf")


    def test_process_brief_malformed_json(self, caplog):
            """Test avec un JSON malformé dans les sections."""
            with patch("src.bot.orchestrator.extract_text_from_pdf") as mock_extract_text:
                with patch("src.bot.orchestrator.extract_brief_sections") as mock_extract_sections:
                    mock_extract_text.return_value = "test content"
                    mock_extract_sections.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
                
                    result = process_brief("test.pdf")
                
                    assert result["titre"] == "Brief extrait automatiquement"
                    assert result["problème"] == "Problème non précisé"
                    assert result["objectifs"] == ["Objectif non précisé"]
                    assert result["kpis"] == ["KPI non identifié"]


    def test_process_brief_invalid_json_structure(self, caplog):
            """Test avec une structure JSON invalide."""
            with patch("src.bot.orchestrator.extract_text_from_pdf") as mock_extract_text:
                with patch("src.bot.orchestrator.extract_brief_sections") as mock_extract_sections:
                    mock_extract_text.return_value = "test content"
                    mock_extract_sections.return_value = ["not", "a", "dict"]
                
                    result = process_brief("test.pdf")
                
                    assert result["titre"] == "Brief extrait automatiquement"
                    assert result["problème"] == "Problème non précisé"
                    assert result["objectifs"] == ["Objectif non précisé"]
                    assert result["kpis"] == ["KPI non identifié"]


    def test_process_brief_mixed_fr_en(self, caplog):
            """Test avec un mélange de clés en français et en anglais."""
            test_brief = {
                "title": "Test Brief",
                "problem": "Test Problem",
                "objectifs": ["Obj1", "Obj2"],
                "kpis": ["KPI1", "KPI2"]
            }
        
            with patch("src.bot.orchestrator.extract_text_from_pdf") as mock_extract_text:
                with patch("src.bot.orchestrator.extract_brief_sections") as mock_extract_sections:
                    with patch("src.bot.orchestrator.load_schema") as mock_load_schema:
                        mock_extract_text.return_value = "test content"
                        mock_extract_sections.return_value = test_brief
                        mock_load_schema.return_value = {
                            "type": "object",
                            "required": ["titre", "problème", "objectifs", "kpis"],
                            "properties": {
                                "titre": {"type": "string"},
                                "problème": {"type": "string"},
                                "objectifs": {"type": "array"},
                                "kpis": {"type": "array"}
                            }
                        }
                    
                        result = process_brief("test.pdf")
                    
                        assert result["titre"] == "Test Brief"
                        assert result["problème"] == "Test Problem"
                        assert result["objectifs"] == ["Obj1", "Obj2"]
                        assert result["kpis"] == ["KPI1", "KPI2"]


    def test_process_brief_partial_validation(self, caplog):
            """Test avec une validation partielle du schéma."""
            test_brief = {
                "titre": "Test Brief",
                "problème": "Test Problem",
                "objectifs": ["Obj1", "Obj2"],
                "kpis": ["KPI1", "KPI2"],
                "extra_field": "Should be ignored"
            }
        
            with patch("src.bot.orchestrator.extract_text_from_pdf") as mock_extract_text:
                with patch("src.bot.orchestrator.extract_brief_sections") as mock_extract_sections:
                    with patch("src.bot.orchestrator.load_schema") as mock_load_schema:
                        mock_extract_text.return_value = "test content"
                        mock_extract_sections.return_value = test_brief
                        mock_load_schema.return_value = {
                            "type": "object",
                            "required": ["titre", "problème", "objectifs", "kpis"],
                            "properties": {
                                "titre": {"type": "string"},
                                "problème": {"type": "string"},
                                "objectifs": {"type": "array"},
                                "kpis": {"type": "array"}
                            },
                            "additionalProperties": False
                        }
                    
                        result = process_brief("test.pdf")
                    
                        assert result["titre"] == "Test Brief"
                        assert result["problème"] == "Test Problem"
                        assert result["objectifs"] == ["Obj1", "Obj2"]
                        assert result["kpis"] == ["KPI1", "KPI2"]
                        assert "extra_field" not in result 


