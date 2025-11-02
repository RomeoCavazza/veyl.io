# API Reference - veyl.io

**Dernière mise à jour**: 02 novembre 2025

## Vue d'ensemble

Cette référence documente les endpoints API REST de veyl.io. L'API utilise FastAPI avec authentification JWT et OAuth.

**Base URL**: `/api/v1`  
**Authentification**: Bearer Token (JWT) pour la plupart des endpoints

---

## Endpoints Projects

### `GET /api/v1/projects`

Liste tous les projets de l'utilisateur authentifié.

**Authentification**: Requise (Bearer Token)

**Réponse**:
```json
[
  {
    "id": 1,
    "user_id": 7,
    "name": "Fashion Trends 2025",
    "description": "Suivi des tendances mode",
    "status": "active",
    "platforms": ["instagram"],
    "scope_type": "both",
    "scope_query": "#fashion, @creator1",
    "creators_count": 5,
    "posts_count": 1247,
    "signals_count": 12,
    "last_run_at": "2025-11-01T10:30:00",
    "last_signal_at": "2025-11-01T14:22:00",
    "created_at": "2025-10-28T09:15:00",
    "updated_at": "2025-11-01T14:22:00"
  }
]
```

---

### `POST /api/v1/projects`

Crée un nouveau projet avec hashtags et/ou créateurs.

**Authentification**: Requise (Bearer Token)

**Body**:
```json
{
  "name": "Fashion Trends 2025",
  "description": "Suivi des tendances mode",
  "platforms": ["instagram"],
  "scope_type": "both",
  "scope_query": "#fashion, @creator1",
  "hashtag_names": ["fashion", "style"],
  "creator_usernames": ["creator1", "creator2"]
}
```

