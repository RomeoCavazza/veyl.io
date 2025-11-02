# Backend Status - veyl.io

**Dernière mise à jour**: 02 novembre 2025  
**Objectif**: État des lieux backend, modules existants, services opérationnels

---

## Résumé Exécutif

### Fonctionnalités Opérationnelles

- ✅ **Backend FastAPI** opérationnel avec structure modulaire
- ✅ **Authentification OAuth** (Instagram, Facebook, Google, TikTok)
- ✅ **Meilisearch** intégré (recherche full-text ultra-rapide, typo-tolerant)
- ✅ **Redis** pour rate limiting
- ✅ **PostgreSQL** avec modèles complets (User, Post, Platform, Hashtag, Project)
- ✅ **Projects CRUD** complet (`projects`, `project_hashtags`, `project_creators`)
- ✅ **Endpoints Projects** opérationnels : `GET`, `POST`, `PUT`, `DELETE /api/v1/projects`
- ✅ **Health checks** (`/ping`, `/healthz`)

---

## Modules Backend

### Modules Existants

```
apps/backend/
├── auth_unified/          ✅ OAuth complet (IG, FB, Google, TikTok)
├── posts/                 ✅ CRUD + search Meilisearch
├── hashtags/              ✅ CRUD hashtags
├── platforms/             ✅ CRUD plateformes
├── analytics/             ✅ Endpoints analytics
├── projects/              ✅ CRUD Projects (GET, POST, PUT, DELETE)
├── jobs/                  ✅ Jobs TikTok (BackgroundTasks)
├── webhooks/              ✅ Webhooks Meta
├── core/                  ✅ Config, Redis, Rate limit
└── db/                    ✅ Models (User, Post, Platform, Hashtag, Project, ProjectHashtag, ProjectCreator)
```

---

## Base de Données

### Tables Opérationnelles

```python
User
OAuthAccount
Platform
Hashtag
PostHashtag
Post
Subscription
Project
ProjectHashtag
ProjectCreator
```

**Architecture**: Tables de liaison (`project_hashtags`, `project_creators`) réutilisent les tables existantes (`hashtags`, `platforms`) pour éviter la duplication.

---

## API Endpoints

### Endpoints Projects (Opérationnels)

```
GET    /api/v1/projects           Liste projets utilisateur
POST   /api/v1/projects           Créer projet
GET    /api/v1/projects/{id}      Détails projet (avec relations)
PUT    /api/v1/projects/{id}      Mettre à jour projet
DELETE /api/v1/projects/{id}      Supprimer projet
```

### Endpoints Autres Modules (Opérationnels)

```
GET  /api/v1/auth/*              OAuth (start, callback, me)
GET  /api/v1/posts/search        Recherche posts Meilisearch
GET  /api/v1/posts/trending      Posts trending
GET  /api/v1/hashtags/*          CRUD hashtags
GET  /api/v1/platforms/*         CRUD plateformes
GET  /api/v1/analytics/*         Endpoints analytics
POST /api/v1/jobs/sync/tiktok    Jobs TikTok (BackgroundTasks)
GET  /ping, /healthz             Health checks
```

### Endpoints Roadmap (Phase 2+)

```
POST   /api/v1/projects/{id}/cluster       Clustering IA (Qdrant)
POST   /api/v1/projects/{id}/lookalikes    Recherche lookalikes
POST   /api/v1/projects/{id}/reports/weekly Génération Weekly Digest
GET    /api/v1/projects/{id}/reports       Liste rapports
POST   /api/v1/reports/{id}/export/gamma   Export Gamma (Phase 4)
POST   /api/v1/reports/{id}/export/pomelli Export Pomelli (Phase 4)
```

**Note**: Ces endpoints seront implémentés dans les phases futures avec feature flags.

---

## Services & Infrastructure

### Services Opérationnels

```python
services/meilisearch_client.py    ✅ Meilisearch intégré (ultra-rapide, typo-tolerant)
services/tiktok_service.py        ✅ TikTok API client
services/cache.py                 ✅ Cache Redis
core/redis_client.py             ✅ Redis client
core/ratelimit.py                ✅ Rate limiting
```

### Services Roadmap (Phase 2+)

```python
services/qdrant_client.py         🔄 Qdrant (vectors) - Phase 2
services/ai_service.py            🔄 LLM wrapper (OpenAI/Anthropic) - Phase 2
services/embeddings_service.py    🔄 Génération embeddings - Phase 2
services/vertex_service.py        🔄 Vertex AI (vidéo) - Phase 4
services/gamma_service.py         🔄 Gamma API export - Phase 4
services/pomelli_service.py       🔄 Pomelli API export - Phase 4
```

---

## Configuration

### Variables d'Environnement Configurées

```python
DATABASE_URL                      ✅ PostgreSQL connection string
SECRET_KEY                        ✅ JWT secret key
ACCESS_TOKEN_EXPIRE_MINUTES       ✅ Token expiration (default: 30)
REDIS_URL                         ✅ Redis connection string
OAuth (IG, FB, Google, TikTok)    ✅ OAuth credentials
MEILI_HOST, MEILI_MASTER_KEY      ✅ Meilisearch configuration
```

