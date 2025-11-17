import logging
import time
from typing import Any, Dict, Optional, Union

import httpx  # type: ignore
from fastapi import HTTPException, status

from core.config import settings

logger = logging.getLogger(__name__)

TIKTOK_BASE_URL = "https://open.tiktokapis.com/v2/"


class TikTokAPIError(HTTPException):
    """Erreur normalisée pour les appels TikTok API."""

    def __init__(self, status_code: int, detail: Union[str, Dict[str, Any]]) -> None:
        super().__init__(status_code=status_code, detail=detail)


def _build_url(endpoint: str) -> str:
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        return endpoint
    return f"{TIKTOK_BASE_URL}{endpoint.lstrip('/')}"


def _sanitize(value: Any) -> Any:
    if isinstance(value, str) and "token" in value.lower():
        return "***"
    return value


async def call_tiktok(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    access_token: Optional[str] = None,
    timeout: float = 20.0,
) -> Any:
    """
    Appelle la TikTok API en journalisant les métadonnées de requête.
    Ne log jamais les tokens.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: Endpoint TikTok API (ex: "user/info/", "video/list/")
        params: Query parameters
        data: Request body (pour POST)
        access_token: Token d'accès TikTok (Bearer token)
        timeout: Timeout en secondes
    
    Returns:
        Réponse JSON de l'API TikTok
    
    Raises:
        TikTokAPIError: Si l'appel API échoue
    """
    method_upper = method.upper()
    url = _build_url(endpoint)

    headers: Dict[str, str] = {
        "Content-Type": "application/json",
    }
    
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    query: Dict[str, Any] = dict(params or {})

    safe_params = {key: _sanitize(str(value)) for key, value in query.items()}
    safe_headers = {key: _sanitize(str(value)) for key, value in headers.items()}

    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method=method_upper,
                url=url,
                params=query,
                json=data,
                headers=headers,
            )
    except httpx.RequestError as exc:
        duration = time.perf_counter() - start
        logger.error(
            "TikTok %s %s request error after %.2fs: %s",
            method_upper,
            url,
            duration,
            exc,
        )
        raise TikTokAPIError(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="TikTok API unreachable",
        ) from exc

    duration = time.perf_counter() - start

    if response.status_code >= 400:
        detail: Union[str, Dict[str, Any]]
        try:
            detail = response.json()
        except ValueError:
            detail = {"error": response.text}

        logger.error(
            "TIKTOK API ERROR | %s %s | Status: %d | Duration: %.2fs",
            method_upper,
            url,
            response.status_code,
            duration,
        )

        raise TikTokAPIError(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "message": "TikTok API error",
                "status_code": response.status_code,
                "detail": detail,
            },
        )

    # Log succès seulement si HTTP 200-399
    logger.info(
        "TIKTOK API SUCCESS | %s %s | Status: %d | Duration: %.2fs | Params: %s",
        method_upper,
        url,
        response.status_code,
        duration,
        safe_params,
    )

    try:
        return response.json()
    except ValueError:
        return response.text

