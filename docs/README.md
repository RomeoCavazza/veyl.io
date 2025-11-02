# Documentation Technique - veyl.io

**Dernière mise à jour**: 02 novembre 2025

## 📚 Vue d'ensemble

Cette documentation technique couvre l'architecture, l'implémentation et la roadmap de **veyl.io**, plateforme de veille culturelle et d'analyse des tendances sur les réseaux sociaux.

**veyl.io** est développé en collaboration avec les étudiants de **ISCOM Paris** et **EPITECH Paris**, et est entièrement **open source** sur GitHub.

## 📖 Structure de la Documentation

### 🏗️ Architecture & Design
- **[architecture.md](./architecture.md)** - Architecture complète, stack technique, vision produit, roadmap
- **[database.md](./database.md)** - Schéma base de données PostgreSQL, relations, exemples de requêtes

### 💻 Développement
- **[frontend.md](./frontend.md)** - Structure frontend React, pages, composants, routing, intégration API
- **[backend.md](./backend.md)** - Modules FastAPI, endpoints, services, configuration, plan d'action

### 🔌 Références Techniques
- **[api-reference.md](./api-reference.md)** - Endpoints API, schémas de données, contrats techniques
- **[oauth-scopes.md](./oauth-scopes.md)** - Permissions OAuth Meta/Facebook et TikTok

## 🚀 Démarrage Rapide

Pour commencer rapidement, consultez le **[README.md principal](../README.md)** qui contient :
- Installation et configuration
- Stack technique
- Démarrage local (backend et frontend)
- Variables d'environnement

## 🎯 État Actuel (02 novembre 2025)

### ✅ Fonctionnalités Opérationnelles
- **Backend FastAPI** avec authentification OAuth (Instagram, Facebook, Google, TikTok)
- **Système Projects** complet (CRUD, hashtags, créateurs)
- **Frontend React** avec pages fonctionnelles (Projects, Analytics, Search, Community, Enterprise)
- **Base de données PostgreSQL** avec modèles normalisés
- **Recherche full-text** via **Meilisearch** (ultra-rapide, typo-tolerant)
- **Rate limiting** via Redis
- **Partenariats officiels** : Meta for Developers et TikTok for Developers

### 🔄 En Développement
- Optimisations UI/UX basées sur retours utilisateurs
- Améliorations de performance et scalabilité

### 📅 Roadmap (Phases Futures)
- **Phase 2**: Recherche vectorielle (Qdrant), clustering IA
- **Phase 3**: Workers asynchrones (Celery), agents backend
- **Phase 4**: Multi-tenant, features avancées (Vertex AI, exports)

## 🔗 Liens Utiles

- **Documentation en ligne**: [https://www.veyl.io/docs](https://www.veyl.io/docs)
- **GitHub Repository** (Open Source): [https://github.com/RomeoCavazza/veyl.io](https://github.com/RomeoCavazza/veyl.io)
- **Discord Community**: [https://discord.gg/TKbNuuV4sX](https://discord.gg/TKbNuuV4sX)
- **API Docs (Swagger)**: Disponible sur `/docs` en local (`http://localhost:8000/docs`)

## 🤝 Partenariats & Communauté

### Partenaires Officiels
- **Meta for Developers** - Partenaire Instagram Graph API et Facebook Pages API
- **TikTok for Developers** - Partenaire TikTok Login Kit et TikTok API

### Communauté Open Source
- **GitHub**: Repository public et collaboratif
- **Discord**: Serveur communautaire pour échanges et support
- **Partenariats académiques**: 
  - **ISCOM Paris** - Développement et analyse des tendances marketing
  - **EPITECH Paris** - Développement technique, architecture backend

## 📝 Notes Importantes

- La documentation est maintenue à jour avec l'évolution du code
- Les dates de mise à jour sont indiquées en haut de chaque fichier
- Les sections "À implémenter" représentent la roadmap future, pas des lacunes actuelles
- **Meilisearch** est le moteur de recherche central pour la recherche full-text ultra-rapide et typo-tolerant
- L'application est soumise aux processus d'App Review de Meta et TikTok pour l'accès aux contenus publics

---

**Pour commencer**: Consultez [architecture.md](./architecture.md) pour une vue d'ensemble complète.