**Champs**:
- `name` (required): Nom du projet
- `description` (optional): Description du projet
- `platforms` (required): Liste des plateformes (`["instagram"]`, `["tiktok"]`, `["instagram", "tiktok"]`)
- `scope_type` (required): Type de scope (`"hashtags"`, `"creators"`, `"both"`)
- `scope_query` (required): Chaîne de requête (hashtags et créateurs séparés par virgule)
- `hashtag_names` (optional): Liste des noms de hashtags (sans #)
- `creator_usernames` (optional): Liste des usernames créateurs (sans @)

**Réponse**: 201 Created avec l'objet projet créé (format identique à GET)

---

### `GET /api/v1/projects/{id}`

Récupère les détails d'un projet spécifique, incluant les relations (hashtags et créateurs).

**Authentification**: Requise (Bearer Token)

**Réponse**:
```json
{
  "id": 1,
  "user_id": 7,
  "name": "Fashion Trends 2025",
  "description": "Suivi des tendances mode",
  "status": "active",
  "platforms": ["instagram"],
  "scope_type": "both",
  "scope_query": "#fashion, @creator1",
  "creators_count": 5,
  "posts_count": 1247,
  "signals_count": 12,
  "hashtags": [
    {"id": 1, "name": "fashion", "platform_id": 1}
  ],
  "creators": [
    {"id": 1, "creator_username": "creator1", "platform_id": 1}
  ],
  "last_run_at": "2025-11-01T10:30:00",
  "last_signal_at": "2025-11-01T14:22:00",
  "created_at": "2025-10-28T09:15:00",
  "updated_at": "2025-11-01T14:22:00"
}
```

---

### `PUT /api/v1/projects/{id}`

Met à jour un projet existant.

**Authentification**: Requise (Bearer Token)

**Body** (tous les champs optionnels, seuls ceux fournis sont mis à jour):
```json
{
  "name": "Fashion Trends 2025 - Updated",
  "description": "Nouvelle description",
  "status": "archived",
  "platforms": ["instagram", "tiktok"],
  "hashtag_names": ["fashion", "style", "ootd"],
  "creator_usernames": ["creator1", "creator2", "creator3"]
}
```

**Réponse**: 200 OK avec l'objet projet mis à jour

---

### `DELETE /api/v1/projects/{id}`

Supprime un projet et toutes ses relations (hashtags, créateurs via CASCADE).

**Authentification**: Requise (Bearer Token)

**Réponse**: 204 No Content

---

## Endpoints Authentification

### `POST /api/v1/auth/register`

Inscription d'un nouvel utilisateur.

**Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

**Réponse**: 201 Created avec token JWT

---

### `POST /api/v1/auth/login`

Connexion utilisateur.

**Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Réponse**: 200 OK avec token JWT

---

### `GET /api/v1/auth/me`

Récupère le profil de l'utilisateur authentifié.

**Authentification**: Requise (Bearer Token)

**Réponse**:
```json
{
  "id": 7,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "created_at": "2025-10-28T09:15:00",
  "is_active": true
}
```

---

### `GET /api/v1/auth/{provider}/start`

Initie le flux OAuth pour un provider (instagram, facebook, google, tiktok).

**Réponse**: 302 Redirect vers le provider OAuth

---

### `GET /api/v1/auth/{provider}/callback`

Callback OAuth après authentification sur le provider.

**Query Parameters**:
- `code`: Code d'autorisation fourni par le provider
- `state`: State token pour sécurité

**Réponse**: 302 Redirect vers frontend avec token

---

## Endpoints Recherche

### `GET /api/v1/posts/search`

Recherche de posts via **Meilisearch** (moteur de recherche ultra-rapide et typo-tolerant).

**Query Parameters**:
- `q` (required): Terme de recherche
- `platform` (optional): Filtrer par plateforme
- `limit` (optional): Nombre de résultats (défaut: 12)
- `sort` (optional): Critère de tri (`score_trend:desc`, `posted_at:desc`)

**Réponse**:
```json
{
  "hits": [
    {
      "id": "instagram_123456",
      "platform_id": 1,
      "author": "creator1",
      "caption": "Post caption...",
      "hashtags": ["fashion", "style"],
      "metrics": {"likes": 15000, "comments": 450},
      "posted_at": "2025-11-01T10:30:00",
      "media_url": "https://...",
      "score": 8.5,
      "score_trend": 0.12
    }
  ],
  "total": 1247
}
```

---

## Health Checks

### `GET /ping`

Health check simple.

**Réponse**: 200 OK avec `{"status": "ok"}`

---

### `GET /healthz`

Health check détaillé (base de données, services).

**Réponse**: 200 OK avec statut des services

---

## Codes d'Erreur

| Code | Signification |
|------|---------------|
| 400 | Bad Request - Données invalides |
| 401 | Unauthorized - Token manquant/invalide |
| 403 | Forbidden - Accès non autorisé |
| 404 | Not Found - Ressource introuvable |
| 422 | Unprocessable Entity - Erreur de validation |
| 500 | Internal Server Error - Erreur serveur |

---

## Notes Techniques

### Configuration FastAPI

L'API utilise `redirect_slashes=False` dans `app.py` pour éviter les redirections 307 lors du proxy Vercel. Les routes utilisent des chaînes vides (`""`) au lieu de `"/"` pour correspondre exactement aux URLs sans slash final.

### Format des Dates

Toutes les dates sont retournées au format ISO 8601 (`YYYY-MM-DDTHH:mm:ss`).

### Relations Projects

Les hashtags et créateurs sont liés via tables de liaison (`project_hashtags`, `project_creators`) qui réutilisent les tables existantes (`hashtags`, `platforms`) pour éviter la duplication.

---

## Meilisearch - Moteur de Recherche

**Meilisearch** est le moteur de recherche utilisé par l'endpoint `/api/v1/posts/search`. Il offre une recherche ultra-rapide et typo-tolerant sur des millions de posts.

### Caractéristiques
- **Typo-tolerance** : Trouve les résultats même avec des fautes de frappe
- **Performance** : Recherche en millisecondes
- **Facettes** : Filtrage avancé par plateforme, date, hashtags
- **Index automatique** : Mise à jour en temps réel

### Configuration Backend
- Service client: `apps/backend/services/meilisearch_client.py`
- Index: `posts` avec champs indexés (caption, hashtags, author, platform_id, posted_at)
- Variables d'environnement: `MEILI_HOST`, `MEILI_MASTER_KEY`

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

**Référence complète des permissions**: Voir [oauth-scopes.md](./oauth-scopes.md)

---

**Référence complète**: Voir [Swagger UI](http://localhost:8000/docs) en local ou [architecture.md](./architecture.md) pour plus de détails.