### Variables d'Environnement Roadmap (Phase 2+)

```python
QDRANT_URL, QDRANT_API_KEY        🔄 Phase 2
OPENAI_API_KEY, MISTRAL_API_KEY   🔄 Phase 2
VERTEX_AI_PROJECT, VERTEX_AI_REGION 🔄 Phase 4
GAMMA_API_KEY                     🔄 Phase 4
POMELLI_API_KEY                   🔄 Phase 4

# Feature flags (à implémenter)
ENABLE_AI_CLUSTERS                🔄 Phase 2
ENABLE_GAMMA_EXPORT               🔄 Phase 4
ENABLE_POMELLI_EXPORT             🔄 Phase 4
ENABLE_VERTEX_VIDEO               🔄 Phase 4
ENABLE_AGENT_SCOUT                🔄 Phase 3
ENABLE_AGENT_SCRIBE               🔄 Phase 3
ENABLE_AGENT_PLANNER              🔄 Phase 3
```

---

## Dépendances

### Dépendances Installées

```python
fastapi, uvicorn, gunicorn
sqlalchemy, alembic, psycopg
redis, slowapi, limits
meilisearch
pydantic, python-jose, bcrypt
httpx, python-dotenv
```

### Dépendances Roadmap (Phase 2+)

```python
celery                    🔄 Workers background - Phase 3
celery[redis]            🔄 Celery + Redis - Phase 3
qdrant-client            🔄 Vector database - Phase 2
openai                   🔄 LLM API - Phase 2
anthropic                🔄 LLM API (optionnel) - Phase 2
google-cloud-aiplatform  🔄 Vertex AI - Phase 4
sentry-sdk               🔄 Observabilité - Phase 4
prometheus-fastapi-instrumentator  🔄 Métriques - Phase 4
```

---

## Plan d'Action (Roadmap)

### Phase 1: Foundations ✅ (Terminé)

1. ✅ Modèles Projects en base de données
2. ✅ Endpoints Projects CRUD (GET, POST, PUT, DELETE)
3. ✅ Interface My Projects
4. ✅ Onboarding simplifié

### Phase 2: Recherche & IA (À venir)

1. 🔄 Intégration Qdrant + service embeddings
2. 🔄 Endpoints clustering (`/api/v1/projects/{id}/cluster`)
3. 🔄 Recherche sémantique dans posts/créateurs

### Phase 3: Workers & Agents (À venir)

1. 🔄 Configuration Celery + jobs background
2. 🔄 Agents backend (Scout, Scribe, Planner)
3. 🔄 Génération Weekly Digest

### Phase 4: Features Avancées (À venir)

1. 🔄 Multi-tenant (organisations)
2. 🔄 Vertex AI (analyse vidéo, on-demand)
3. 🔄 Export Gamma/Pomelli
4. 🔄 docker-compose pour développement local

---

## Points Forts

- ✅ Architecture FastAPI propre et modulaire
- ✅ OAuth multi-plateformes fonctionnel
- ✅ Meilisearch intégré
- ✅ Projects CRUD complet avec relations
- ✅ Structure prête pour scaling progressif

---

---

## Meilisearch - Moteur de Recherche

**Meilisearch** est le moteur de recherche central de veyl.io. Il indexe et recherche des millions de posts en temps réel avec une performance exceptionnelle.

### Caractéristiques
- **Typo-tolerance** : Trouve les résultats même avec des fautes de frappe
- **Performance** : Recherche en millisecondes
- **Facettes** : Filtrage avancé par plateforme, date, hashtags
- **Index automatique** : Mise à jour en temps réel

### Intégration
- Service client: `apps/backend/services/meilisearch_client.py`
- Index: `posts` avec champs indexés (caption, hashtags, author, platform_id)
- Endpoint: `GET /api/v1/posts/search`

**Documentation**: [Meilisearch Docs](https://www.meilisearch.com/docs)

---

## Partenariats & Intégrations

### Meta for Developers
- Partenaire officiel Instagram Graph API et Facebook Pages API
- Permissions: `instagram_business_basic`, `pages_read_engagement`, `Page Public Content Access`
- Documentation: [Meta for Developers](https://developers.facebook.com/)

### TikTok for Developers
- Partenaire officiel TikTok Login Kit et TikTok API
- Permissions: `user.info.basic`, `user.info.profile`, `user.info.stats`, `video.list`
- Documentation: [TikTok for Developers](https://developers.tiktok.com/)

---

## Communauté Open Source

**veyl.io** est entièrement **open source** sur GitHub :
- Repository: [https://github.com/RomeoCavazza/veyl.io](https://github.com/RomeoCavazza/veyl.io)
- Discord: [https://discord.gg/TKbNuuV4sX](https://discord.gg/TKbNuuV4sX)
- Partenariats académiques: **ISCOM Paris** et **EPITECH Paris**

---

**Référence**: [architecture.md](./architecture.md) pour architecture complète, [api-reference.md](./api-reference.md) pour endpoints détaillés.
