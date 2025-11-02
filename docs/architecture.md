# Architecture & Vision - veyl.io

**Dernière mise à jour**: 02 novembre 2025

---

## Vision Produit

**veyl.io** est une plateforme de veille culturelle et d'analyse des tendances sur les réseaux sociaux. La solution permet aux créateurs, agences et marques de surveiller, analyser et anticiper les tendances émergentes sur Instagram et TikTok.

**Positionnement**: Workspace OSINT (Open Source Intelligence) multi-plateformes pour l'analyse de contenu social media public.

**veyl.io** est développé en collaboration avec les étudiants de **ISCOM Paris** et **EPITECH Paris**, et est entièrement **open source** sur GitHub.

---

## Stack Technique Actuel

| Composant | Technologie | Fonction | Statut |
|-----------|------------|----------|--------|
| **API Backend** | FastAPI | API REST, logique métier, orchestration | ✅ Opérationnel |
| **Base de données** | PostgreSQL | Persistence des données, relations | ✅ Opérationnel |
| **Cache** | Redis | Rate limiting, sessions | ✅ Opérationnel |
| **Recherche full-text** | Meilisearch | Recherche ultra-rapide, typo-tolerant, facettes | ✅ Opérationnel |
| **Interface** | React + TypeScript | Interface utilisateur web | ✅ Opérationnel |
| **Infrastructure** | Railway (API) + Vercel (Frontend) | Hébergement et déploiement | ✅ Opérationnel |

---

## Modules Backend

```
apps/backend/
├── auth_unified/          ✅ OAuth (Instagram, Facebook, Google, TikTok)
├── posts/                 ✅ CRUD + recherche Meilisearch
├── hashtags/              ✅ CRUD hashtags
├── platforms/             ✅ CRUD plateformes
├── analytics/             ✅ Endpoints analytics
├── projects/              ✅ CRUD Projects (GET, POST, PUT, DELETE)
├── jobs/                  ✅ Jobs TikTok (BackgroundTasks)
├── webhooks/              ✅ Webhooks Meta
├── core/                  ✅ Configuration, Redis, Rate limiting
└── db/                    ✅ Models SQLAlchemy (User, Post, Platform, Hashtag, Project)
```

---

## Fonctionnalités Opérationnelles

- ✅ **Authentification OAuth** multi-plateformes (Instagram, Facebook, Google, TikTok)
- ✅ **Recherche de posts** via Meilisearch
- ✅ **Système Projects** complet :
  - Tables: `projects`, `project_hashtags`, `project_creators`
  - API CRUD: `GET`, `POST`, `PUT`, `DELETE /api/v1/projects`
  - Relations avec hashtags et créateurs existants
- ✅ **Interface utilisateur React** avec navigation complète :
  - Pages Projects (`/projects`, `/projects/new`, `/projects/:id`)
  - Onglets: Watchlist, Grille, Analytics
  - Composant `ProjectPanel` réutilisable
  - Dialog Instagram-style pour posts
  - Autocomplétion tags inline
- ✅ **Base de données PostgreSQL** normalisée avec tables de liaison

---

## Schéma Base de Données

### Tables Core

- `users` - Comptes utilisateurs
- `oauth_accounts` - Comptes OAuth liés
- `platforms` - Plateformes supportées (Instagram, TikTok)
- `hashtags` - Hashtags surveillés (réutilisé pour projects)
- `posts` - Posts collectés (réutilisé pour projects)
- `post_hashtags` - Relation posts ↔ hashtags
- `subscriptions` - Abonnements et quotas utilisateurs

### Tables Projects

- `projects` - Projets de monitoring
  - Colonnes: `id`, `user_id`, `name`, `description`, `status`, `platforms` (JSON), `scope_type`, `scope_query`
  - Métriques: `creators_count`, `posts_count`, `signals_count`
  - Timestamps: `last_run_at`, `last_signal_at`, `created_at`, `updated_at`

- `project_hashtags` - Relation projets ↔ hashtags (réutilise `hashtags`)
  - Colonnes: `project_id`, `hashtag_id`, `added_at`
  - Contrainte unique: `(project_id, hashtag_id)`

- `project_creators` - Créateurs suivis par projet
  - Colonnes: `project_id`, `creator_username`, `platform_id`, `added_at`
  - Contrainte unique: `(project_id, platform_id, creator_username)`

**Architecture**: Tables de liaison pour éviter la duplication, réutilisation des tables existantes.

---

## Workflow Utilisateur

### Parcours Principal

1. **Onboarding** (`/projects/new`)
   - Création d'un projet avec nom et description
   - Ajout de hashtags et/ou créateurs à suivre (tags inline avec autocomplétion)
   - Sélection des plateformes (Instagram, TikTok)

