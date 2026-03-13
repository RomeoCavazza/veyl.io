import logging
from pathlib import Path
from typing import Optional, Union
from src.utils.logger_v2 import logger

def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Configure le logger pour l'application."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    logger.setLevel(numeric_level)
    
    if log_file:
        logger.add_file_handler(log_file)

def validate_file_path(file_path: Union[str, Path]) -> Path:
    """Valide et retourne un chemin de fichier."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return path.resolve()

def ensure_dir(dir_path: Union[str, Path]) -> Path:
    """Crée un répertoire s'il n'existe pas."""
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()

def get_output_dir() -> Path:
    """Retourne le répertoire de sortie par défaut."""
    output_dir = Path("output")
    ensure_dir(output_dir)
    return output_dir.resolve()

def get_data_dir() -> Path:
    """Retourne le répertoire de données par défaut."""
    data_dir = Path("data")
    ensure_dir(data_dir)
    return data_dir.resolve()

def get_workspace_dir() -> Path:
    """Retourne le répertoire de travail."""
    return Path.cwd().resolve()
