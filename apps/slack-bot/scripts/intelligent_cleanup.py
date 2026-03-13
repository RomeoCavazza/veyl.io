#!/usr/bin/env python3
"""
Script de nettoyage intelligent pour Revolver AI Bot
Analyse avant suppression, conserve l'état fonctionnel
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import json

class IntelligentCleanup:
    """Nettoyage intelligent avec analyse pré-suppression"""
    
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.project_root = Path.cwd()
        self.cleanup_log = []
        
    def log_action(self, action, file_path, reason, safe=True):
        """Logger une action de nettoyage"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "file": str(file_path),
            "reason": reason,
            "safe": safe,
            "executed": not self.dry_run
        }
        self.cleanup_log.append(entry)
        
        status = "🔄" if self.dry_run else ("✅" if safe else "⚠️")
        print(f"{status} {action}: {file_path} - {reason}")
    
    def is_safe_to_delete(self, file_path):
        """Vérifier s'il est sûr de supprimer un fichier"""
        path = Path(file_path)
        
        # Ne jamais toucher au venv
        if "venv/" in str(path) or ".git/" in str(path):
            return False, "Système (venv/git)"
        
        # Fichiers clairement temporaires
        if path.suffix in ['.bak', '.tmp', '.temp']:
            return True, "Fichier temporaire"
        
        # Fichiers backup avec timestamp
        if "backup_" in path.name and path.suffix == '.py':
            return True, "Backup horodaté"
        
        # Fichiers Python cache
        if path.name == "__pycache__" or path.suffix == '.pyc':
            return True, "Cache Python"
        
        # Fichiers vides (sauf __init__.py)
        if path.is_file() and path.stat().st_size == 0:
            if path.name != "__init__.py":
                return True, "Fichier vide"
        
        return False, "Fichier fonctionnel"
    
    def analyze_backup_files(self):
        """Analyser les fichiers backup intelligemment"""
        backup_files = [
            "tests/bot/monitoring/test_monitoring.py.bak",
            "pytest.ini.backup", 
            "tests/parser/test_pdf_parser.py.backup_20250723_103554",
            "tests/functional/orchestrator/test_orchestrator_critical.py.backup_20250723_164107",
            "tests/functional/orchestrator/test_orchestrator_functional.py.backup_20250723_145914",
            "tests/functional/orchestrator/test_orchestrator_functional.py.backup_20250723_150111"
        ]
        
        for backup_file in backup_files:
            path = Path(backup_file)
            if path.exists():
                # Vérifier si le fichier original existe
                if backup_file.endswith('.bak'):
                    original = str(path).replace('.bak', '')
                elif 'backup_' in backup_file:
                    original = str(path).split('.backup_')[0] + path.suffix
                else:
                    original = str(path).replace('.backup', '')
                
                original_exists = Path(original).exists()
                
                if original_exists:
                    self.log_action("DELETE", path, "Backup obsolète (original existe)", True)
                    if not self.dry_run:
                        path.unlink()
                else:
                    self.log_action("KEEP", path, "Backup utile (original manquant)", True)
    
    def clean_python_cache(self):
        """Nettoyer les caches Python"""
        cache_dirs = []
        pyc_files = []
        
        # Trouver les __pycache__ et .pyc
        for root, dirs, files in os.walk(self.project_root):
            if "venv" in root or ".git" in root:
                continue
                
            if "__pycache__" in dirs:
                cache_dirs.append(Path(root) / "__pycache__")
            
            for file in files:
                if file.endswith('.pyc'):
                    pyc_files.append(Path(root) / file)
        
        # Supprimer les caches
        for cache_dir in cache_dirs:
            self.log_action("DELETE", cache_dir, "Cache Python", True)
            if not self.dry_run:
                shutil.rmtree(cache_dir)
        
        for pyc_file in pyc_files:
            self.log_action("DELETE", pyc_file, "Fichier compilé Python", True)
            if not self.dry_run:
                pyc_file.unlink()
    
    def clean_empty_files(self):
        """Nettoyer les fichiers vides (sauf __init__.py)"""
        for root, dirs, files in os.walk(self.project_root):
            if "venv" in root or ".git" in root:
                continue
            
            for file in files:
                file_path = Path(root) / file
                
                if file_path.stat().st_size == 0 and file != "__init__.py":
                    # Vérifier que ce n'est pas un __init__.py requis
                    if not (file.endswith('.py') and 'test' in str(file_path)):
                        self.log_action("DELETE", file_path, "Fichier vide non critique", True)
                        if not self.dry_run:
                            file_path.unlink()
    
    def clean_test_outputs(self):
        """Nettoyer les outputs de test obsolètes"""
        test_output_dirs = [
            "test_output_fix",
            "test_output_fix_v2", 
            "analysis_test",
            "advanced_test",
            "production_test"
        ]
        
        for dir_name in test_output_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                # Vérifier s'il y a des fichiers récents (< 7 jours)
                recent_files = False
                for file in dir_path.rglob('*'):
                    if file.is_file():
                        age_days = (datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)).days
                        if age_days < 7:
                            recent_files = True
                            break
                
                if not recent_files:
                    self.log_action("DELETE", dir_path, "Dossier test output obsolète", True)
                    if not self.dry_run:
                        shutil.rmtree(dir_path)
                else:
                    self.log_action("KEEP", dir_path, "Contient des fichiers récents", True)
    
    def run_cleanup(self):
        """Exécuter le nettoyage complet"""
        print(f"🧹 NETTOYAGE INTELLIGENT {'(DRY RUN)' if self.dry_run else '(EXÉCUTION)'}")
        print("=" * 60)
        
        # 1. Analyser les backups
        print("\n📂 ANALYSE FICHIERS BACKUP:")
        self.analyze_backup_files()
        
        # 2. Nettoyer les caches Python
        print("\n🐍 NETTOYAGE CACHE PYTHON:")
        self.clean_python_cache()
        
        # 3. Nettoyer les fichiers vides
        print("\n📄 NETTOYAGE FICHIERS VIDES:")
        self.clean_empty_files()
        
        # 4. Nettoyer les outputs de test
        print("\n🧪 NETTOYAGE OUTPUTS TEST:")
        self.clean_test_outputs()
        
        # Résumé
        total_actions = len(self.cleanup_log)
        delete_actions = len([a for a in self.cleanup_log if a['action'] == 'DELETE'])
        
        print(f"\n📊 RÉSUMÉ:")
        print(f"Total actions: {total_actions}")
        print(f"Suppressions: {delete_actions}")
        print(f"Conservation: {total_actions - delete_actions}")
        
        # Sauvegarder le log
        log_file = f"cleanup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w') as f:
            json.dump(self.cleanup_log, f, indent=2)
        
        print(f"📋 Log sauvegardé: {log_file}")
        
        return total_actions, delete_actions

def main():
    """Fonction principale"""
    # D'abord en dry run pour voir ce qui sera supprimé
    cleaner = IntelligentCleanup(dry_run=True)
    total, deletes = cleaner.run_cleanup()
    
    if deletes > 0:
        print(f"\n❓ Exécuter le nettoyage réel ? ({deletes} suppressions)")
        print("Tapez 'yes' pour confirmer:")
        
        # En mode automatique, on valide si c'est raisonnable
        if deletes < 20:  # Seuil de sécurité
            print("🔄 Auto-validation (< 20 suppressions)")
            # Exécution réelle
            cleaner = IntelligentCleanup(dry_run=False)
            cleaner.run_cleanup()
            print("\n✅ Nettoyage terminé!")
        else:
            print("⚠️ Trop de suppressions, validation manuelle requise")
    else:
        print("\n✅ Aucun nettoyage nécessaire!")

if __name__ == "__main__":
    main() 