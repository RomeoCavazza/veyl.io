import os
import json
from pathlib import Path
from typing import Dict, Any

class ConfigError(Exception):
    """Exception raised for configuration errors."""
    pass

def load_config(config_path: str = None) -> Dict[str, Any]:
    """Charge la configuration depuis un fichier JSON."""
    if not config_path:
        config_path = os.getenv('REVOLVER_CONFIG', 'config.json')
    
    if not os.path.exists(config_path):
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if not validate_config(config):
                raise ConfigError("Configuration invalide")
            return config
    except Exception as e:
        raise ConfigError(f"Erreur lors du chargement de la configuration: {e}")

def validate_config(config: Dict[str, Any]) -> bool:
    """Valide la configuration."""
    required_fields = ['api_key', 'output_dir']
    return all(field in config for field in required_fields)

def get_config_path() -> Path:
    """Retourne le chemin du fichier de configuration."""
    return Path(os.getenv('REVOLVER_CONFIG', 'config.json'))

def save_config(config: Dict[str, Any], config_path: str = None) -> None:
    """Sauvegarde la configuration dans un fichier JSON."""
    if not config_path:
        config_path = get_config_path()
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise ConfigError(f"Erreur lors de la sauvegarde de la configuration: {e}")

def update_config(updates: Dict[str, Any], config_path: str = None) -> Dict[str, Any]:
    """Met à jour la configuration avec de nouvelles valeurs."""
    config = load_config(config_path)
    config.update(updates)
    save_config(config, config_path)
    return config
