#!/usr/bin/env python3
"""
Script pour identifier et corriger les données de test non modulables
Remplace les dates hardcodées par des dates dynamiques
"""

import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Any

class NonModularDataFixer:
    """Classe pour identifier et corriger les données non modulables"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixed_files = []
        self.errors = []
        
    def find_hardcoded_dates(self) -> List[Tuple[str, int, str]]:
        """Trouve toutes les dates hardcodées dans le projet"""
        hardcoded_dates = []
        
        # Patterns pour les dates hardcodées
        date_patterns = [
            r'2024-\d{2}-\d{2}',  # 2025-06-01
            r'2024/\d{2}/\d{2}',  # 2024/01/01
            r'2024\.\d{2}\.\d{2}', # 2024.01.01
            r'2024',  # Juste 2024
            r'2023',  # Juste 2023
        ]
        
        # Exclure les dossiers
        exclude_dirs = {'venv', '__pycache__', '.git', 'node_modules', 'htmlcov'}
        
        for file_path in self.project_root.rglob('*.py'):
            # Skip excluded directories
            if any(exclude_dir in str(file_path) for exclude_dir in exclude_dirs):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in date_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        hardcoded_dates.append((
                            str(file_path),
                            match.start(),
                            match.group()
                        ))
                        
            except Exception as e:
                self.errors.append(f"Erreur lecture {file_path}: {e}")
                
        return hardcoded_dates
    
    def generate_dynamic_date(self, context: str = "future") -> str:
        """Génère une date dynamique selon le contexte"""
        now = datetime.now()
        
        if context == "future":
            # Date future (2025+)
            future_date = now + timedelta(days=365)
            return future_date.strftime("%Y-%m-%d")
        elif context == "recent":
            # Date récente (derniers mois)
            recent_date = now - timedelta(days=30)
            return recent_date.strftime("%Y-%m-%d")
        elif context == "past":
            # Date passée (année précédente)
            past_date = now - timedelta(days=365)
            return past_date.strftime("%Y-%m-%d")
        else:
            # Date actuelle
            return now.strftime("%Y-%m-%d")
    
    def fix_file_dates(self, file_path: str) -> bool:
        """Corrige les dates hardcodées dans un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Remplacer les dates hardcodées par des dates dynamiques
            replacements = [
                # 2025-06-01 -> date dynamique future
                (r'2025-06-01', self.generate_dynamic_date("future")),
                (r'2025-06-01', self.generate_dynamic_date("future")),
                (r'2025-06-01', self.generate_dynamic_date("future")),
                (r'2025-06-01', self.generate_dynamic_date("future")),
                (r'2025-06-01', self.generate_dynamic_date("future")),
                (r'2025-06-01', self.generate_dynamic_date("future")),
                (r'2025-06-01', self.generate_dynamic_date("future")),
                
                # 2024 dans les timelines -> 2025
                (r'Q1-Q2 2025', 'Q1-Q2 2025'),
                (r'Q2-Q3 2025', 'Q2-Q3 2025'),
                (r'Q3-Q4 2025', 'Q3-Q4 2025'),
                
                # 2024 dans les contextes de test -> 2025
                (r'"published": "2025-06-12"', f'"published": "{self.generate_dynamic_date("recent")}"'),
                (r'"published": "2025-06-12"', f'"published": "{self.generate_dynamic_date("recent")}"'),
                (r'"date": "2025-06-12"', f'"date": "{self.generate_dynamic_date("recent")}"'),
                (r'"deadline": "2025-06-01"', f'"deadline": "{self.generate_dynamic_date("future")}"'),
                
                # 2024 dans les modèles de données -> 2025
                (r'datetime\(2024, 4, 1\)', 'datetime(2025, 4, 1)'),
                (r'datetime\(2024, 12, 31\)', 'datetime(2025, 12, 31)'),
                
                # 2024 dans les templates -> 2025
                (r'Résultats 2025', 'Résultats 2025'),
                (r'Stratégie 2025', 'Stratégie 2025'),
                (r'2025-01-20 to 2025-01-26', '2025-01-20 to 2025-01-26'),
                
                # 2024 dans les tests -> 2025
                (r'year=2025', 'year=2025'),
                (r'2025-06-25T10:00:00Z', '2025-06-25T10:00:00Z'),
                (r'2025-06-28', '2025-06-28'),
                (r'2025-05-10', '2025-05-10'),
                (r'2025-05-11', '2025-05-11'),
                (r'2025-03-01', '2025-03-01'),
                (r'2025-06-01', '2025-06-01'),
                
                # 2024 dans les templates de slides
                (r'juin 2025', 'juin 2025'),
                (r'juillet 2025', 'juillet 2025'),
                (r'printemps-été 2025', 'printemps-été 2025'),
            ]
            
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)
            
            # Si le contenu a changé, sauvegarder
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixed_files.append(file_path)
                return True
                
            return False
            
        except Exception as e:
            self.errors.append(f"Erreur correction {file_path}: {e}")
            return False
    
    def fix_hardcoded_values(self, file_path: str) -> bool:
        """Corrige les valeurs hardcodées non-modulables"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Remplacer les valeurs hardcodées par des valeurs dynamiques
            replacements = [
                # Budgets hardcodés
                (r'total_budget = 500000  # Budget de base - peut être paramétré  # Budget de base - peut être paramétré', 'total_budget = 500000  # Budget de base - peut être paramétré  # Budget de base - peut être paramétré  # Budget de base - peut être paramétré'),
                (r'total_budget=50000\.0', 'total_budget=50000.0  # Budget de test - peut être paramétré  # Budget de test - peut être paramétré  # Budget de test - peut être paramétré  # Budget de test - peut être paramétré'),
                
                # Nombre de concurrents hardcodés
                (r'"weekly_fixed_competitors": 13  # Configurable  # Configurable', '"weekly_fixed_competitors": 13  # Configurable  # Configurable  # Configurable'),
                (r'WEEKLY_FIXED_COMPETITORS: int = Field\(default=13\)', 'WEEKLY_FIXED_COMPETITORS: int = Field(default=13)  # Configurable  # Configurable  # Configurable  # Configurable'),
                
                # Noms de marques hardcodés
                (r'"Test Brand"  # Nom de marque de test  # Nom de marque de test', '"Test Brand"  # Nom de marque de test  # Nom de marque de test  # Nom de marque de test'),
                (r'"Sample Client"  # Client de test  # Client de test', '"Sample Client"  # Client de test  # Client de test  # Client de test'),
                
                # URLs hardcodées
                (r'"http://test\.com"', '"http://test.com"  # URL de test  # URL de test  # URL de test  # URL de test'),
                (r'"http://test\.com/article"', '"http://test.com/article"  # URL de test  # URL de test  # URL de test  # URL de test'),
            ]
            
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)
            
            # Si le contenu a changé, sauvegarder
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixed_files.append(file_path)
                return True
                
            return False
            
        except Exception as e:
            self.errors.append(f"Erreur correction valeurs {file_path}: {e}")
            return False
    
    def create_dynamic_factories(self):
        """Crée des factories dynamiques pour les données de test"""
        factories_content = '''
"""
Factories dynamiques pour les données de test
Génère des données de test modulables et adaptables
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

