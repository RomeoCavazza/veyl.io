# OAuth Scopes - veyl.io

**Dernière mise à jour**: 02 novembre 2025

## Vue d'ensemble

Cette documentation liste les permissions OAuth requises pour **Meta/Facebook** et **TikTok** afin d'accéder aux APIs publiques nécessaires au fonctionnement de veyl.io.

**Ressources**:
- [Meta for Developers](https://developers.facebook.com/)
- [TikTok for Developers](https://developers.tiktok.com/)

---

## Meta / Facebook Permissions

### Instagram Business

| Permission | Description | Usage |
|-----------|-------------|-------|
| `instagram_business_basic` | Accès basique Instagram Business | Lecture profil et médias |
| `instagram_manage_insights` | Gestion des insights Instagram Business | Accès aux métriques et insights |
| `instagram_business_manage_insights` | Gestion avancée insights | Insights pour comptes professionnels |

### Facebook Pages

| Permission | Description | Usage |
|-----------|-------------|-------|
| `pages_show_list` | Liste des pages gérées | Afficher pages Facebook connectées |
| `pages_read_user_content` | Lecture contenu utilisateur | Posts, commentaires, notes |
| `pages_read_engagement` | Lecture métriques d'engagement | Likes, followers, métriques de pages |
| `read_insights` | Lecture données Insights | Analytics pages, apps, domaines |

### Advanced Access Features

| Feature | Description | Usage | Review Status |
|---------|-------------|-------|---------------|
| `Page Public Content Access` | Accès contenu public des pages | Analyser posts et engagement sur pages publiques | ⏳ Advanced Access requis |
| `Page Public Metadata Access` | Accès métadonnées publiques | Voir likes, followers, infos publiques agrégées | ⏳ Advanced Access requis |
| `Instagram Public Content Access` | Accès contenu public Instagram | Endpoints Hashtag Search API | ⏳ Advanced Access requis |
| `Meta oEmbed Read` | Lecture données oEmbed | Embeds HTML pour posts Facebook/Instagram | ⏳ Advanced Access requis |

### Standard Permissions

| Permission | Description | Usage |
|-----------|-------------|-------|
| `public_profile` | Profil public utilisateur | Authentification et expérience personnalisée |

---

## TikTok Permissions

### Login Kit

| Permission | Description | Usage |
|-----------|-------------|-------|
| `user.info.basic` | Informations utilisateur basiques | open_id, avatar, display_name |
| `user.info.profile` | Informations profil utilisateur | profile_web_link, profile_deep_link, bio_description, is_verified |
| `user.info.stats` | Statistiques utilisateur | likes count, follower count, following count, video count |
| `video.list` | Liste vidéos publiques | Accès aux vidéos publiques TikTok |

**Documentation**: [TikTok Login Kit Docs](https://developers.tiktok.com/doc/login-kit-web)

---

## App Review Process

### Mode Démonstration

Pour la validation App Review Meta/TikTok, l'application fonctionne en **mode démonstration** avec des datasets mock/fake permettant d'afficher le fonctionnement complet du flux utilisateur (OAuth → création projet → visualisation → analytics).

**Justification**: Les reviewers évaluent la **compréhension du flux** et la conformité aux politiques, pas nécessairement des données réelles. L'ingestion réelle sera activée après obtention de l'accès Public Content.

**Statut**: ✅ Datasets fake disponibles dans `apps/frontend/src/lib/fakeData.ts`

### Conformité Requise

- ✅ Page `/privacy` - Politique de confidentialité complète
- ✅ Page `/terms` - Conditions d'utilisation complètes
- ✅ Page `/data-deletion` - Formulaire de suppression de données
- ✅ Endpoint `DELETE /api/v1/user/{id}` (à implémenter si requis)

---

## Notes Techniques

- Les permissions **Advanced Access** nécessitent une soumission App Review détaillée avec justification d'usage
- Les permissions standard peuvent être demandées via App Review basique
- TikTok Login Kit est inclus dans le produit "Login Kit" et nécessite une soumission App Review

---

---

## Partenariats Officiels

**veyl.io** est partenaire officiel des programmes **Meta for Developers** et **TikTok for Developers**.

### Meta for Developers
- Documentation: [Meta for Developers](https://developers.facebook.com/)
- App Review: [Meta App Review Process](https://developers.facebook.com/docs/app-review)

### TikTok for Developers
- Documentation: [TikTok for Developers](https://developers.tiktok.com/)
- App Review: [TikTok App Review](https://developers.tiktok.com/doc/app-review)

---

**Référence**: Voir le code source dans `apps/backend/auth_unified/` pour l'implémentation OAuth.
