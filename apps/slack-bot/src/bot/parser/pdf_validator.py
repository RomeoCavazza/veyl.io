"""
Validation des fichiers PDF
Module spécialisé pour la validation
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class PDFValidator:
    """Validateur spécialisé pour les fichiers PDF"""

    def __init__(self):
        self.supported_extensions = ['.pdf']
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.min_file_size = 1024  # 1KB

    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validation complète d'un fichier PDF - refactorisé pour réduire la complexité

        Args:
            file_path: Chemin vers le fichier à valider

        Returns:
            Dictionnaire avec le résultat de validation
        """
        try:
            # Étape 1: Initialisation
            validation_result = _initialize_validation_result(file_path)
            path = Path(file_path)

            # Étape 2: Vérifications de base
            if not _check_file_existence(path, validation_result):
                return validation_result

            if not _check_file_extension(path, self.supported_extensions, validation_result):
                return validation_result

            # Étape 3: Vérifications de taille et permissions
            if not _check_file_size(path, self.min_file_size, self.max_file_size, validation_result):
                return validation_result

            if not _check_file_permissions(path, validation_result):
                return validation_result

            # Étape 4: Validation du contenu
            if not _validate_content(path, self, validation_result):
                return validation_result

            # Étape 5: Finalisation
            return _finalize_validation(path, file_path, validation_result)

        except Exception as e:
            return _handle_validation_error(e, file_path, validation_result)

def _initialize_validation_result(file_path: str) -> Dict[str, Any]:
    """Initialise le dictionnaire de résultat de validation"""
    return {
        'is_valid': False,
        'file_path': file_path,
        'errors': [],
        'warnings': [],
        'file_info': {}
    }

def _check_file_existence(path: Path, result: Dict[str, Any]) -> bool:
    """Vérifie l'existence du fichier"""
    if not path.exists():
        result['errors'].append('File does not exist')
        return False
    return True

def _check_file_extension(path: Path, supported_extensions: list, result: Dict[str, Any]) -> bool:
    """Vérifie l'extension du fichier"""
    if path.suffix.lower() not in supported_extensions:
        result['errors'].append(f'Invalid file extension: {path.suffix}')
        return False
    return True

def _check_file_size(path: Path, min_size: int, max_size: int, result: Dict[str, Any]) -> bool:
    """Vérifie la taille du fichier"""
    file_size = path.stat().st_size
    result['file_info']['size'] = file_size

    if file_size < min_size:
        result['errors'].append(f'File too small: {file_size} bytes')
        return False

    if file_size > max_size:
        result['warnings'].append(f'File very large: {file_size} bytes')

    return True

def _check_file_permissions(path: Path, result: Dict[str, Any]) -> bool:
    """Vérifie les permissions de lecture du fichier"""
    if not os.access(path, os.R_OK):
        result['errors'].append('File not readable')
        return False
    return True

def _validate_content(path: Path, validator, result: Dict[str, Any]) -> bool:
    """Valide le contenu du PDF"""
    if not validator._validate_pdf_content(path):
        result['errors'].append('Invalid PDF content')
        return False
    return True

def _finalize_validation(path: Path, file_path: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """Finalise la validation avec succès"""
    result['is_valid'] = True
    result['file_info']['last_modified'] = path.stat().st_mtime
    logger.info(f"✅ PDF validation successful: {file_path}")
    return result

def _handle_validation_error(error: Exception, file_path: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """Gère les erreurs de validation"""
    result['errors'].append(f'Validation error: {str(error)}')
    logger.error(f"PDF validation failed for {file_path}: {error}")
    return result

    def _validate_pdf_content(self, path: Path) -> bool:
        """Validation basique du contenu PDF"""
        try:
            with open(path, 'rb') as f:
                # Lire le début du fichier
                header = f.read(8)

                # Vérifier le header PDF
                if not header.startswith(b'%PDF-'):
                    return False

                # Lire la fin du fichier pour vérifier le EOF
                f.seek(-1024, 2)  # Derniers 1024 octets
                end_content = f.read()

                # Chercher %%EOF
                if b'%%EOF' not in end_content:
                    return False

            return True

        except Exception:
            return False

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Récupère les informations détaillées du fichier"""
        try:
            path = Path(file_path)
            stat = path.stat()

            return {
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'accessed': stat.st_atime,
                'permissions': oct(stat.st_mode)[-3:],
                'readable': os.access(path, os.R_OK),
                'writable': os.access(path, os.W_OK)
            }

        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            return {}

    def is_corrupted(self, file_path: str) -> bool:
        """Vérifie si le fichier PDF est corrompu"""
        try:
            validation = self.validate_file(file_path)
            return not validation['is_valid'] or len(validation['errors']) > 0
        except Exception:
            return True

# Fonction de compatibilité
def validate_pdf_file(file_path: str) -> bool:
    """Fonction de compatibilité pour l'ancien code"""
    validator = PDFValidator()
    result = validator.validate_file(file_path)
    return result['is_valid']
