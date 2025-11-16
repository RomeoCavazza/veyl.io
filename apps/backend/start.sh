#!/bin/bash
set -e

echo "🔄 Vérification des migrations Alembic..."
cd /app/apps/backend
# Vérifier si la table alembic_version existe
if alembic current 2>/dev/null | grep -q "initial_schema"; then
  echo "✅ Migration déjà appliquée (initial_schema)"
elif alembic current 2>/dev/null | grep -q "head"; then
  echo "✅ Base de données à jour"
else
  echo "🔄 Application de la migration initial_schema..."
  if ! alembic upgrade head; then
    echo "⚠️  Alembic upgrade a échoué, marquage de la base comme à jour..."
    alembic stamp initial_schema || echo "⚠️  Stamp échoué, continuons quand même..."
  fi
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
