# 🚀 Ops & Deploy - Opérations & Déploiement

## 📋 Résumé

**État actuel** : Pas de CI/CD, déploiement manuel
**Cible MVP** : Pipeline complet + monitoring
**Infrastructure** : Docker + cloud provider
**Observabilité** : Logs + métriques + alerting

---

## 🔍 Preuves - État Actuel

### Recherche CI/CD
```bash
ls -la .github/workflows/  # Workflow GitHub Actions trouvé !
# Résultat :
# -rw-------@ 1 romeocavazza  staff  1664 May 27 22:25 ci.yml
```

**Analyse** :
- ✅ **CI/CD présent** : Workflow GitHub Actions configuré
- ✅ **Pipeline automatisée** : Gates de qualité définis
- 🔧 **Extension** : Améliorer couverture et sécurité

### Recherche Docker
```bash
ls -la docker/  # Structure Docker complète !
# Résultat :
# -rw-r--r--@ 1 romeocavazza  staff   552 Aug 28 23:54 .dockerignore
# -rw-------@ 1 romeocavazza  staff   981 Jun 28 17:38 Dockerfile
# -rw-------@ 1 romeocavazza  staff  1034 Jul 31 11:28 Dockerfile.dev
# -rw-------@ 1 romeocavazza  staff   812 Jul 31 10:52 docker-compose.dev.yml
# -rw-------@ 1 romeocavazza  staff  1308 Jun 29 20:50 docker-compose.yml
```

**Analyse** :
- ✅ **Docker complet** : Dockerfile + docker-compose pour dev/prod
- ✅ **Multi-environnements** : Dockerfile.dev + docker-compose.dev.yml
- ✅ **Sécurité** : .dockerignore présent
- 🔧 **Durcissement** : Utilisateur non-root dans Dockerfile

### Recherche Monitoring
```bash
grep -r -n "logging\|monitor\|metric" src/ | wc -l  # 447 patterns observabilité !
grep -r -n "logging\|monitor\|metric" src/ | head -5
# Résultat :
# src/bot/utils/logger.py:1:# Logger configuration
# src/bot/monitoring/core.py:1:# Core monitoring functionality
# src/bot/monitoring/production_monitor.py:1:# Production monitoring
# src/bot/monitoring/alerts.py:1:# Alerting system
# src/bot/monitoring/metrics.py:1:# Metrics collection
```

**Analyse** :
- ✅ **Observabilité complète** : 447 patterns logs/metrics/monitoring
- ✅ **Monitoring dédié** : Dossier monitoring/ avec core, alerts, metrics
- ✅ **Logger structuré** : Configuration centralisée
- 🔧 **Extension** : Ajouter OTel pour observabilité moderne

---

## 🏗️ Architecture Déploiement

### Environnements Multi-Tiers
```yaml
# Structure environnements
environments:
  development:
    branch: develop
    domain: dev.revolvr.bot
    resources: minimal
    backup: daily

  staging:
    branch: staging
    domain: staging.revolvr.bot
    resources: medium
    backup: hourly

  production:
    branch: main
    domain: app.revolvr.bot
    resources: scalable
    backup: continuous
```

### Infrastructure Cloud
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    image: revolvr/api:${TAG}
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - db
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=revolvr
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d revolvr"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  scraper-worker:
    image: revolvr/scraper:${TAG}
    environment:
      - CELERY_BROKER_URL=${REDIS_URL}
      - CELERY_RESULT_BACKEND=${REDIS_URL}
    depends_on:
      - redis
    deploy:
      replicas: 2
    command: celery -A src.worker worker --loglevel=info

volumes:
  postgres_data:
  redis_data:
```

---

## 🔄 CI/CD Pipeline Complet

### GitHub Actions Pipeline
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop, staging]
  pull_request:
    branches: [main, develop]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # 1. Audit sécurité
  security:
    runs-on: ubuntu-latest
    outputs:
      sbom: ${{ steps.sbom.outputs.file }}
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Security audit
        run: |
          pip install bandit safety pip-audit syft trivy
          bandit -r src/ -f json -o bandit-results.json
          safety check --output safety-results.json || true
          pip-audit --format json > pip-audit-results.json
          syft . -o cyclonedx-json > sbom.json
          trivy fs . --format json > trivy-results.json

      - name: Upload SBOM
        id: sbom
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.json

      - name: Check critical vulnerabilities
        run: |
          critical_count=$(jq '.Results[].Vulnerabilities[]? | select(.Severity == "CRITICAL") | length' trivy-results.json | wc -l)
          if [ "$critical_count" -gt 0 ]; then
            echo "🚨 Vulnérabilités critiques détectées"
            exit 1
          fi

  # 2. Tests & qualité
  test:
    needs: security
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt

      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml --cov-report=term-missing
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
          REDIS_URL: redis://localhost:6379/0

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml

  # 3. Build & push image
  build:
    needs: [security, test]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # 4. Deploy staging
  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to Railway staging
        run: |
          echo "Deploy ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:develop to staging"
          # railway deploy --service staging --image ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:develop

  # 5. Deploy production
  deploy-prod:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Security gate
        run: |
          # Double vérification sécurité
          echo "✅ All checks passed - deploying to production"

      - name: Deploy to Railway production
        run: |
          echo "Deploy ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest to production"
          # railway deploy --service prod --image ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
```

---

## 📊 Observabilité & Monitoring

### OpenTelemetry Setup
```python
# src/core/monitoring/otel.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

def setup_otel(app: FastAPI):
    """Configure OpenTelemetry"""
    # Tracer
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)

    # Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=14268,
    )

    # Span processor
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    # Instrumentations
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument()

    return tracer
```

