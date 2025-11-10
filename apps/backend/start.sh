#!/bin/bash
set -e

echo "🔄 Exécution des migrations Alembic..."
cd /app/apps/backend
if ! alembic upgrade head; then
  echo "⚠️  Alembic upgrade a échoué, tentative de stamp head..."
  alembic stamp head
fi

echo "🚀 Démarrage du serveur..."

PORT=${PORT:-8000}
exec gunicorn app:app \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:${PORT} \
  --workers 1 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
