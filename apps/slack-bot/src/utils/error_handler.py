"""
Error Handler Module - Standardisation des messages d'erreur
"""

import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from src.core.timestamped_model import TimestampedModel

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Niveaux de sévérité des erreurs"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Catégories d'erreurs"""
    API_ERROR = "api_error"
    VALIDATION_ERROR = "validation_error"
    CONFIGURATION_ERROR = "configuration_error"
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    AUTHENTICATION_ERROR = "authentication_error"
    PERMISSION_ERROR = "permission_error"
    RESOURCE_ERROR = "resource_error"
    UNKNOWN_ERROR = "unknown_error"

@dataclass
class ErrorInfo(TimestampedModel):
    """Informations structurées sur une erreur"""
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    traceback: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "error_code": self.error_code,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "traceback": self.traceback,
            "context": self.context
        }

class ErrorHandler:
    """Gestionnaire centralisé des erreurs"""
    
    def __init__(self):
        self.error_patterns = self._init_error_patterns()
        self.error_messages = self._init_error_messages()
    
    def _init_error_patterns(self) -> Dict[str, ErrorCategory]:
        """Initialise les patterns de reconnaissance d'erreurs"""
        return {
            # API Errors
            "timeout": ErrorCategory.TIMEOUT_ERROR,
            "connection": ErrorCategory.NETWORK_ERROR,
            "rate limit": ErrorCategory.API_ERROR,
            "quota": ErrorCategory.API_ERROR,
            "api key": ErrorCategory.AUTHENTICATION_ERROR,
            "unauthorized": ErrorCategory.AUTHENTICATION_ERROR,
            "forbidden": ErrorCategory.PERMISSION_ERROR,
            "not found": ErrorCategory.RESOURCE_ERROR,
            
            # Validation Errors
            "invalid": ErrorCategory.VALIDATION_ERROR,
            "missing": ErrorCategory.VALIDATION_ERROR,
            "required": ErrorCategory.VALIDATION_ERROR,
            "format": ErrorCategory.VALIDATION_ERROR,
            
            # Configuration Errors
            "config": ErrorCategory.CONFIGURATION_ERROR,
            "environment": ErrorCategory.CONFIGURATION_ERROR,
            "setting": ErrorCategory.CONFIGURATION_ERROR,
        }
    
    def _init_error_messages(self) -> Dict[ErrorCategory, str]:
        """Initialise les messages d'erreur standardisés"""
        return {
            ErrorCategory.API_ERROR: "Erreur de communication avec le service externe",
            ErrorCategory.VALIDATION_ERROR: "Données invalides ou manquantes",
            ErrorCategory.CONFIGURATION_ERROR: "Erreur de configuration du système",
            ErrorCategory.NETWORK_ERROR: "Erreur de connexion réseau",
            ErrorCategory.TIMEOUT_ERROR: "Délai d'attente dépassé",
            ErrorCategory.AUTHENTICATION_ERROR: "Erreur d'authentification",
            ErrorCategory.PERMISSION_ERROR: "Permissions insuffisantes",
            ErrorCategory.RESOURCE_ERROR: "Ressource non trouvée ou indisponible",
            ErrorCategory.UNKNOWN_ERROR: "Erreur inattendue du système"
        }
    
    def analyze_error(self, exception: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorInfo:
        """
        Analyse une exception et retourne des informations structurées
        
        Args:
            exception: Exception à analyser
            context: Contexte supplémentaire
            
        Returns:
            ErrorInfo avec les détails de l'erreur
        """
        error_message = str(exception)
        error_category = self._categorize_error(error_message, exception)
        severity = self._determine_severity(error_category, exception)
        
        return ErrorInfo(
            message=self._get_standard_message(error_category, error_message),
            category=error_category,
            severity=severity,
            error_code=self._generate_error_code(error_category),
            details={
                "original_message": error_message,
                "exception_type": type(exception).__name__
            },
            traceback=traceback.format_exc(),
            context=context
        )
    
    def _categorize_error(self, message: str, exception: Exception) -> ErrorCategory:
        """Catégorise l'erreur selon son message et type"""
        message_lower = message.lower()
        
        # Vérifier les patterns
        for pattern, category in self.error_patterns.items():
            if pattern in message_lower:
                return category
        
        # Vérifier le type d'exception
        exception_type = type(exception).__name__
        
        if "Timeout" in exception_type:
            return ErrorCategory.TIMEOUT_ERROR
        elif "Connection" in exception_type:
            return ErrorCategory.NETWORK_ERROR
        elif "Validation" in exception_type:
            return ErrorCategory.VALIDATION_ERROR
        elif "Authentication" in exception_type:
            return ErrorCategory.AUTHENTICATION_ERROR
        elif "Permission" in exception_type:
            return ErrorCategory.PERMISSION_ERROR
        
        return ErrorCategory.UNKNOWN_ERROR
    
    def _determine_severity(self, category: ErrorCategory, exception: Exception) -> ErrorSeverity:
        """Détermine la sévérité de l'erreur"""
        if category in [ErrorCategory.AUTHENTICATION_ERROR, ErrorCategory.PERMISSION_ERROR]:
            return ErrorSeverity.HIGH
        elif category in [ErrorCategory.NETWORK_ERROR, ErrorCategory.TIMEOUT_ERROR]:
            return ErrorSeverity.MEDIUM
        elif category == ErrorCategory.VALIDATION_ERROR:
            return ErrorSeverity.LOW
        else:
            return ErrorSeverity.MEDIUM
    
    def _get_standard_message(self, category: ErrorCategory, original_message: str) -> str:
        """Retourne un message d'erreur standardisé"""
        base_message = self.error_messages.get(category, self.error_messages[ErrorCategory.UNKNOWN_ERROR])
        
        # Ajouter des détails spécifiques si disponibles
        if category == ErrorCategory.API_ERROR and "rate limit" in original_message.lower():
            return f"{base_message} : Limite de requêtes dépassée"
        elif category == ErrorCategory.TIMEOUT_ERROR:
            return f"{base_message} : Le service ne répond pas dans les délais"
        elif category == ErrorCategory.NETWORK_ERROR:
            return f"{base_message} : Impossible de se connecter au service"
        
        return base_message
    
    def _generate_error_code(self, category: ErrorCategory) -> str:
        """Génère un code d'erreur unique"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{category.value.upper()}_{timestamp}"

    def handle_error(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        reraise: bool = True
    ) -> ErrorInfo:
        """
        Gère une erreur de manière centralisée
        
        Args:
            exception: Exception à gérer
            context: Contexte supplémentaire
            reraise: Si True, relance l'exception après traitement
            
        Returns:
            ErrorInfo avec les détails de l'erreur
        """
        error_info = self.analyze_error(exception, context)
        self.log_error(error_info)
        
        if reraise:
            raise exception
        
        return error_info

# Instance globale
error_handler = ErrorHandler()

def handle_errors(
    reraise: bool = True,
    context: Optional[Dict[str, Any]] = None
):
    """
    Décorateur pour gérer automatiquement les erreurs
    
    Args:
        reraise: Si True, relance l'exception après traitement
        context: Contexte supplémentaire à ajouter
    """

def get_module_error_message(module: str, error_type: str, fallback: str = None) -> str:
    """
    Obtient un message d'erreur spécifique à un module
    
    Args:
        module: Nom du module ("openai", "slack", "redis", "google")
        error_type: Type d'erreur
        fallback: Message de fallback
        
    Returns:
        Message d'erreur spécifique
    """
    module_messages = MODULE_ERROR_MESSAGES.get(module, {})
    return module_messages.get(error_type, fallback or "Erreur inattendue")

# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple d'utilisation du gestionnaire d'erreurs
    @handle_errors(reraise=False)
    def example_function():
        raise ValueError("Données invalides")
    
    try:
        example_function()
    except Exception as e:
        print(f"Erreur gérée: {e}")
    
    # Exemple d'analyse d'erreur
    try:
        import requests
        requests.get("http://invalid-url", timeout=1)
    except Exception as e:
        error_info = error_handler.analyze_error(e, {"url": "http://invalid-url"})
        print(f"Erreur analysée: {error_info.to_dict()}")
