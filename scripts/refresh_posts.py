#!/usr/bin/env python3
"""
Helper CLI pour rafraîchir les posts Instagram via le job backend.

Usage :
    python scripts/refresh_posts.py --project PROJECT_UUID --limit 20

Les variables d'environnement suivantes doivent être définies :
    - DATABASE_URL
    - IG_ACCESS_TOKEN
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "apps" / "backend"

# Injecter apps/backend dans PYTHONPATH pour retrouver jobs.post_refresh
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Certains settings FastAPI exigent des variables d'environnement obligatoires.
# Pour un script local, on injecte des valeurs factices si elles sont absentes.
_MANDATORY_ENV = {
    "SECRET_KEY": "local-refresh-secret",
    "OAUTH_STATE_SECRET": "local-refresh-oauth",
    "WEBHOOK_VERIFY_TOKEN": "local-refresh-webhook",
}
for key, value in _MANDATORY_ENV.items():
    os.environ.setdefault(key, value)

try:
    from jobs.post_refresh import refresh_posts  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit(
        "Impossible d'importer jobs.post_refresh. Vérifie que tu exécutes le script "
        "depuis la racine du projet (veyl.io)."
    ) from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Rafraîchir les posts via le job backend.")
    parser.add_argument("--project", help="UUID du projet à rafraîchir (optionnel).", default=None)
    parser.add_argument("--limit", type=int, default=20, help="Nombre max de posts à traiter.")
    args = parser.parse_args()

    missing_env = [name for name in ("DATABASE_URL", "IG_ACCESS_TOKEN") if not os.getenv(name)]
    if missing_env:
        raise SystemExit(
            f"Variables d'environnement manquantes : {', '.join(missing_env)}. "
            "Exportez-les avant de lancer le script."
        )

    refresh_posts(project_id=args.project, limit=args.limit)


if __name__ == "__main__":
    main()

