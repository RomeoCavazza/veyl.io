# Database Schema - veyl.io

**Dernière mise à jour**: 02 novembre 2025  
**Objectif**: Analyse schéma base de données, tables existantes, réutilisation pour Projects

---

## Inventaire des Tables

### Tables Core Existantes (7 tables)

| Table | Colonnes Clés | Utilité pour Projects |
|-------|---------------|----------------------|
| `users` | `id`, `email`, `name` | Clé étrangère `projects.user_id` |
| `oauth_accounts` | `user_id`, `provider`, `access_token` | Indirect (via users) |
| `platforms` | `id`, `name` | Référence pour plateformes |
| `hashtags` | `id`, `name`, `platform_id`, `last_scraped` | **Réutilisable directement** |
| `posts` | `id`, `platform_id`, `author`, `caption`, `hashtags`, `metrics` | **Réutilisable** |
| `post_hashtags` | `post_id`, `hashtag_id` | Relation posts ↔ hashtags |
| `subscriptions` | `user_id`, `plan`, `quota` | Non lié à projects |

### Tables Projects (3 tables - nouveau)

| Table | Colonnes Clés | Utilité |
|-------|---------------|---------|
| `projects` | `id`, `user_id`, `name`, `description`, `status`, `platforms`, `scope_type`, `creators_count`, `posts_count`, `signals_count` | Projets de monitoring |
| `project_hashtags` | `project_id`, `hashtag_id`, `added_at` | Relation projets ↔ hashtags |
| `project_creators` | `project_id`, `creator_username`, `platform_id`, `added_at` | Créateurs suivis par projet |

### Views Matérialisées (2 views)

| View | Colonnes | Utilité |
|------|----------|---------|
| `hashtags_with_stats` | `id`, `name`, `platform`, `total_posts`, `avg_engagement` | Statistiques agrégées pour Projects |
| `posts_with_platform` | Posts + informations plateforme | Vue enrichie posts |

---

## Analyse de Réutilisation

### Table `hashtags` - Réutilisable Directement

**Structure actuelle**:
```python
Hashtag:
  - id (Integer, PK)
  - name (String, unique)
  - platform_id (FK → platforms)
  - last_scraped (DateTime)
  - updated_at (DateTime)
```

**Avantages pour Projects**:
- Table déjà normalisée avec identifiants
- Pas de duplication de données
- Statistiques disponibles via `hashtags_with_stats`
- Relations existantes via `post_hashtags`

**Implémentation**: Table de liaison `project_hashtags` créée pour relier projets et hashtags existants.

---

### Table `posts` - Réutilisable Directement

**Structure actuelle**:
```python
Post:
  - id (Text, PK) - e.g. "instagram_123456"
  - platform_id (FK → platforms)
  - author (String) - username créateur
  - caption (Text)
  - hashtags (Array) - liste hashtags dans le post
  - metrics (JSON) - likes, comments, shares, views
  - posted_at (DateTime)
  - sentiment (Float)
  - score (Float), score_trend (Float)
```

**Pour Projects**:
- Requêtes posts via `project_hashtags` + `post_hashtags`
- Requêtes posts via `project_creators` + `posts.author`

---

## Schéma Projects (Implémenté)

### Architecture: Tables de Liaison

```python
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default='draft')
    
    platforms = Column(Text)  # JSON: ["instagram", "tiktok"]
    scope_type = Column(String(50))  # 'hashtags', 'creators', 'both'
    scope_query = Column(Text)
    
    creators_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    signals_count = Column(Integer, default=0)
    
    last_run_at = Column(DateTime)
    last_signal_at = Column(DateTime)
    
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

class ProjectHashtag(Base):
    __tablename__ = "project_hashtags"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    hashtag_id = Column(Integer, ForeignKey("hashtags.id", ondelete="CASCADE"), nullable=False)
    added_at = Column(DateTime, default=dt.datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('project_id', 'hashtag_id', name='uq_project_hashtag'),
    )

class ProjectCreator(Base):
    __tablename__ = "project_creators"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    creator_username = Column(String(255), nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    added_at = Column(DateTime, default=dt.datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('project_id', 'platform_id', 'creator_username', name='uq_project_creator'),
    )
```

**Avantages**:
- Réutilisation de la table `hashtags` existante (évite duplication)
- Réutilisation de `posts` via `author` (pas besoin de `selected_posts`)
- Statistiques disponibles via `hashtags_with_stats` (pas de recalcul)
- Requêtes optimisées (JOIN, index)
- Architecture normalisée et maintenable

---

## Exemples de Requêtes

### Posts d'un projet (via hashtags)

```sql
SELECT p.* FROM posts p
JOIN post_hashtags ph ON p.id = ph.post_id
JOIN project_hashtags proj_h ON ph.hashtag_id = proj_h.hashtag_id
WHERE proj_h.project_id = ?;
```

### Posts d'un projet (via créateurs)

```sql
SELECT p.* FROM posts p
JOIN project_creators pc ON p.author = pc.creator_username
WHERE pc.project_id = ? AND p.platform_id = pc.platform_id;
```

### Statistiques hashtags d'un projet

```sql
SELECT * FROM hashtags_with_stats hws
JOIN project_hashtags ph ON hws.id = ph.hashtag_id
WHERE ph.project_id = ?;
```

---

## Schéma Final

```python
# Table principale (sans duplication)
Project:
  - id, user_id, name, description, status
  - platforms (JSON), scope_type, scope_query
  - creators_count, posts_count, signals_count (cache)
  - last_run_at, last_signal_at
  - created_at, updated_at

# Tables de liaison (réutilisent l'existant)
ProjectHashtag:
  - project_id → projects.id
  - hashtag_id → hashtags.id (réutilise hashtags existante)

ProjectCreator:
  - project_id → projects.id
  - creator_username, platform_id → platforms.id

# Requêtes:
# - Posts d'un projet = JOIN project_hashtags + post_hashtags + posts
# - Stats hashtags = JOIN project_hashtags + hashtags_with_stats
# - Posts créateurs = JOIN project_creators + posts (WHERE author = creator_username)
```

**Note**: Le schéma actuel est optimisé pour la réutilisation des données existantes et les performances à long terme.

---

**Référence**: Voir le code source dans `apps/backend/db/models.py` pour l'implémentation complète.
