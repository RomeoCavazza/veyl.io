"""
Décorateur unifié pour les endpoints API
Évite la répétition de code dans les endpoints FastAPI
"""

import functools
import logging
from typing import Any, Callable, Dict, Optional, TypeVar, Type
from datetime import datetime
from fastapi import HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])

def endpoint_handler(
    response_model: Optional[Type[BaseModel]] = None,
    demo_mode: bool = False,
    demo_endpoint_name: Optional[str] = None
) -> Callable[[F], F]:
    """Décorateur unifié pour les endpoints API"""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = datetime.now()
            endpoint_name = demo_endpoint_name or func.__name__

            try:
                # Mode démo si activé
                if demo_mode:
                    return {"demo_mode": True, "endpoint": endpoint_name}

                # Exécuter la fonction normale
                result = await func(*args, **kwargs)

                # Calculer le temps de traitement
                processing_time = (datetime.now() - start_time).total_seconds()

                # Ajouter processing_time si nécessaire
                if hasattr(result, 'processing_time'):
                    result.processing_time = processing_time
                elif isinstance(result, dict) and 'processing_time' not in result:
                    result['processing_time'] = processing_time

                return result

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        return wrapper
    return decorator