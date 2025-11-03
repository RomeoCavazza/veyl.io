# Veyl.io - Social Media Intelligence Platform

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Meilisearch](https://img.shields.io/badge/Meilisearch-FF5C5C?style=for-the-badge&logo=meilisearch&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)
![Railway](https://img.shields.io/badge/Railway-131415?style=for-the-badge&logo=railway&logoColor=white)

Plateforme de veille culturelle et d'analyse des tendances sur les réseaux sociaux.

**Mission**: Permettre aux créateurs, agences et marques de surveiller, analyser et anticiper les tendances émergentes sur Instagram et TikTok via un workspace dédié.

---

## Démarrage Rapide

### Backend (FastAPI)

```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (React)

```bash
cd apps/frontend
npm install
npm run dev
```

**Accès local**:
- Frontend: `http://localhost:8081`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

#### Build Frontend

```bash
cd apps/frontend
npm run build
```

#### Structure Frontend

```
src/
├── components/
│   ├── ui/              Composants Radix UI complets (shadcn/ui)
│   ├── Navbar.tsx       Navigation principale
│   ├── ProjectPanel.tsx Panneau projet réutilisable
│   └── AISearchBar.tsx  Barre de recherche
├── contexts/
│   ├── AuthContext.tsx  Gestion authentification
│   └── WatchlistContext.tsx Watchlist state
├── pages/
│   ├── Landing.tsx      Page d'accueil
│   ├── Auth.tsx         Login/Register
│   ├── Search.tsx       Recherche posts (Meilisearch)
│   ├── Projects.tsx     My Projects (liste)
│   ├── ProjectsNew.tsx  Création projet (tags inline)
│   ├── ProjectDetail.tsx Détails projet (Watchlist/Grille/Analytics)
│   ├── CreatorDetail.tsx Détails créateur (Feed/Grid/Analytics)
│   ├── Analytics.tsx    Analytics dashboard global
│   ├── Profile.tsx      Profil utilisateur + OAuth
│   ├── Community.tsx    Community Hub (GitHub + Discord)
│   ├── Enterprise.tsx   Solutions entreprise
│   └── Docs.tsx         Documentation
├── assets/
│   ├── css/             Styles (github-card, discord-button, browser-mockup, image-stack)
│   └── img/             Images (logo, captures écran)
└── lib/
    ├── api.ts           Client API (auth, search, projects)
    ├── fakeData.ts      Datasets mock pour développement/App Review
    └── utils/
        └── imageStack.ts Utilitaires pour animations cascade
```

#### Pages Frontend Principales

**`/projects`** - My Projects
- Liste projets avec layout amélioré
- Photos créateurs en cascade (3 premiers)
- Posts récents en ligne horizontale scrollable

**`/projects/new`** - Onboarding
- Tags hashtags/créateurs inline dans l'input
- Autocomplétion avec suggestions en temps réel
- Photos de profil dans suggestions créateurs
- Croix de suppression sur chaque tag

**`/projects/:id`** - Project Detail
- **3 onglets**: Watchlist, Grille, Analytics
- **ProjectPanel** réutilisable (métriques, actions)
- Dialog Instagram-style pour posts
- Tableau triable dans onglet Grille

**`/projects/:id/creator/:username`** - Creator Detail
- **3 onglets**: Feed, Grid, Analytics
- Stats regroupées sous description
- 4 graphiques en layout 2x2
- Dialog post au clic

---

## Stack Technique

### Backend
- **FastAPI** - Framework API Python asynchrone
- **PostgreSQL** - Base de données relationnelle (Railway)
- **SQLAlchemy + Alembic** - ORM et migrations
- **Redis** - Cache et rate limiting
- **Meilisearch** - Moteur de recherche full-text

### Frontend
- **React 18** - Framework UI
- **TypeScript** - Typage statique
- **Vite** - Build tool et dev server
- **Tailwind CSS** - Framework CSS utility-first
- **Radix UI + shadcn/ui** - Composants UI accessibles (headless)
- **React Router** - Gestion de navigation
- **Recharts** - Bibliothèque de graphiques
- **date-fns** - Manipulation de dates et formatage relatif

### Infrastructure
- **Railway** - Hébergement backend (auto-deploy)
- **Vercel** - Hébergement frontend (auto-deploy) avec proxy vers Railway
- **Configuration**: FastAPI avec `redirect_slashes=False`, routes avec chaînes vides (`""`) pour éviter redirections 307

### Intégrations Social Media

#### Meta Developer Platform
- **Instagram Graph API** - Accès aux contenus publics Instagram Business
- **Facebook Pages API** - Gestion des pages et insights
- **OAuth 2.0** - Authentification via Meta/Facebook
- **Permissions**: `instagram_business_basic`, `pages_read_engagement`, `Page Public Content Access`, `Meta oEmbed Read`

**Ressources**: 
- [Meta for Developers](https://developers.facebook.com/)
- [Instagram Graph API Docs](https://developers.facebook.com/docs/instagram-api)

#### TikTok Developer Platform
- **TikTok Login Kit** - Authentification OAuth
- **TikTok API** - Accès aux vidéos publiques et statistiques créateurs
- **Permissions**: `user.info.basic`, `user.info.profile`, `user.info.stats`, `video.list`

**Ressources**: 
- [TikTok for Developers](https://developers.tiktok.com/)
- [TikTok Login Kit Docs](https://developers.tiktok.com/doc/login-kit-web)

---

## Structure du Projet

```
veyl.io/
├── apps/
│   ├── backend/              # Application FastAPI
│   │   ├── app.py           # Point d'entrée
│   │   ├── core/            # Configuration, Redis, rate limiting
│   │   ├── db/              # Models SQLAlchemy, migrations
│   │   │   ├── models.py
│   │   │   └── migrations/
│   │   ├── auth_unified/    # OAuth (IG, FB, Google, TikTok)
│   │   ├── posts/           # CRUD posts + recherche
│   │   ├── projects/        # CRUD Projects
│   │   ├── analytics/       # Endpoints analytics
│   │   └── requirements.txt
│   │
│   └── frontend/            # Application React
│       ├── src/
│       │   ├── pages/      # Pages (Landing, Search, Projects, etc.)
│       │   ├── components/ # Composants UI réutilisables
│       │   ├── contexts/   # Context providers (Auth, etc.)
│       │   ├── lib/        # Utilitaires, client API
│       │   └── App.tsx     # Router principal
│       └── package.json
│
├── docs/                    # Documentation technique organisée
│   ├── README.md            # Index de la documentation
│   ├── architecture.md      # Architecture complète
│   ├── backend.md           # État backend
│   ├── frontend.md          # État frontend
│   ├── database.md          # Schéma base de données
│   ├── api-reference.md     # Référence API
│   └── oauth-scopes.md      # Permissions OAuth
├── DATA.md                  # Schéma DB (référence rapide)
├── SCOPES.md                # Liste scopes OAuth (référence)
└── README.md                # Ce fichier
```

---

## Configuration

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql+psycopg2://user:pass@host:port/db

# Authentication
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Cache & Rate Limiting
REDIS_URL=redis://localhost:6379/0

# OAuth Providers
IG_APP_ID=your-instagram-app-id
IG_APP_SECRET=your-instagram-app-secret
IG_REDIRECT_URI=https://veyl.io/auth/callback

FB_APP_ID=your-facebook-app-id
FB_APP_SECRET=your-facebook-app-secret
FB_REDIRECT_URI=https://veyl.io/auth/facebook/callback

# Search Engine
MEILI_HOST=http://localhost:7700
MEILI_MASTER_KEY=your-master-key
```

### Frontend (.env.local)

```bash
VITE_API_URL=http://localhost:8000  # Backend API URL (optionnel, proxy Vercel par défaut)
```

**Note**: Pour la production, Vercel proxy automatiquement vers Railway backend. La variable `VITE_API_URL` est optionnelle et permet un accès direct au backend en développement.

---

## Base de Données

### Migrations

```bash
cd apps/backend
alembic upgrade head
```

### Tables Principales

- `users` - Comptes utilisateurs
- `projects` - Projets de monitoring
- `project_hashtags` - Relation projets ↔ hashtags
- `project_creators` - Créateurs suivis par projet
- `hashtags` - Hashtags surveillés
- `posts` - Posts collectés
- `platforms` - Plateformes supportées
- `oauth_accounts` - Comptes OAuth liés

Voir [docs/architecture.md](docs/architecture.md) et [docs/database.md](docs/database.md) pour le schéma complet.

---

## API Endpoints

### Authentification
- `POST /api/v1/auth/register` - Inscription
- `POST /api/v1/auth/login` - Connexion
- `GET /api/v1/auth/me` - Profil utilisateur

### OAuth
- `GET /api/v1/auth/{provider}/start` - Init OAuth
- `GET /api/v1/auth/{provider}/callback` - Callback OAuth

### Projects
- `GET /api/v1/projects` - Liste projets
- `POST /api/v1/projects` - Créer projet
- `GET /api/v1/projects/{id}` - Détails projet (avec relations)
- `PUT /api/v1/projects/{id}` - Mettre à jour projet
- `DELETE /api/v1/projects/{id}` - Supprimer projet

### Recherche
- `GET /api/v1/posts/search` - Recherche posts (Meilisearch - ultra-rapide, typo-tolerant)
- `GET /api/v1/posts/trending` - Posts trending

### Système
- `GET /ping` - Health check
- `GET /docs` - Documentation Swagger (OpenAPI)

---

## Tests Locaux

### Backend
```bash
cd apps/backend
python -c "from app import app; print('✅ API OK')"
```

### Frontend
```bash
cd apps/frontend
npm run build  # Test compilation
```

---

## Déploiement

### Backend (Railway)
- Déploiement automatique sur push vers `main`
- Variables d'environnement configurées dans Railway dashboard

### Frontend (Vercel)
- Déploiement automatique sur push vers `main`
- Variables d'environnement dans Vercel dashboard

---

## Documentation

### Documentation Technique

La documentation technique complète est organisée dans le dossier `docs/` :

- **[docs/README.md](docs/README.md)** - Index et guide de la documentation technique
- **[docs/architecture.md](docs/architecture.md)** - Architecture complète, vision produit, roadmap
- **[docs/backend.md](docs/backend.md)** - Modules backend, endpoints, services, roadmap
- **[docs/database.md](docs/database.md)** - Analyse schéma base de données
- **[docs/frontend.md](docs/frontend.md)** - État des lieux frontend, pages implémentées
- **[docs/api-reference.md](docs/api-reference.md)** - Référence API, endpoints, schémas
- **[docs/oauth-scopes.md](docs/oauth-scopes.md)** - Permissions OAuth Meta/Facebook et TikTok
- **[docs/post-app-review-roadmap.md](docs/post-app-review-roadmap.md)** - Roadmap post-App Review (Meilisearch advanced, Supabase+pgvector, Make/n8n, Dust)

### Références Rapides

- **[DATA.md](DATA.md)** - Schéma base de données (vue d'ensemble rapide)
- **[SCOPES.md](SCOPES.md)** - Liste des scopes OAuth (référence)

### Documentation Web

- **[Documentation en ligne](https://www.veyl.io/docs)** - Documentation accessible depuis l'interface web

---

## Roadmap

### ✅ Phase 1: Foundations (Terminé)
- Modèles Projects en base de données
- Endpoints Projects CRUD (GET, POST, PUT, DELETE)
- Interface My Projects avec layout amélioré
- Onboarding avec tags inline et autocomplétion
- ProjectPanel réutilisable
- Onglets Watchlist, Grille, Analytics
- Dialog Instagram-style pour posts

### 🔄 Phase 2: Recherche & IA (À venir)
- Qdrant (recherche vectorielle)
- Clustering IA
- Service embeddings
- Investigate Mode

### 📅 Phase 3: Workers & Agents (À venir)
- Celery workers
- Agents backend (Scout, Scribe, Planner)
- Génération Weekly Digest

### 📅 Phase 4: Features Avancées (À venir)
- Multi-tenant (organisations)
- Vertex AI (analyse vidéo, on-demand)
- Gamma/Pomelli export
- Feature flags système

---

## Compte de Test

Pour créer un utilisateur de test, utiliser le script backend:
```bash
cd apps/backend
python scripts/create_test_user.py
```

---

## Meilisearch - Moteur de Recherche

**Meilisearch** est le moteur de recherche central de veyl.io. Il permet une recherche ultra-rapide et typo-tolerant sur des millions de posts.

### Avantages
- **Typo-tolerance** : Trouve les résultats même avec des fautes de frappe
- **Performance** : Recherche en millisecondes
- **Facettes** : Filtrage avancé par plateforme, date, hashtags
- **Configuration simple** : Index automatique, mise à jour en temps réel

**Documentation**: [Meilisearch](https://www.meilisearch.com/docs)

---

## Communauté Open Source

**veyl.io** est entièrement **open source** et développé en collaboration avec :

- **ISCOM Paris** - Analyse des tendances marketing et communication
- **EPITECH Paris** - Développement technique, architecture backend

### Liens Communauté
- **GitHub Repository**: [https://github.com/RomeoCavazza/veyl.io](https://github.com/RomeoCavazza/veyl.io)
- **Discord Community**: [https://discord.gg/TKbNuuV4sX](https://discord.gg/TKbNuuV4sX)

### Contribution

1. Fork le repository sur GitHub
2. Créer une branche depuis `main`
3. Développer et tester localement
4. Push et créer une Pull Request

Les contributions sont les bienvenues ! Consultez les issues GitHub pour voir comment vous pouvez aider.

---

## License

Proprietary - Tous droits réservés

---

## Partenariats Officiels

**veyl.io** est partenaire officiel des programmes **Meta for Developers** et **TikTok for Developers**.

### Meta for Developers
- **Instagram Graph API** - Accès aux contenus publics Instagram Business
- **Facebook Pages API** - Gestion des pages et insights
- **Documentation**: [Meta for Developers](https://developers.facebook.com/)

### TikTok for Developers
- **TikTok Login Kit** - Authentification OAuth
- **TikTok API** - Accès aux vidéos publiques et statistiques créateurs
- **Documentation**: [TikTok for Developers](https://developers.tiktok.com/)

---

## App Review Mode

Pour la validation **Meta App Review** et **TikTok App Review**, l'application fonctionne en **mode démonstration** via des datasets mock/fake (posts, creators, insights) afin d'afficher le fonctionnement complet du flux utilisateur (OAuth → création projet → visualisation → analytics).

Les reviewers évaluent la **compréhension du flux** et la conformité aux politiques, pas nécessairement des données réelles. Les données réelles seront activées automatiquement dès l'obtention de l'accès Public Content.

### Permissions Meta/Facebook Demandées

- `instagram_business_basic` - Accès basique Instagram Business
- `instagram_manage_insights` - Gestion des insights Instagram
- `pages_read_engagement` - Lecture métriques d'engagement
- `Page Public Content Access` - Accès contenu public (Advanced Access)
- `Instagram Public Content Access` - Accès contenu public Instagram (Advanced Access)
- `Meta oEmbed Read` - Lecture données oEmbed pour embeds

**Documentation**: [Meta for Developers - App Review](https://developers.facebook.com/docs/app-review)

### Permissions TikTok Demandées

- `user.info.basic` - Informations utilisateur basiques
- `user.info.profile` - Informations profil utilisateur
- `user.info.stats` - Statistiques utilisateur
- `video.list` - Liste des vidéos publiques

**Documentation**: [TikTok for Developers - App Review](https://developers.tiktok.com/doc/app-review)

### Pages Légales

- `/privacy` - Politique de confidentialité
- `/terms` - Conditions d'utilisation
- `/data-deletion` - Formulaire de suppression de données

**Conformité**: Toutes les pages légales sont complètes et accessibles publiquement pour satisfaire aux exigences des plateformes.

---

**Pour plus de détails**: Voir [docs/architecture.md](docs/architecture.md) ou [Documentation en ligne](https://www.veyl.io/docs)
