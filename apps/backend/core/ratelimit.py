# core/ratelimit.py
# Configuration du rate limiting avec SlowAPI (en mémoire)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Rate limiting en mémoire (suffisant pour un early SaaS)
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")

def setup_rate_limit(app: FastAPI):
    """Configure le rate limiting pour l'application FastAPI"""
    @app.exception_handler(RateLimitExceeded)
    async def rl_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse({"detail": "Too Many Requests"}, status_code=429)
    app.state.limiter = limiter
