# Frontend Status - veyl.io

**Dernière mise à jour**: 02 novembre 2025  
**Objectif**: État des lieux frontend, pages implémentées, routing, composants

---

## Structure Actuelle

```
apps/frontend/src/
├── components/
│   ├── ui/              Composants Radix UI complets (shadcn/ui)
│   ├── Navbar.tsx       Navigation principale
│   ├── ProtectedRoute.tsx Auth guard
│   ├── AISearchBar.tsx  Barre de recherche
│   └── ProjectPanel.tsx Panneau projet réutilisable
├── contexts/
│   ├── AuthContext.tsx  Gestion authentification
│   └── WatchlistContext.tsx Watchlist state
├── pages/
│   ├── Landing.tsx      Page d'accueil
│   ├── Auth.tsx         Login/Register
│   ├── Search.tsx       Recherche posts
│   ├── Analytics.tsx     Analytics dashboard global
│   ├── Profile.tsx      Profil utilisateur + OAuth
│   ├── Projects.tsx     My Projects (liste)
│   ├── ProjectsNew.tsx  Création projet (tags inline)
│   ├── ProjectDetail.tsx Détails projet (Watchlist/Grille/Analytics)
│   ├── CreatorDetail.tsx Détails créateur (Feed/Grid/Analytics)
│   └── Community.tsx    Community Hub
└── lib/
    ├── api.ts           Client API (auth, search, projects)
    ├── fakeData.ts      Datasets mock pour développement/App Review
    ├── mockData.ts      Données de test
    └── utils.ts         Utilitaires
```

---

## Routing (App.tsx)

### Routes Publiques
- `/` → Landing
- `/auth` → Auth (login/register)
- `/auth/callback` → AuthCallback (OAuth)
- `/docs` → Documentation
- `/enterprise` → Enterprise
- `/privacy`, `/terms`, `/data-deletion` → Pages légales

### Routes Protégées
- `/search` → Search posts
- `/projects` → My Projects (liste)
- `/projects/new` → Onboarding (création projet)
- `/projects/:id` → Project Detail (Watchlist/Grille/Analytics tabs)
- `/projects/:id/creator/:username` → Creator Detail (Feed/Grid/Analytics tabs)
- `/community` → Community Hub
- `/analytics` → Analytics (global)
- `/profile` → User Profile + OAuth accounts

---

## Pages Projects (Implémentées)

### `/projects` - My Projects

**Fonctionnalités**:
- Liste projets utilisateur avec statut
- Bouton "New project"
- Empty state si aucun projet
- Badge status (active, draft, archived)

**Layout**:
- Cards pleine largeur
- Bloc gauche (`w-80`): nom, date, status, description, photos créateurs (3 premiers en cascade)
- Bloc droit (`flex-1`): posts récents (10 max) en ligne horizontale scrollable
- Date alignée horizontalement avec nom et status
- Compteur créateurs affiché (total, mais 3 visibles visuellement)
- Clic sur card pour accéder au projet

### `/projects/new` - Onboarding

**Formulaire**:
- Champs: name, description (optionnel), platforms (default: Instagram)

**Input Hashtags**:
- Tags affichés directement dans l'input (inline)
- Autocomplétion avec suggestions en temps réel
- Croix de suppression sur chaque tag
- Support Backspace pour supprimer le dernier tag
- Pas de bouton "+" (ajout via Enter ou clic suggestion)

**Input Créateurs**:
- Tags affichés directement dans l'input (inline)
- Photos de profil dans les suggestions et badges (dicebear avatars)
- Autocomplétion avec suggestions en temps réel
- Croix de suppression sur chaque tag
- Support Backspace pour supprimer le dernier tag
- Pas de bouton "+" (ajout via Enter ou clic suggestion)

**Validation**: Au moins 1 hashtag OU 1 créateur requis

### `/projects/:id` - Project Detail

**ProjectPanel** (réutilisable en haut de chaque onglet):
- Nom, description, status, plateformes (avec logos Instagram/TikTok)
- Métriques (Créateurs, Posts, Signals) avec indicateurs de tendance style crypto (+/-, vert/rouge/gris)
- Menu dropdown pour modifier, dupliquer, supprimer

**Onglet Watchlist**:
- Layout 50/50: ProjectPanel (gauche) + Liste créateurs (droite)
- Liste créateurs: photos profil, followers, posts (filtre Jour/Semaine/Mois avec Select)
- Feed posts: photos créateurs, dialog Instagram-style au clic
- Dialog post: photo gauche (60%), infos droite (40%) avec description, stats, commentaires

