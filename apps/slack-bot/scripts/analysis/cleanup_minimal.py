#!/usr/bin/env python3
"""
Script de nettoyage pour créer une structure minimale et fonctionnelle.
Garde seulement les briques essentielles : PDF, IA, Veille, Slides.
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Nettoie le projet pour garder seulement les briques essentielles."""
    
    # Dossiers à supprimer (non essentiels)
    dirs_to_remove = [
        "src/bot/analysis.py",
        "src/bot/orchestrator.py", 
        "src/bot/slack_bot.py",
        "src/bot/slack_handler.py",
        "src/bot/slack_events_handler.py",
        "src/bot/slack_events_endpoint.py",
        "src/bot/email_handler.py",
        "src/bot/reco_api.py",
        "src/bot/decorators.py",
        "src/bot/exceptions.py",
        "src/bot/config.py",
        "src/bot/__main__.py",
        "src/bot/schemas.py",
        "src/bot/veille.py",
        "src/bot/veille_api.py",
        "src/api/",
        "src/bot/cli/",
        "src/bot/config/",
        "src/bot/monitoring/",
        "src/bot/reco/",
        "src/bot/schemas/",
        "src/bot/security/",
        "src/bot/slack/",
        "src/bot/utils/",
        "src/config/",
        "src/utils/",
        "tests/test_production_config.py",
        "tests/test_revolver_complete.py",
        "tests/test_generic_bot.py",
        "tests/test_minimal.py",
        "tests/test_pdf_simple.py",
        "test_simple_integration.py",
        "run_parser.py",
        "test_revolver_complete.py",
        "test_generic_bot.py",
        "test_minimal.py",
        "test_pdf_simple.py",
        "test_simple_integration.py",
        "run_parser.py"
    ]
    
    # Fichiers à supprimer
    files_to_remove = [
        "src/bot/analysis.py",
        "src/bot/orchestrator.py", 
        "src/bot/slack_bot.py",
        "src/bot/slack_handler.py",
        "src/bot/slack_events_handler.py",
        "src/bot/slack_events_endpoint.py",
        "src/bot/email_handler.py",
        "src/bot/reco_api.py",
        "src/bot/decorators.py",
        "src/bot/exceptions.py",
        "src/bot/config.py",
        "src/bot/__main__.py",
        "src/bot/schemas.py",
        "src/bot/veille.py",
        "src/bot/veille_api.py",
        "tests/test_production_config.py",
        "tests/test_revolver_complete.py",
        "tests/test_generic_bot.py",
        "tests/test_minimal.py",
        "tests/test_pdf_simple.py",
        "test_simple_integration.py",
        "run_parser.py",
        "test_revolver_complete.py",
        "test_generic_bot.py",
        "test_minimal.py",
        "test_pdf_simple.py",
        "test_simple_integration.py",
        "run_parser.py"
    ]
    
    print("🧹 Nettoyage du projet...")
    
    # Supprimer les fichiers
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🗑️ Supprimé: {file_path}")
            except Exception as e:
                print(f"❌ Erreur suppression {file_path}: {e}")
    
    # Supprimer les dossiers
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"🗑️ Supprimé: {dir_path}")
            except Exception as e:
                print(f"❌ Erreur suppression {dir_path}: {e}")
    
    print("✅ Nettoyage terminé")

def create_minimal_structure():
    """Crée la structure minimale finale."""
    
    # Structure minimale à garder
    minimal_structure = {
        "src/bot/": [
            "__init__.py",
            "ai/__init__.py",
            "ai/brief_summarizer.py", 
            "ai/openai_client.py",
            "parser/__init__.py",
            "parser/pdf_parser.py",
            "veille/__init__.py", 
            "veille/veilleur.py",
            "slides/__init__.py",
            "slides/builder.py"
        ],
        "tests/": [
            "ai/test_brief_summarizer.py",
            "parser/test_pdf_parser.py", 
            "veille/test_veilleur.py",
            "slides/test_builder.py"
        ]
    }
    
    print("\n📁 Structure minimale finale:")
    for base_dir, files in minimal_structure.items():
        print(f"\n{base_dir}")
        for file in files:
            full_path = os.path.join(base_dir, file)
            if os.path.exists(full_path):
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file} (MANQUANT)")

if __name__ == "__main__":
    cleanup_project()
    create_minimal_structure() 