2. **Gestion des Projets** (`/projects`)
   - Liste de tous les projets de l'utilisateur
   - Layout amélioré: photos créateurs en cascade, posts récents
   - Accès rapide aux projets actifs

3. **Détails Projet** (`/projects/:id`)
   - **ProjectPanel** réutilisable (nom, description, métriques, actions)
   - **Onglet Watchlist**: Layout 50/50 (ProjectPanel + Liste créateurs), Feed posts, dialog Instagram-style
   - **Onglet Grille**: Tableau triable des posts
   - **Onglet Analytics**: Layout 50/50 (ProjectPanel + Graphiques), charts engagement, reach, top creators

---

## Roadmap Technique

### Phase 1: Foundations ✅ (Terminé)

- [x] Modèles Projects en base de données
- [x] Endpoints Projects CRUD (GET, POST, PUT, DELETE)
- [x] Interface My Projects avec layout amélioré
- [x] Onboarding simplifié avec tags inline
- [x] ProjectPanel réutilisable
- [x] Onglets Watchlist, Grille, Analytics

### Phase 2: Recherche & IA (À venir)

- [ ] Intégration Qdrant + service embeddings
- [ ] Endpoints clustering (`/api/v1/projects/{id}/cluster`)
- [ ] Recherche sémantique dans posts/créateurs
- [ ] Investigate Mode (recherche avancée dans projet)

### Phase 3: Workers & Agents (À venir)

- [ ] Configuration Celery + workers background
- [ ] Agents backend (Scout, Scribe, Planner)
- [ ] Génération Weekly Digest
- [ ] Jobs asynchrones pour ingestion

### Phase 4: Features Avancées (À venir)

- [ ] Multi-tenant (organisations)
- [ ] Vertex AI (analyse vidéo, on-demand)
- [ ] Gamma/Pomelli export
- [ ] docker-compose pour développement local
- [ ] Feature flags système

---

## Configuration & Environnement

**Note technique**: FastAPI est configuré avec `redirect_slashes=False` dans `app.py` pour éviter les redirections 307 lors du proxy Vercel. Les routes dans `projects_endpoints.py` utilisent des chaînes vides (`""`) au lieu de `"/"` pour correspondre exactement aux URLs sans slash final.

### Variables Backend Requises

```bash
# Database
DATABASE_URL=postgresql+psycopg2://...

# Authentication
SECRET_KEY=...
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OAuth Providers
IG_APP_ID=...
IG_APP_SECRET=...
FB_APP_ID=...
FB_APP_SECRET=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
TIKTOK_CLIENT_KEY=...
TIKTOK_CLIENT_SECRET=...

# Services
REDIS_URL=redis://...
MEILI_HOST=...
MEILI_MASTER_KEY=...

# Advanced (Phase 2+)
QDRANT_URL=...
OPENAI_API_KEY=...
ENABLE_AI_CLUSTERS=false
ENABLE_GAMMA_EXPORT=false
```

---

## Principes d'Architecture

1. **MVP First** - Implémentation progressive, focus sur App Review
2. **Feature Flags** - Toutes fonctionnalités avancées derrière flags
3. **Réutilisabilité** - Tables de liaison plutôt que duplication de données
4. **Progressive Enhancement** - Scaling technologies uniquement si nécessaire
5. **Simplicité** - Architecture claire, éviter sur-ingénierie

---

## App Review Mode (Meta/TikTok)

Pour la validation **App Review Meta** et **TikTok**, l'application fonctionne en **mode démonstration** avec des datasets mock/fake permettant d'afficher le fonctionnement complet du flux utilisateur (OAuth → création projet → visualisation → analytics).

**Justification**: Les reviewers évaluent la **compréhension du flux** et la conformité aux politiques. L'ingestion réelle sera activée après obtention de l'accès Public Content.

**Statut**: ✅ Datasets fake disponibles dans `apps/frontend/src/lib/fakeData.ts`

**Documentation complète des permissions**: Voir [oauth-scopes.md](./oauth-scopes.md)

---

## Documentation Complémentaire

- **[README.md](./README.md)** - Index de la documentation
- **[backend.md](./backend.md)** - Modules backend détaillés, services, plan d'action
- **[frontend.md](./frontend.md)** - Structure frontend, pages, composants
- **[database.md](./database.md)** - Schéma base de données complet
- **[api-reference.md](./api-reference.md)** - Endpoints API, schémas, exemples
- **[oauth-scopes.md](./oauth-scopes.md)** - Permissions OAuth Meta/Facebook et TikTok
