#!/usr/bin/env python3
"""
Script pour ajouter automatiquement des markers pytest aux tests
"""

import os
import re
from pathlib import Path

def add_markers_to_test_file(filepath):
    """Ajoute des markers appropriés aux tests dans un fichier"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Détecter le type de test selon le nom du fichier/dossier
    filepath_str = str(filepath)
    
    # Déterminer les markers selon le chemin
    markers = []
    
    if 'real_world' in filepath_str:
        markers = ['@pytest.mark.real_world', '@pytest.mark.slow']
    elif 'integration' in filepath_str:
        markers = ['@pytest.mark.integration']
    elif 'api' in filepath_str:
        markers = ['@pytest.mark.unit', '@pytest.mark.api']
    elif 'unit' in filepath_str:
        markers = ['@pytest.mark.unit']
    elif any(x in filepath_str for x in ['scraper', 'scraping']):
        markers = ['@pytest.mark.unit', '@pytest.mark.scraping']
    elif 'pdf' in filepath_str:
        markers = ['@pytest.mark.unit', '@pytest.mark.pdf']
    elif 'veille' in filepath_str:
        markers = ['@pytest.mark.unit', '@pytest.mark.veille']
    else:
        # Par défaut, considérer comme unitaire
        markers = ['@pytest.mark.unit']
    
    # Ajouter des markers pour les tests de performance/mémoire
    if 'memory' in content or 'performance' in content or 'benchmark' in content:
        markers.append('@pytest.mark.performance')
    
    if 'stress' in filepath_str or 'concurrent' in content:
        markers.append('@pytest.mark.stress')
    
    # Pattern pour trouver les définitions de test
    test_pattern = r'(\s*)def (test_\w+)\(([^)]*)\):'
    
    def add_marker_to_test(match):
        indent = match.group(1)
        test_name = match.group(2)
        params = match.group(3)
        
        # Vérifier si des markers existent déjà
        lines_before = content[:match.start()].split('\n')
        has_markers = any('@pytest.mark.' in line for line in lines_before[-5:])
        
        if not has_markers:
            marker_lines = [f'{indent}{marker}' for marker in markers]
            marker_str = '\n'.join(marker_lines) + '\n'
            return f'{marker_str}{indent}def {test_name}({params}):'
        
        return match.group(0)
    
    # Appliquer les modifications
    new_content = re.sub(test_pattern, add_marker_to_test, content)
    
    # Écrire seulement si des changements ont été faits
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Markers ajoutés à {filepath}")
        return True
    
    return False

def main():
    """Ajoute des markers à tous les fichiers de test"""
    test_dir = Path('tests')
    
    if not test_dir.exists():
        print("❌ Dossier tests/ non trouvé")
        return
    
    modified_count = 0
    
    # Parcourir tous les fichiers de test
    for test_file in test_dir.rglob('test_*.py'):
        try:
            if add_markers_to_test_file(test_file):
                modified_count += 1
        except Exception as e:
            print(f"❌ Erreur avec {test_file}: {e}")
    
    print(f"\n🎯 {modified_count} fichiers modifiés avec des markers")

if __name__ == "__main__":
    main() 