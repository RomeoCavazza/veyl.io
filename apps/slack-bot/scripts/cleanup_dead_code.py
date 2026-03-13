#!/usr/bin/env python3
"""
NETTOYAGE AUTOMATIQUE DU CODE MORT
==================================

Supprime automatiquement toutes les fonctions inutilisées identifiées par l'audit.
"""

import json
import re
from pathlib import Path

class DeadCodeCleaner:
    """Nettoyeur automatique de code mort"""

    def __init__(self, audit_results_file: str = "audit_results.json"):
        self.audit_file = audit_results_file
        self.cleaned_count = 0

    def load_audit_results(self):
        """Charge les résultats d'audit"""
        with open(self.audit_file, 'r') as f:
            return json.load(f)

    def clean_all_dead_code(self):
        """Nettoie tout le code mort"""
        print("🧹 NETTOYAGE DU CODE MORT")
        print("=" * 40)

        results = self.load_audit_results()
        dead_functions = results['dead_code']['dead_functions']

        print(f"🔍 {len(dead_functions)} fonctions inutilisées à supprimer")

        # Grouper par fichier
        by_file = {}
        for func in dead_functions:
            file_path = func['file']
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(func['function'])

        # Nettoyer chaque fichier
        for file_path, functions in by_file.items():
            print(f"\n📁 Nettoyage de {file_path}")
            print(f"   • {len(functions)} fonctions à supprimer")
            self.clean_file(file_path, functions)

        print("\n✅ Nettoyage terminé !")
        print(f"   • {self.cleaned_count} fonctions supprimées")

    def clean_file(self, file_path: str, functions_to_remove: list):
        """Nettoie un fichier spécifique"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_lines = len(content.split('\n'))

            for func_name in functions_to_remove:
                # Pattern pour trouver et supprimer la fonction complète
                pattern = rf'def {re.escape(func_name)}\([^)]*\):.*?(?=\n\s*(?:def|\n\s*$))'
                content = re.sub(pattern, '', content, flags=re.DOTALL)

                # Supprimer aussi les méthodes de classe
                class_pattern = rf'\s+def {re.escape(func_name)}\([^)]*\):.*?(?=\n\s*(?:def|\n\s*$))'
                content = re.sub(class_pattern, '', content, flags=re.DOTALL)

                self.cleaned_count += 1

            # Nettoyer les lignes vides multiples
            content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)

            # Écrire le fichier nettoyé
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.strip() + '\n')

            final_lines = len(content.split('\n'))
            saved_lines = original_lines - final_lines
            print(f"   ✅ {saved_lines} lignes économisées")

        except Exception as e:
            print(f"   ❌ Erreur lors du nettoyage de {file_path}: {e}")

def main():
    """Fonction principale"""
    cleaner = DeadCodeCleaner()
    cleaner.clean_all_dead_code()

    # Vérifier les métriques après nettoyage
    print("\n📊 MÉTRIQUES APRÈS NETTOYAGE:")
    import subprocess
    result = subprocess.run(['find', 'src/', '-name', '*.py', '-exec', 'wc', '-l', '{}', '+'],
                          capture_output=True, text=True)
    total_lines = sum(int(line.split()[0]) for line in result.stdout.split('\n') if line.strip())
    print(f"   • Lignes totales: {total_lines}")

if __name__ == "__main__":
    main()