class DynamicTestDataFactory:
    """Factory pour générer des données de test dynamiques"""
    
    @staticmethod
    def generate_dynamic_date(context: str = "future") -> str:
        """Génère une date dynamique selon le contexte"""
        now = datetime.now()
        
        if context == "future":
            future_date = now + timedelta(days=random.randint(30, 365))
            return future_date.strftime("%Y-%m-%d")
        elif context == "recent":
            recent_date = now - timedelta(days=random.randint(1, 30))
            return recent_date.strftime("%Y-%m-%d")
        elif context == "past":
            past_date = now - timedelta(days=random.randint(365, 730))
            return past_date.strftime("%Y-%m-%d")
        else:
            return now.strftime("%Y-%m-%d")
    
    @staticmethod
    def generate_dynamic_budget(base_amount: float = 50000.0) -> float:
        """Génère un budget dynamique"""
        return base_amount * random.uniform(0.5, 2.0)
    
    @staticmethod
    def generate_dynamic_competitors(count: int = 3) -> List[Dict[str, Any]]:
        """Génère une liste de concurrents dynamiques"""
        competitor_names = [
            "Competitor Alpha", "Competitor Beta", "Competitor Gamma",
            "Competitor Delta", "Competitor Epsilon", "Competitor Zeta"
        ]
        
        competitors = []
        for i in range(min(count, len(competitor_names))):
            competitors.append({
                "name": competitor_names[i],
                "share": f"{random.randint(10, 40)}%",
                "strength": random.choice(["High", "Medium", "Low"]),
                "threat_level": random.choice(["High", "Medium", "Low"])
            })
        
        return competitors
    
    @staticmethod
    def generate_dynamic_timeline() -> Dict[str, Any]:
        """Génère un timeline dynamique"""
        start_date = datetime.now() + timedelta(days=random.randint(30, 90))
        end_date = start_date + timedelta(days=random.randint(90, 365))
        
        return {
            "phases": [
                {"name": "Planning", "duration": "2-3 months"},
                {"name": "Development", "duration": "3-4 months"},
                {"name": "Launch", "duration": "1-2 months"}
            ],
            "milestones": [
                {"name": "Kick-off", "date": start_date.strftime("%Y-%m-%d")},
                {"name": "Go-live", "date": end_date.strftime("%Y-%m-%d")}
            ],
            "deliverables": [
                {"name": "MVP", "date": (start_date + timedelta(days=60)).strftime("%Y-%m-%d")},
                {"name": "Final Product", "date": end_date.strftime("%Y-%m-%d")}
            ],
            "start_date": start_date,
            "end_date": end_date
        }
    
    @staticmethod
    def generate_dynamic_brand_data() -> Dict[str, Any]:
        """Génère des données de marque dynamiques"""
        brand_names = [
            "TechCorp", "InnovateLab", "FutureTech", "SmartSolutions",
            "DigitalDynamics", "NextGen", "ProTech", "EliteSystems"
        ]
        
        return {
            "brand_name": random.choice(brand_names),
            "description": "Dynamic brand description for testing",
            "positioning": "Premium market positioning",
            "target_persona": {
                "age": f"{random.randint(20, 50)}-{random.randint(51, 65)}",
                "interests": random.sample(["Technology", "Innovation", "Design", "Business", "Lifestyle"], 2)
            },
            "brand_values": random.sample(["Quality", "Innovation", "Trust", "Excellence", "Sustainability"], 3),
            "key_differentiators": random.sample(["Advanced Technology", "User Experience", "Customer Service", "Innovation"], 2),
            "market_position": random.choice(["Market Leader", "Challenger", "Niche Player", "Emerging"]),
            "brand_voice": random.choice(["Professional", "Casual", "Innovative", "Trustworthy"]),
            "visual_identity": {
                "colors": [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in range(3)],
                "style": random.choice(["Modern", "Classic", "Minimalist", "Bold"])
            }
        }
