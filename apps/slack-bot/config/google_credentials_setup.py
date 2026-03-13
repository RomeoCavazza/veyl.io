"""
Configuration Google Credentials pour Google Slides API
Script d'aide pour setup rapide
"""

import os
import json
from pathlib import Path

def create_google_credentials_template():
    """Créer un template de credentials Google"""
    
    credentials_template = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
    }
    
    # Créer dossier secrets
    secrets_dir = Path("config/secrets")
    secrets_dir.mkdir(parents=True, exist_ok=True)
    
    # Sauvegarder template
    template_path = secrets_dir / "credentials.json.template"
    with open(template_path, 'w') as f:
        json.dump(credentials_template, f, indent=2)
    
    print(f"✅ Template créé: {template_path}")
    print("📝 Instructions:")
    print("1. Aller sur https://console.cloud.google.com/")
    print("2. Créer un projet ou sélectionner existant")
    print("3. Activer Google Slides API")
    print("4. Créer Service Account")
    print("5. Télécharger JSON credentials")
    print("6. Renommer en 'credentials.json' dans config/secrets/")
    
    return template_path

def setup_google_env():
    """Configurer variable d'environnement Google"""
    
    credentials_path = "config/secrets/credentials.json"
    
    if os.path.exists(credentials_path):
        # Ajouter à .env
        env_line = f"GOOGLE_APPLICATION_CREDENTIALS={credentials_path}\n"
        
        with open('.env', 'a') as f:
            f.write(env_line)
        
        print(f"✅ Variable ajoutée à .env: {env_line.strip()}")
        return True
    else:
        print(f"❌ Fichier credentials non trouvé: {credentials_path}")
        print("🔧 Utiliser create_google_credentials_template() d'abord")
        return False

def test_google_credentials():
    """Tester les credentials Google"""
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'config/secrets/credentials.json')
        
        if not os.path.exists(credentials_path):
            print(f"❌ Credentials non trouvées: {credentials_path}")
            return False
        
        # Charger credentials
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/presentations']
        )
        
        # Test service
        service = build('slides', 'v1', credentials=credentials)
        
        print("✅ Google Slides API: Credentials valides")
        return True
        
    except Exception as e:
        print(f"❌ Test Google credentials: {e}")
        return False

def quick_setup():
    """Setup rapide complet"""
    print("🚀 SETUP GOOGLE SLIDES API")
    print("=" * 30)
    
    # 1. Créer template
    create_google_credentials_template()
    
    # 2. Instructions
    print("\n📋 ÉTAPES SUIVANTES:")
    print("1. Configurer credentials Google (voir instructions ci-dessus)")
    print("2. Lancer: python config/google_credentials_setup.py")
    print("3. Le bot utilisera Google Slides API automatiquement")
    
    print("\n🟡 FALLBACK AUTOMATIQUE:")
    print("Si pas de credentials → Mode local JSON (fonctionne déjà)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "template":
            create_google_credentials_template()
        elif command == "setup":
            setup_google_env()
        elif command == "test":
            test_google_credentials()
        else:
            print("Usage: python google_credentials_setup.py [template|setup|test]")
    else:
        quick_setup() 