#!/bin/bash
set -e

echo "🔄 Exécution des migrations Alembic..."
cd /app
alembic -c apps/backend/alembic.ini upgrade head

echo "🚀 Démarrage du serveur..."
cd /app/apps/backend
exec gunicorn app:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000}
