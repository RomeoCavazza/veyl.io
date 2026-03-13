"""
Retry Logic Module - Gestion robuste des erreurs APIs externes
"""

import time
import random
import logging
from typing import Callable, Any
from functools import wraps
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class RetryStrategy(Enum):
    """Stratégies de retry disponibles"""
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"

class CircuitBreakerState(Enum):
    """États du circuit breaker"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit open, reject requests
    HALF_OPEN = "half_open"  # Testing if service is back

class RetryConfig:
    """Configuration pour le retry logic"""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
        jitter: bool = True,
        timeout: float = 30.0,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 60.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.strategy = strategy
        self.jitter = jitter
        self.timeout = timeout
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout

class CircuitBreaker:
    """Circuit breaker pattern pour éviter les cascades d'erreurs"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
    
    def can_execute(self) -> bool:
        """Vérifie si l'exécution est autorisée"""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                return True
            return False
        
        # HALF_OPEN state
        return True

    def _should_attempt_reset(self) -> bool:
        """Vérifie si on doit tenter de réinitialiser le circuit breaker"""
        if not self.last_failure_time:
            return True
        
        return (datetime.now() - self.last_failure_time).total_seconds() >= self.config.circuit_breaker_timeout

class RetryLogic:
    """Logique de retry avec circuit breaker"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self.circuit_breaker = CircuitBreaker(config)
    
    def execute(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Exécute une fonction avec retry logic
        
        Args:
            func: Fonction à exécuter
            *args: Arguments de la fonction
            **kwargs: Arguments nommés de la fonction
            
        Returns:
            Résultat de la fonction
            
        Raises:
            Exception: Si tous les retries échouent
        """
        if not self.circuit_breaker.can_execute():
            raise Exception("Circuit breaker is open - service unavailable")
        
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                self.circuit_breaker.on_success()
                return result
                
            except Exception as e:
                last_exception = e
                self.circuit_breaker.on_failure()
                
                if attempt < self.config.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(f"[RETRY] Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s")
                    time.sleep(delay)
                else:
                    logger.error(f"[RETRY] All {self.config.max_retries + 1} attempts failed. Last error: {e}")
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calcule le délai d'attente selon la stratégie"""
        if self.config.strategy == RetryStrategy.FIXED:
            delay = self.config.base_delay
        
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.base_delay * (attempt + 1)
        
        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.base_delay * (2 ** attempt)
        
        else:
            delay = self.config.base_delay
        
        # Appliquer le délai maximum
        delay = min(delay, self.config.max_delay)
        
        # Ajouter du jitter pour éviter les thundering herds
        if self.config.jitter:
            jitter = random.uniform(0, 0.1 * delay)
            delay += jitter
        
        return delay

def retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    exceptions: tuple = (Exception,)
):
    """
    Décorateur pour appliquer le retry logic
    
    Args:
        max_retries: Nombre maximum de tentatives
        base_delay: Délai de base entre les tentatives
        strategy: Stratégie de retry
        exceptions: Types d'exceptions à retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_retry_logic(api_type: str = "http") -> RetryLogic:
    """
    Obtient une instance de RetryLogic configurée pour un type d'API
    
    Args:
        api_type: Type d'API ("openai", "slack", "redis", "google", "http")
        
    Returns:
        RetryLogic configuré
    """
    config = API_CONFIGS.get(api_type, API_CONFIGS["http"])
    return RetryLogic(config)

# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple avec décorateur
    @retry(max_retries=3, base_delay=1.0)
    def example_function():
        import random
        if random.random() < 0.7:  # 70% de chance d'échec
            raise Exception("Random failure")
        return "Success!"
    
    # Exemple avec RetryLogic direct
    retry_logic = get_retry_logic("openai")
    
    try:
        result = retry_logic.execute(example_function)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Failed: {e}")
