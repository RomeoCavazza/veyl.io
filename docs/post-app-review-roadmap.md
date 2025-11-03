# Roadmap Post-App Review - veyl.io

**Dernière mise à jour**: 02 novembre 2025  
**Phase**: Post-App Review (Phase 2)

---

## Contexte

Après la validation **App Review** (Meta et TikTok), la plateforme entrera dans une phase d'amélioration et d'optimisation des fonctionnalités existantes, avec un focus sur :

1. **Expérience utilisateur de recherche** améliorée
2. **Recherche sémantique et RAG** (Retrieval-Augmented Generation)
3. **Ingestion automatisée** des données
4. **Agent reasoning** avancé si nécessaire

---

## Stack Technique Post-App Review

### 1. Meilisearch - Recherche UX Avancée

**Objectif**: Améliorer l'expérience de recherche avec des filtres avancés et des règles de ranking personnalisées.

**Fonctionnalités**:
- **Filtres avancés**: Multi-critères (plateforme, date, engagement, type de contenu)
- **Ranking rules personnalisées**: Priorisation selon contexte (ex: engagement rate, trending, récent)
- **Facettes dynamiques**: Navigation par catégories (hashtags, créateurs, dates)
- **Suggestions intelligentes**: Autocomplétion contextuelle
- **Recherche typo-tolerant étendue**: Gestion des variantes de hashtags/créateurs

**Intégration**:
- Étendre les index Meilisearch existants avec nouveaux attributs
- Implémenter des filtres avancés dans l'interface de recherche
- Configurer des ranking rules selon les use cases (trending, engagement, recency)

---

### 2. Supabase + pgvector - Stockage Sémantique & RAG

**Objectif**: Ajouter la recherche sémantique et le RAG (Retrieval-Augmented Generation) pour une compréhension contextuelle du contenu.

**Technologies**:
- **Supabase**: PostgreSQL hébergé avec extensions vectorielles
- **pgvector**: Extension PostgreSQL pour stocker et rechercher des embeddings vectoriels

**Fonctionnalités**:
- **Embeddings vectoriels**: Génération d'embeddings pour posts, hashtags, créateurs
  - Modèle: OpenAI `text-embedding-3-small` ou équivalent open-source
- **Recherche par similarité**: Similarity search via pgvector (cosine distance)
- **RAG (Retrieval-Augmented Generation)**:
  - Recherche contextuelle dans la base de données
  - Génération de réponses basées sur le contenu récupéré
  - Applications: Analyse de tendances, résumés automatiques, insights
- **Hybrid search**: Combinaison recherche textuelle (Meilisearch) + recherche sémantique (pgvector)

**Architecture**:
```
PostgreSQL (Supabase)
├── Tables existantes (posts, hashtags, creators, projects)
└── Colonnes vectorielles (pgvector)
    ├── post_embedding (vector(1536))
    ├── hashtag_embedding (vector(1536))
    └── creator_embedding (vector(1536))
```

**Use Cases**:
- Recherche sémantique: "Trouve des posts similaires à celui-ci"
- Clustering automatique: Regroupement de posts par similarité sémantique
- Lookalikes: Trouver des créateurs similaires à un créateur de référence
- Analyse de tendances: Identifier des patterns sémantiques dans le contenu

**Migration**:
- Migrer PostgreSQL vers Supabase (ou ajouter pgvector à PostgreSQL Railway)
- Générer embeddings pour contenu existant (batch job)
- Créer index vectoriel (IVFFlat ou HNSW)

---

### 3. Make / n8n - Ingestion Automatisée

**Objectif**: Automatiser l'ingestion de données depuis Instagram et TikTok via workflows visuels.

**Technologies**:
- **Make (Integromat)**: Plateforme d'automatisation no-code/low-code
- **n8n**: Alternative open-source à Make

**Workflows**:
1. **Ingestion Instagram**:
   - Webhook → Make/n8n → Instagram Graph API → FastAPI → PostgreSQL
   - Déclenchement: Nouveaux posts détectés, nouvelles pages suivies
   
2. **Ingestion TikTok**:
   - Webhook → Make/n8n → TikTok API → FastAPI → PostgreSQL
   - Déclenchement: Nouveaux posts détectés, nouveaux créateurs suivis

3. **Traitement de données**:
   - Extraction métriques (engagement, reach)
   - Génération embeddings (via API embeddings)
   - Indexation Meilisearch
   - Mise à jour projets et analytics

**Avantages**:
- **Séparation des préoccupations**: Ingestion déléguée à Make/n8n
- **Flexibilité**: Modifications de workflows sans déploiement backend
- **Monitoring**: Visibilité sur les workflows via UI Make/n8n
- **Scaling**: Gestion automatique des rate limits

