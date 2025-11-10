FROM python:3.11-slim
# Railway cache invalidation - force reload
# Updated: 2025-10-27 - BACKEND-SPECIFIC DOCKERFILE

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# deps system minimales (certifs, build, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# code backend + dépendances
COPY . ./
RUN if [ -f apps/backend/requirements.txt ]; then \
      pip install --no-cache-dir -r apps/backend/requirements.txt; \
    elif [ -f requirements.txt ]; then \
      pip install --no-cache-dir -r requirements.txt; \
    else \
      echo "requirements.txt introuvable" && exit 1; \
    fi

# Copier start.sh (depuis la racine du repo)
COPY start.sh ./start.sh
RUN chmod +x start.sh

# ----- runtime -----
# Railway expects port from $PORT environment variable
EXPOSE $PORT

CMD ["./start.sh"]