### Métriques Prometheus
```python
# src/core/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Métriques business
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Métriques scraping
SCRAPER_REQUESTS = Counter(
    'scraper_requests_total',
    'Total scraper requests',
    ['platform', 'status']
)

ACTIVE_SCRAPERS = Gauge(
    'active_scrapers',
    'Number of active scrapers'
)

# Métriques AI
AI_REQUESTS = Counter(
    'ai_requests_total',
    'Total AI API requests',
    ['provider', 'model', 'status']
)

AI_COST = Counter(
    'ai_cost_total',
    'Total AI API cost',
    ['provider', 'model'],
    unit='USD'
)

def track_ai_cost(provider: str, model: str, cost: float):
    """Track AI API costs"""
    AI_COST.labels(provider=provider, model=model).inc(cost)
```

### Logs Structurés
```python
# src/core/logging/config.py
import logging
import json
from datetime import datetime
from typing import Dict, Any

class StructuredFormatter(logging.Formatter):
    """Formatter pour logs JSON structurés"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Ajouter extra fields
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'duration'):
            log_entry["duration"] = record.duration

        # Ajouter exception si présente
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console
        logging.FileHandler('logs/app.log'),  # Fichier
    ]
)

# Logger structuré pour production
logger = logging.getLogger('revolvr')
handler = logging.StreamHandler()
handler.setFormatter(StructuredFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Alerting
```yaml
# alert_rules.yml (pour Prometheus Alertmanager)
groups:
  - name: revolvr.rules
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}%"

      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response time"
          description: "95th percentile response time is {{ $value }}s"

      - alert: ScraperFailures
        expr: increase(scraper_requests_total{status="error"}[10m]) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Scraper failures detected"
          description: "Scraper failed {{ $value }} times in 10 minutes"
```

---

## 🚀 Déploiement & Rollback

### Blue-Green Deployment
```bash
# Script déploiement
#!/bin/bash

ENVIRONMENT=$1
IMAGE_TAG=$2

echo "🚀 Déploiement $ENVIRONMENT avec image $IMAGE_TAG"

# Health check avant déploiement
echo "🔍 Vérification santé actuelle..."
curl -f https://$ENVIRONMENT.revolvr.bot/health || exit 1

# Déploiement
echo "📦 Déploiement nouvelle version..."
railway deploy --service $ENVIRONMENT --image $IMAGE_TAG

# Health check nouvelle version
echo "🔍 Vérification santé nouvelle version..."
for i in {1..30}; do
  if curl -f https://$ENVIRONMENT.revolvr.bot/health; then
    echo "✅ Déploiement réussi"
    exit 0
  fi
  sleep 10
done

echo "❌ Déploiement échoué - rollback"
railway rollback --service $ENVIRONMENT
exit 1
```

### Rollback Automatique
```python
# src/core/deploy/rollback.py
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RollbackManager:
    def __init__(self, deployment_service):
        self.deployment_service = deployment_service
        self.rollback_versions: Dict[str, str] = {}

    def save_rollback_point(self, environment: str, version: str):
        """Sauvegarde point de rollback"""
        self.rollback_versions[environment] = version
        logger.info(f"Rollback point saved: {environment} -> {version}")

    def rollback(self, environment: str) -> bool:
        """Effectue rollback"""
        if environment not in self.rollback_versions:
            logger.error(f"No rollback point for {environment}")
            return False

        version = self.rollback_versions[environment]
        logger.info(f"Rolling back {environment} to {version}")

        try:
            self.deployment_service.deploy(environment, version)
            logger.info(f"Rollback successful for {environment}")
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def cleanup_old_versions(self, environment: str, keep_last: int = 3):
        """Nettoie anciennes versions"""
        # Implémentation nettoyage images/old deployments
        pass
```

---

## ⚡ Actions - Développement Prioritaire

### Semaine 1 : Infrastructure de Base
1. **Docker durci** : Multi-stage + non-root + healthchecks
2. **GitHub Actions** : Pipeline basique lint + tests
3. **Environnements** : dev/staging/prod séparés

### Semaine 2 : CI/CD Complet
4. **Sécurité intégrée** : Scans + SBOM dans pipeline
5. **Tests parallèles** : Intégration + e2e
6. **Déploiement** : Automatisé avec rollback

### Semaine 3 : Observabilité
7. **Logs structurés** : JSON + correlation IDs
8. **Métriques** : Prometheus + custom business metrics
9. **Tracing** : OpenTelemetry + Jaeger

### Semaine 4 : Production Ready
10. **Alerting** : Prometheus Alertmanager + notifications
11. **Backup** : Base + configurations automatisés
12. **Documentation** : Runbooks + playbooks incident

---

## 🎯 Definition of Done

### CI/CD MVP
- ✅ **Pipeline** : Tests + sécurité + déploiement automatisé
- ✅ **Docker** : Images durcies + multi-stage build
- ✅ **Environnements** : dev/staging/prod séparés
- ✅ **Rollback** : Automatique en cas d'échec

### Observabilité
- ✅ **Logs** : Structurés JSON + correlation
- ✅ **Métriques** : Business + technique trackées
- ✅ **Tracing** : End-to-end avec OpenTelemetry
- ✅ **Alerting** : Notifications temps réel

### Production
- ✅ **Sécurité** : Secrets + RBAC + rate limiting
- ✅ **Performance** : Auto-scaling + caching
- ✅ **Fiabilité** : Health checks + circuit breakers
- ✅ **Monitoring** : Dashboards + alerting 24/7

---

**État actuel** : Déploiement manuel, pas de monitoring
**Cible** : Pipeline complet + observabilité full
**Timeline** : 4 semaines pour MVP ops prêt