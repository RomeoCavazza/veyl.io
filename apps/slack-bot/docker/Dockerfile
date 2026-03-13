# Dockerfile optimisé pour Revolver AI Bot
FROM python:3.10-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Création de l'utilisateur non-root
RUN useradd --create-home --shell /bin/bash revolver

# Définition du répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY requirements.txt pyproject.toml setup.py ./

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY src/ ./src/
COPY config/ ./config/
COPY resources/ ./resources/

# Changement de propriétaire
RUN chown -R revolver:revolver /app

# Utilisateur non-root
USER revolver

# Exposition du port
EXPOSE 8000

# Commande par défaut
CMD ["python", "-m", "src.bot"]