**Intégration Backend**:
- FastAPI endpoints dédiés pour recevoir les données de Make/n8n
- Webhooks pour notifications en temps réel
- Queue system pour traitement asynchrone (si nécessaire)

---

### 4. Dust - Agent Internal Reasoning

**Objectif**: Ajouter un système de raisonnement interne pour les agents si nécessaire (analyse complexe, décisions stratégiques).

**Technologie**:
- **Dust**: Plateforme pour construire des agents AI avec raisonnement structuré

**Use Cases Potentiels**:
- **Analyse de tendances complexes**: Raisonnement multi-étapes pour identifier patterns
- **Recommandations stratégiques**: Agents qui analysent données et suggèrent actions
- **Génération de rapports intelligents**: Agents qui synthétisent informations multiples
- **Détection d'anomalies**: Raisonnement pour identifier comportements atypiques

**Intégration**:
- API Dust pour déclencher agents depuis FastAPI
- Agents configurés pour accéder à la base de données et Meilisearch
- Résultats retournés au backend pour traitement/finalisation

**Note**: À évaluer selon les besoins réels. Peut être optionnel si RAG + recherche sémantique suffisent.

---

## Architecture Globale Post-App Review

```
┌─────────────────────────────────────────────────────────┐
│              Frontend (Vercel)                          │
│  React + TypeScript + Recherche UX avancée              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Backend (Railway)                          │
│  FastAPI                                                │
│  ├─→ PostgreSQL (Supabase) + pgvector                  │
│  ├─→ Meilisearch (Filtres, Ranking Rules)              │
│  ├─→ Redis (Cache)                                      │
│  └─→ Dust API (Agents reasoning)                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         Ingestion (Make/n8n)                            │
│  Workflows automatisés                                  │
│  ├─→ Instagram Graph API                               │
│  └─→ TikTok API                                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         Services Externes                               │
│  OpenAI (Embeddings)                                    │
│  Meta/Facebook APIs                                     │
│  TikTok APIs                                            │
└─────────────────────────────────────────────────────────┘
```

---

## Plan d'Implémentation

### Phase 2.1: Meilisearch Advanced (Priorité 1)
- [ ] Configurer ranking rules personnalisées
- [ ] Implémenter filtres avancés dans l'interface
- [ ] Ajouter facettes dynamiques
- [ ] Optimiser autocomplétion

### Phase 2.2: Supabase + pgvector (Priorité 2)
- [ ] Migrer vers Supabase (ou ajouter pgvector à Railway)
- [ ] Générer embeddings pour contenu existant
- [ ] Implémenter similarity search
- [ ] Créer endpoints RAG
- [ ] Hybrid search (Meilisearch + pgvector)

### Phase 2.3: Make/n8n Ingestion (Priorité 3)
- [ ] Configurer workflows Make/n8n
- [ ] Créer endpoints FastAPI pour réception données
- [ ] Tester ingestion Instagram
- [ ] Tester ingestion TikTok
- [ ] Monitoring et alertes

### Phase 2.4: Dust Agents (Priorité 4 - Optionnel)
- [ ] Évaluer besoins réels
- [ ] Configurer agents Dust si nécessaire
- [ ] Intégrer avec FastAPI
- [ ] Tests et validation

---

## Variables d'Environnement Supplémentaires

```bash
# Supabase
SUPABASE_URL=https://...
SUPABASE_KEY=...
SUPABASE_DB_URL=postgresql://...

# Embeddings (OpenAI ou alternative)
OPENAI_API_KEY=...
EMBEDDINGS_MODEL=text-embedding-3-small

# Make/n8n
MAKE_WEBHOOK_URL=...
N8N_WEBHOOK_URL=...
MAKE_API_KEY=...

# Dust (si utilisé)
DUST_API_KEY=...
DUST_WORKSPACE_ID=...
```

---

## Ressources

- [Meilisearch Documentation](https://www.meilisearch.com/docs)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Supabase Vector Guide](https://supabase.com/docs/guides/ai)
- [Make Platform](https://www.make.com/)
- [n8n Documentation](https://docs.n8n.io/)
- [Dust Platform](https://dust.tt/)

---

## Notes

- **Priorisation**: Meilisearch d'abord (impact UX immédiat), puis Supabase+pgvector (recherche sémantique), puis Make/n8n (automatisation)
- **Compatibilité**: S'assurer que Supabase est compatible avec l'infrastructure actuelle (ou migration progressive)
- **Costs**: Évaluer les coûts de Supabase, OpenAI embeddings, et Make/n8n avant déploiement
- **Testing**: Valider chaque composant indépendamment avant intégration complète

