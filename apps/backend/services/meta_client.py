import logging
import time
from typing import Any, Dict, Optional, Union

import httpx  # type: ignore
from fastapi import HTTPException, status

from core.config import settings

logger = logging.getLogger(__name__)

META_BASE_URL = "https://graph.facebook.com/"


class MetaAPIError(HTTPException):
    """Erreur normalisée pour les appels Meta Graph API."""

    def __init__(self, status_code: int, detail: Union[str, Dict[str, Any]]) -> None:
        super().__init__(status_code=status_code, detail=detail)


def _build_url(endpoint: str) -> str:
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        return endpoint
    return f"{META_BASE_URL}{endpoint.lstrip('/')}"


def _sanitize(value: Any) -> Any:
    if isinstance(value, str) and "token" in value.lower():
        return "***"
    return value


async def call_meta(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    access_token: Optional[str] = None,
    timeout: float = 20.0,
) -> Any:
    """
    Appelle la Meta Graph API en journalisant les métadonnées de requête.
    Ne log jamais les tokens.
    """
    method_upper = method.upper()
    url = _build_url(endpoint)

    query: Dict[str, Any] = dict(params or {})
    if access_token:
        query.setdefault("access_token", access_token)

    # Token de fallback depuis la config si disponible
    if "access_token" not in query and settings.IG_ACCESS_TOKEN:
        query["access_token"] = settings.IG_ACCESS_TOKEN

    safe_params = {key: _sanitize(str(value)) for key, value in query.items()}

    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method=method_upper,
                url=url,
                params=query,
                json=data,
            )
    except httpx.RequestError as exc:
        duration = time.perf_counter() - start
        logger.error(
            "Meta %s %s request error after %.2fs: %s",
            method_upper,
            url,
            duration,
            exc,
        )
        raise MetaAPIError(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Meta API unreachable",
        ) from exc

    duration = time.perf_counter() - start
    snippet = response.text[:150].replace("\n", " ") if response.text else ""

    logger.info(
        "Meta %s %s status=%s duration=%.2fs params=%s response_snippet=%s",
        method_upper,
        url,
        response.status_code,
        duration,
        safe_params,
        snippet,
    )

    if response.status_code >= 400:
        detail: Union[str, Dict[str, Any]]
        try:
            detail = response.json()
        except ValueError:
            detail = {"error": response.text}

        raise MetaAPIError(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "message": "Meta API error",
                "status_code": response.status_code,
                "detail": detail,
            },
        )

    try:
        return response.json()
    except ValueError:
        return response.text


