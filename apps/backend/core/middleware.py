# core/middleware.py
# Middleware pour le tracing et la gestion des erreurs

import uuid
import logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware pour ajouter un Request ID à chaque requête pour le tracing"""
    
    async def dispatch(self, request: Request, call_next):
        # Générer ou récupérer le Request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Ajouter le Request ID au contexte de la requête
        request.state.request_id = request_id
        
        # Logger avec le Request ID
        logger.info(f"[{request_id}] {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Ajouter le Request ID dans les headers de réponse
            response.headers["X-Request-ID"] = request_id
            
            return response
        except Exception as exc:
            # Logger l'erreur avec le Request ID
            logger.error(f"[{request_id}] Error: {exc}", exc_info=True)
            raise


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware pour standardiser les réponses d'erreur non gérées"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            request_id = getattr(request.state, "request_id", "unknown")
            
            # FastAPI gère déjà les HTTPException, on ne les intercepte pas
            from fastapi import HTTPException
            if isinstance(exc, HTTPException):
                raise  # Laisser FastAPI gérer
            
            # Erreur inattendue - logger et retourner 500
            logger.error(f"[{request_id}] Unhandled error: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": 500,
                        "message": "Internal server error",
                        "request_id": request_id,
                    }
                },
                headers={"X-Request-ID": request_id}
            )

