#!/usr/bin/env python3
"""
Script pour corriger les imports pytest manquants
"""

import os
import re
from pathlib import Path

def fix_pytest_imports(filepath):
    """Ajoute l'import pytest si nécessaire"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si pytest.mark est utilisé mais pytest n'est pas importé
    has_pytest_mark = '@pytest.mark.' in content
    has_pytest_import = re.search(r'^import pytest', content, re.MULTILINE) or \
                       re.search(r'^from pytest', content, re.MULTILINE)
    
    if has_pytest_mark and not has_pytest_import:
        # Trouver où insérer l'import
        lines = content.split('\n')
        
        # Chercher après les docstrings et avant les autres imports
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') and '"""' in line[3:]:
                # Docstring sur une ligne
                insert_pos = i + 1
                break
            elif line.strip().startswith('"""'):
                # Début de docstring multi-ligne
                for j in range(i + 1, len(lines)):
                    if '"""' in lines[j]:
                        insert_pos = j + 1
                        break
                break
            elif line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_pos = i
                break
        
        # Insérer l'import pytest
        lines.insert(insert_pos, 'import pytest')
        if insert_pos < len(lines) - 1 and lines[insert_pos + 1].strip():
            lines.insert(insert_pos + 1, '')  # Ligne vide après l'import
        
        new_content = '\n'.join(lines)
        
        # Écrire le fichier modifié
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Import pytest ajouté à {filepath}")
        return True
    
    return False

def main():
    """Corrige les imports pytest dans tous les fichiers de test"""
    test_dir = Path('tests')
    
    if not test_dir.exists():
        print("❌ Dossier tests/ non trouvé")
        return
    
    fixed_count = 0
    
    # Parcourir tous les fichiers de test
    for test_file in test_dir.rglob('test_*.py'):
        try:
            if fix_pytest_imports(test_file):
                fixed_count += 1
        except Exception as e:
            print(f"❌ Erreur avec {test_file}: {e}")
    
    print(f"\n🎯 {fixed_count} fichiers corrigés avec l'import pytest")

if __name__ == "__main__":
    main() 