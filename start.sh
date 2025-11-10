#!/bin/bash
set -e

echo "🔄 Exécution des migrations Alembic..."
cd /app/apps/backend
alembic upgrade head

echo "🚀 Démarrage du serveur..."
exec gunicorn app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000}