**Onglet Grille**:
- Tableau triable des posts (pas de pagination pour l'instant)
- Colonnes: Image, Auteur, Description, Date, Likes, Comments, Score, Platform
- Tri par colonne (cliquable sur header)

**Onglet Analytics**:
- Layout 50/50: ProjectPanel (gauche) + Graphique Content Type Distribution (droite)
- Charts: Engagement Trends (AreaChart), Top Performing Creators (BarChart), Reach & Impressions (AreaChart)

### `/projects/:id/creator/:username` - Creator Detail

**Panneau Info Créateur**:
- Photo profil gauche, infos droite
- Nom, pseudo, description
- Stats regroupées sous description (grid 3x2): Followers, Following, Posts, Avg Engagement, Total Likes, Total Comments
- Badges: platform, verified, category

**Onglet Feed**:
- Grille de posts (3 colonnes)
- Dialog Instagram-style au clic

**Onglet Grid**:
- Tableau triable des posts (format identique à ProjectDetail Grille)

**Onglet Analytics**:
- Stats numériques regroupées dans un seul bloc (grid 4 colonnes)
- 4 graphiques en layout 2x2: Engagement Trends, Post Performance, Likes Over Time, Comments Over Time

---

## Composants UI

### Radix UI + shadcn/ui
- `Card`, `CardHeader`, `CardTitle`, `CardContent`
- `Button`, `Input`, `Label`
- `Badge`, `Tabs`, `Table`, `Select`, `Dialog`
- `DropdownMenu`, `Toast` (sonner)

### Icons (lucide-react)
- Navigation: `FileText`, `ArrowLeft`, `Settings`
- Actions: `Edit`, `Trash2`, `Plus`, `X`
- Métriques: `Heart`, `MessageCircle`, `Eye`
- Tendances: `TrendingUp`, `TrendingDown`, `Minus`
- Tri: `ArrowUpDown`, `ArrowUp`, `ArrowDown`
- Plateformes: `Instagram`, `Video`, `Music`

### Graphiques (recharts)
- `ResponsiveContainer`, `AreaChart`, `Area`, `BarChart`, `Bar`, `PieChart`, `Pie`
- `XAxis`, `YAxis`, `CartesianGrid`, `Tooltip`, `Legend`, `Cell`

---

## Design System

- **Tailwind CSS** - Framework CSS utility-first
- **Radix UI + shadcn/ui** - Composants UI accessibles (headless)
- **Theme**: Dark mode par défaut, variables CSS personnalisées
- **Recharts** - Bibliothèque de graphiques
- **date-fns** - Manipulation de dates et formatage relatif

---

## État d'Implémentation

| Page | Statut | Fonctionnalités |
|------|--------|----------------|
| Landing | ✅ | CTA "Start a demo" → `/projects/new` |
| Search | ✅ | Recherche posts Meilisearch (ultra-rapide, typo-tolerant), images avec fallback, layout compact |
| Projects | ✅ | Liste améliorée (photos cascade, posts récents) |
| ProjectsNew | ✅ | Tags inline, autocomplétion, photos profil |
| ProjectDetail | ✅ | 3 tabs (Watchlist/Grille/Analytics), ProjectPanel, dialog Instagram-style |
| CreatorDetail | ✅ | 3 tabs (Feed/Grid/Analytics), stats regroupées, dialog post |
| Community | ✅ | Widgets GitHub et Discord, sections écoles ISCOM/EPITECH, contribution open source |
| Enterprise | ✅ | Section contact, recherche beta testeurs, avantages entreprise |
| Landing | ✅ | Badges partenariats Meta/TikTok, section Meilisearch, stack technique, intégrations |
| Analytics | ✅ | Dashboard global avec graphiques |
| Profile | ✅ | OAuth accounts management |

---

## Intégration Backend

### API Client (`lib/api.ts`)

**Fonctions implémentées**:
- ✅ `createProject()` - Créer projet
- ✅ `getProjects()` - Liste projets
- ✅ `getProject(id)` - Détails projet
- ✅ `updateProject(id)` - Mettre à jour projet
- ✅ `deleteProject(id)` - Supprimer projet
- ✅ `searchPosts()` - Recherche posts

**Configuration**:
- `getApiBase()` - Détermine base URL (Vercel proxy ou Railway direct)
- Support `VITE_API_URL` pour développement

### Données Mock (`lib/fakeData.ts`)

**Pour App Review**:
- ✅ `getFakeProject(id)` - Projet mock
- ✅ `getFakeProjectPosts(projectId)` - Posts mock
- ✅ `fakeCreators`, `fakePosts` - Données de test

**Note**: Frontend utilise données réelles via API, fallback sur fake data en développement.

---

## Roadmap Frontend (Phases Futures)

### Phase 2: Investigate Mode
- Recherche avancée dans projet
- Multi-select posts/créateurs
- "Add to Project" batch

### Phase 3: Clustering IA
- Bouton "Cluster with AI" (requiert Qdrant backend)
- Groupement automatique en niches
- Édition manuelle niches

### Phase 4: Reports & Export
- Liste rapports générés
- Weekly Digest viewer
- Export slides (Gamma/Pomelli) - flag Pro+

---

---

## Pages Publiques (Refonte Complète)

### `/` - Landing Page
- Badges partenariats Meta/TikTok
- Section **Meilisearch** mise en avant
- Stack technique avec badges
- Sections intégrations social media
- CTA vers Community et Projects

### `/community` - Communauté Open Source
- Widget **GitHub** (card style)
- Widget **Discord** (bouton stylisé)
- Sections écoles **ISCOM Paris** et **EPITECH Paris**
- Section contribution et collaboration

### `/enterprise` - Solutions Entreprise
- Section contact avec formulaire
- Recherche **beta testeurs** (agences)
- Avantages entreprise
- Features sur mesure

### `/docs` - Documentation
- Sections partenariats Meta/TikTok
- Section **Meilisearch** détaillée
- Section communauté GitHub/Discord
- Sections écoles académiques

### Pages Légales
- `/privacy` - Politique de confidentialité (RGPD/CCPA)
- `/terms` - Conditions d'utilisation
- `/data-deletion` - Suppression de données (conformité Meta/TikTok)

---

## Technologies & Intégrations

### Meilisearch
Le frontend utilise **Meilisearch** via l'endpoint `/api/v1/posts/search` pour une recherche ultra-rapide et typo-tolerant.

**Avantages**:
- Recherche instantanée en millisecondes
- Typo-tolerance automatique
- Facettes et filtres avancés
- Résultats pertinents

### Partenariats
- **Meta for Developers**: Intégration Instagram Graph API et Facebook Pages API
- **TikTok for Developers**: Intégration TikTok Login Kit et TikTok API

---

**Référence**: [architecture.md](./architecture.md) pour roadmap complète, [api-reference.md](./api-reference.md) pour endpoints API.
