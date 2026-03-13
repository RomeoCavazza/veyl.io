#!/usr/bin/env python3
"""
Script de configuration pour la production Revolver AI Bot
Vérifie et configure automatiquement tous les composants nécessaires
"""

import os
import sys
import asyncio
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import platform

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config.production import (
    load_production_config,
    RateLimiter,
    ProductionLogger,
    BackupManager,
    PerformanceManager
)


class ProductionSetup:
    """Script de configuration pour la production"""
    
    def __init__(self):
        self.config = None
        self.setup_log = []
    
    def log(self, message: str, level: str = "INFO"):
        """Enregistre un message de log"""
        timestamp = asyncio.get_event_loop().time()
        log_entry = f"[{timestamp:.2f}] {level}: {message}"
        self.setup_log.append(log_entry)
        print(log_entry)
    
    def check_python_version(self) -> bool:
        """Vérifie la version de Python"""
        version = sys.version_info
        self.log(f"Python version: {version.major}.{version.minor}.{version.micro}")
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.log("❌ Python 3.8+ requis", "ERROR")
            return False
        
        self.log("✅ Version Python compatible")
        return True
    
    def check_dependencies(self) -> bool:
        """Vérifie les dépendances requises"""
        self.log("Vérification des dépendances...")
        
        required_packages = [
            "fastapi", "uvicorn", "openai", "redis", "aiohttp",
            "prometheus_client", "pytest", "pytest-cov"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                self.log(f"✅ {package}")
            except ImportError:
                missing_packages.append(package)
                self.log(f"❌ {package} manquant", "ERROR")
        
        if missing_packages:
            self.log(f"Dépendances manquantes: {', '.join(missing_packages)}", "ERROR")
            return False
        
        self.log("✅ Toutes les dépendances sont installées")
        return True
    
    def check_environment_variables(self) -> bool:
        """Vérifie les variables d'environnement"""
        self.log("Vérification des variables d'environnement...")
        
        required_vars = ["OPENAI_API_KEY"]
        optional_vars = [
            "SLACK_BOT_TOKEN", "SLACK_SIGNING_SECRET", "SLACK_APP_TOKEN",
            "REDIS_URL", "DATABASE_URL", "ALERT_WEBHOOK_URL"
        ]
        
        missing_required = []
        missing_optional = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_required.append(var)
                self.log(f"❌ {var} manquant (obligatoire)", "ERROR")
            else:
                self.log(f"✅ {var}")
        
        for var in optional_vars:
            if not os.getenv(var):
                missing_optional.append(var)
                self.log(f"⚠️  {var} manquant (optionnel)", "WARNING")
            else:
                self.log(f"✅ {var}")
        
        if missing_required:
            self.log(f"Variables obligatoires manquantes: {', '.join(missing_required)}", "ERROR")
            return False
        
        if missing_optional:
            self.log(f"Variables optionnelles manquantes: {', '.join(missing_optional)}", "WARNING")
        
        return True
    
    def create_directories(self) -> bool:
        """Crée les répertoires nécessaires"""
        self.log("Création des répertoires...")
        
        directories = [
            "logs",
            "backups",
            "presentations",
            "data/veille",
            "htmlcov",
            "reports"
        ]
        
        for directory in directories:
            path = Path(directory)
            try:
                path.mkdir(parents=True, exist_ok=True)
                self.log(f"✅ Créé: {directory}")
            except Exception as e:
                self.log(f"❌ Erreur création {directory}: {e}", "ERROR")
                return False
        
        return True
    
    def check_redis_connection(self) -> bool:
        """Vérifie la connexion Redis"""
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            self.log("⚠️  REDIS_URL non configuré - rate limiting en mémoire", "WARNING")
            return True
        
        try:
            import redis
            client = redis.from_url(redis_url)
            client.ping()
            self.log("✅ Connexion Redis OK")
            return True
        except Exception as e:
            self.log(f"❌ Erreur connexion Redis: {e}", "ERROR")
            self.log("⚠️  Le rate limiting utilisera la mémoire", "WARNING")
            return False
    
    def run_tests(self) -> bool:
        """Exécute les tests"""
        self.log("Exécution des tests...")
        
        try:
            # Tests unitaires
            result = subprocess.run([
                sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log("✅ Tests unitaires passés")
            else:
                self.log(f"❌ Tests unitaires échoués: {result.stderr}", "ERROR")
                return False
            
            # Tests de couverture
            result = subprocess.run([
                sys.executable, "-m", "pytest", "tests/", 
                "--cov=src", "--cov-report=term-missing", "--cov-fail-under=80"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log("✅ Couverture de tests OK")
            else:
                self.log(f"❌ Couverture insuffisante: {result.stderr}", "ERROR")
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            self.log("❌ Timeout lors de l'exécution des tests", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Erreur lors des tests: {e}", "ERROR")
            return False
    
    def check_security(self) -> bool:
        """Vérifie la sécurité de base"""
        self.log("Vérification de la sécurité...")
        
        # Vérifier les permissions des fichiers sensibles
        sensitive_files = [".env", "env.example"]
        
        for file_path in sensitive_files:
            if Path(file_path).exists():
                stat = Path(file_path).stat()
                if platform.system() != "Windows":
                    if stat.st_mode & 0o777 != 0o600:
                        self.log(f"⚠️  Permissions {file_path} trop ouvertes", "WARNING")
                    else:
                        self.log(f"✅ Permissions {file_path} OK")
        
        # Vérifier la présence de clés secrètes dans le code
        code_files = list(Path("src").rglob("*.py"))
        secret_patterns = ["sk-", "xoxb-", "xoxp-", "password", "secret"]
        
        for file_path in code_files:
            try:
                content = file_path.read_text()
                for pattern in secret_patterns:
                    if pattern in content.lower():
                        self.log(f"⚠️  Pattern suspect dans {file_path}: {pattern}", "WARNING")
            except Exception:
                pass
        
        self.log("✅ Vérification sécurité terminée")
        return True
    
    def generate_production_report(self) -> Dict:
        """Génère un rapport de configuration"""
        self.log("Génération du rapport de production...")
        
        report = {
            "timestamp": asyncio.get_event_loop().time(),
            "system_info": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": platform.system(),
                "architecture": platform.machine()
            },
            "environment": {
                "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
                "slack_configured": bool(os.getenv("SLACK_BOT_TOKEN")),
                "redis_configured": bool(os.getenv("REDIS_URL")),
                "database_configured": bool(os.getenv("DATABASE_URL"))
            },
            "directories": {
                "logs": Path("logs").exists(),
                "backups": Path("backups").exists(),
                "presentations": Path("presentations").exists(),
                "data_veille": Path("data/veille").exists()
            },
            "setup_log": self.setup_log
        }
        
        # Sauvegarder le rapport
        report_path = Path("reports/production_setup_report.json")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.log(f"✅ Rapport sauvegardé: {report_path}")
        return report
    
    async def run_full_setup(self) -> bool:
        """Exécute la configuration complète"""
        self.log("🚀 Démarrage de la configuration de production Revolver AI Bot")
        
        checks = [
            ("Version Python", self.check_python_version),
            ("Dépendances", self.check_dependencies),
            ("Variables d'environnement", self.check_environment_variables),
            ("Répertoires", self.create_directories),
            ("Connexion Redis", self.check_redis_connection),
            ("Tests", self.run_tests),
            ("Sécurité", self.check_security)
        ]
        
        failed_checks = []
        
        for check_name, check_func in checks:
            self.log(f"\n--- {check_name} ---")
            try:
                if not check_func():
                    failed_checks.append(check_name)
            except Exception as e:
                self.log(f"❌ Erreur lors de {check_name}: {e}", "ERROR")
                failed_checks.append(check_name)
        
        # Générer le rapport
        report = self.generate_production_report()
        
        # Résumé final
        self.log(f"\n{'='*50}")
        self.log("📊 RÉSUMÉ DE LA CONFIGURATION")
        self.log(f"{'='*50}")
        
        if failed_checks:
            self.log(f"❌ ÉCHECS: {', '.join(failed_checks)}", "ERROR")
            self.log("⚠️  La configuration n'est pas complète", "WARNING")
            return False
        else:
            self.log("✅ CONFIGURATION RÉUSSIE", "SUCCESS")
            self.log("🎉 Revolver AI Bot est prêt pour la production!")
            return True


async def main():
    """Fonction principale"""
    setup = ProductionSetup()
    
    try:
        success = await setup.run_full_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Configuration interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 