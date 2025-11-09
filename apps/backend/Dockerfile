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

# dépendances Python
COPY apps/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# code backend
COPY apps/backend/ ./

# Copier start.sh
COPY apps/backend/start.sh ./start.sh
RUN chmod +x start.sh

# ----- runtime -----
# Railway expects port from $PORT environment variable
EXPOSE $PORT

CMD ["./start.sh"]