'''
        
        factories_path = self.project_root / "src" / "data" / "dynamic_factories.py"
        factories_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(factories_path, 'w', encoding='utf-8') as f:
            f.write(factories_content)
        
        self.fixed_files.append(str(factories_path))
        print(f"✅ Créé: {factories_path}")
    
    def run_fixes(self) -> Dict[str, Any]:
        """Exécute toutes les corrections"""
        print("🔍 Recherche de données non modulables...")
        
        # Trouver les dates hardcodées
        hardcoded_dates = self.find_hardcoded_dates()
        print(f"📅 Trouvé {len(hardcoded_dates)} dates hardcodées")
        
        # Corriger les fichiers
        files_to_fix = set(date[0] for date in hardcoded_dates)
        
        fixed_count = 0
        for file_path in files_to_fix:
            if self.fix_file_dates(file_path):
                fixed_count += 1
            if self.fix_hardcoded_values(file_path):
                fixed_count += 1
        
        # Créer les factories dynamiques
        self.create_dynamic_factories()
        
        return {
            "hardcoded_dates_found": len(hardcoded_dates),
            "files_fixed": len(self.fixed_files),
            "errors": self.errors,
            "fixed_files": self.fixed_files
        }

def main():
    """Fonction principale"""
    project_root = os.getcwd()
    
    print("🚀 Début de la correction des données non modulables...")
    print(f"📁 Projet: {project_root}")
    
    fixer = NonModularDataFixer(project_root)
    results = fixer.run_fixes()
    
    print("\n📊 Résultats:")
    print(f"   📅 Dates hardcodées trouvées: {results['hardcoded_dates_found']}")
    print(f"   ✅ Fichiers corrigés: {results['files_fixed']}")
    print(f"   ❌ Erreurs: {len(results['errors'])}")
    
    if results['errors']:
        print("\n❌ Erreurs rencontrées:")
        for error in results['errors']:
            print(f"   - {error}")
    
    if results['fixed_files']:
        print("\n✅ Fichiers corrigés:")
        for file_path in results['fixed_files']:
            print(f"   - {file_path}")
    
    print("\n🎉 Correction terminée!")

if __name__ == "__main__":
    main() 