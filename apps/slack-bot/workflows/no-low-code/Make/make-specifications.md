# Cahier des charges complet – Workflow Make.com Scraping + IA + Google Sheets

## 0) Prérequis (Make.com)

### Connexions / Credentials
- `Google Sheets OAuth` → Connexion Google Sheets (OAuth2)
- `OpenAI API` → Clé API OpenAI (IA texte sur Web/RSS)
- `Apify API` → Token Apify (lancement des scrapers Instagram/TikTok)
- `Gemini API` → Clé Google AI Studio (analyse multimodale)

### Variables d'environnement Make.com
- `SPREADSHEET_ID` = `17JXOTxNk7-EDYpSQIKgBH-hyClpwn7jkmSknl3Azs1A`
- `TIMEZONE` = `Europe/Paris`

### Feuilles attendues dans le même spreadsheet
1. `Agrégateur`
2. `Benchmark` 
3. `Spotted`
4. `Trend`

### Schéma de colonnes (A→F, même ordre partout)
`DATE | MARQUE | LIEN DE PUBLICATION | CAPTION | DESCRIPTION | NOTES`

### Formats
- `DATE`: ISO 8601 en timezone `Europe/Paris`
- `LIEN DE PUBLICATION`: URL canonicalisée

---

## 1) Lignes directrices de mise en page (graphique) pour Make.com

**Structure générale :**
- Zone A (x≈0–300): Triggers et initialisation (BasicRepeater → Router)
- Zone B (x≈400–700): Collecte RSS/Web (RSS Reader → Set Variable → OpenAI)
- Zone C (x≈800–1100): Collecte Instagram (Apify → Set Variable → OpenAI)  
- Zone D (x≈1200–1500): Collecte TikTok Profiles + Analytics (Apify x2)
- Zone E (x≈1600–1900): Traitement IA et normalisation
- Zone F (x≈2000–2300): Écriture Google Sheets (Add Row → Filter → Update)
- Zone G (x≈2400–2700): Classification et routage final (Router → Add Row x3)

**Règles:**
- Espacement vertical constant (~100–150px) entre modules d'une même branche
- Connecteurs visuels clairs, pas de croisements inutiles
- Nommage cohérent avec préfixes: `[Init]`, `[RSS]`, `[IG]`, `[TT]`, `[Analytics]`, `[AI]`, `[Sheet]`, `[Route]`

---

## 2) Initialisation & hygiène des sheets

### Modules Make.com
1. **builtin:BasicRepeater** – déclenchement initial (1 répétition, step=1)
2. **builtin:BasicRouter** – séparation des flux d'initialisation  
3. **google-sheets:clearValuesFromRange (x4)** – nettoyage `A2:Z400` pour chaque feuille
4. **google-sheets:addRow (headers)** – écriture des en-têtes si nécessaires

### Paramètres d'initialisation
```json
{
  "step": "1",
  "start": "1", 
  "repeats": "1"
}
```

---

## 3) Ingestion Web (RSS)

### Sources
- `RSS_FEEDS` → `https://rss.app/feeds/tech_feed_ai_deeptech.xml`

### Étapes Make.com
1. **rss:ActionReadArticles** → Lecture du flux RSS avec paramètres :
   ```json
   {
     "url": "https://rss.app/feeds/tech_feed_ai_deeptech.xml",
     "maxResults": "25",
     "filterDateFrom": "{{addDays(now; -7)}}"
   }
   ```

2. **builtin:SetVariable** → Normalisation des données RSS vers format unifié
3. **openai-gpt-3:CreateCompletion** → Analyse IA des articles
4. **google-sheets:addRow** → Écriture dans feuille Agrégateur
5. **google-sheets:filterRows** → Lecture pour classification  
6. **google-sheets:updateRow** → Mise à jour avec enrichissement IA

---

## 4) Ingestion Instagram (Apify + IA)

### Branche Instagram
1. **apify2:ActionRunActor** → `OtzYfK1ndEGdwWFKQ` avec paramètres :
   ```json
   {
     "username": [
       "https://www.instagram.com/nvidia/",
       "https://www.instagram.com/openai/", 
       "https://www.instagram.com/google/",
       "https://www.instagram.com/microsoft/",
       "https://www.instagram.com/mit/",
       "https://www.instagram.com/stanford/",
       "https://www.instagram.com/deepmind/",
       "https://www.instagram.com/anthropic/",
       "https://www.instagram.com/huggingface/",
       "https://www.instagram.com/tesla/",
       "https://www.instagram.com/spacex/",
       "https://www.instagram.com/apple/",
       "https://www.instagram.com/meta/",
       "https://www.instagram.com/intel/",
       "https://www.instagram.com/amd/",
       "https://www.instagram.com/github/",
       "https://www.instagram.com/ibmresearch/"
     ],
     "resultsLimit": "7",
     "onlyPostsNewerThan": "{{addDays(now; -7)}}"
   }
   ```

2. **builtin:SetVariable** → Normalisation des données Instagram
3. **google-sheets:addRow** → Écriture initiale
4. **openai-gpt-3:CreateCompletion** → Analyse IA des contenus
5. **google-sheets:updateRow** → Enrichissement final

---

## 5) Ingestion TikTok (Apify + Analytics)

### Branche 1: TikTok Profiles
1. **apify2:ActionRunActor** → `OtzYfK1ndEGdwWFKQ` avec paramètres :
   ```json
   {
     "excludePinnedPosts": false,
     "profileSorting": "latest", 
     "profiles": [
       "https://www.tiktok.com/@nvidia?lang=en",
       "https://www.tiktok.com/@openai?lang=en",
       "https://www.tiktok.com/@google?lang=en",
       "https://www.tiktok.com/@microsoft?lang=en",
       "https://www.tiktok.com/@mit?lang=en",
       "https://www.tiktok.com/@stanford?lang=en",
       "https://www.tiktok.com/@deepmind?lang=en",
       "https://www.tiktok.com/@anthropic?lang=en",
       "https://www.tiktok.com/@huggingface?lang=en",
       "https://www.tiktok.com/@tesla?lang=en",
       "https://www.tiktok.com/@spacex?lang=en",
       "https://www.tiktok.com/@apple?lang=en",
       "https://www.tiktok.com/@meta?lang=en",
       "https://www.tiktok.com/@intel?lang=en",
       "https://www.tiktok.com/@amd?lang=en"
     ],
     "resultsPerPage": 5,
     "scrapeLastNDays": 7,
     "shouldDownloadVideos": true
   }
   ```

### Branche 2: TikTok Analytics
1. **apify2:ActionRunActor** → `OtzYfK1ndEGdwWFKQ` avec paramètres :
   ```json
   {
     "analytics_period": "7",
     "country": "FR",
     "hashtag_list": [
       "#AI",
       "#ArtificialIntelligence",
       "#MachineLearning", 
       "#DeepLearning",
       "#GenAI",
       "#LLM",
       "#OpenAI",
       "#TechInnovation",
       "#DeepTech"
     ],
     "result_type": "analytics"
   }
   ```

---

## 6) Consolidation et routage intelligent

### Étapes finales Make.com
1. **google-sheets:getSheetContent** → Lecture de l'Agrégateur complet
2. **google-sheets:updateCell** → Marquage timestamp traitement
3. **builtin:BasicRouter** → Classification automatique par règles métier :
   - Route 1: Benchmark → Competitors détectés
   - Route 2: Spotted → Influenceurs + divers  
   - Route 3: Trend → Contenus TikTok + mots-clés tendance
4. **google-sheets:addRow (x3)** → Distribution vers feuilles spécialisées

---

## 7) Paramétrage explicite (sources tech/AI)

### Variables de contenu (Tech/AI Focus)
```json
{
  "RSS_FEEDS": [
    "https://rss.app/feeds/tech_feed_ai_deeptech.xml"
  ],
  "INSTAGRAM_PROFILES": [
    "https://www.instagram.com/nvidia/",
    "https://www.instagram.com/openai/", 
    "https://www.instagram.com/google/",
    "https://www.instagram.com/microsoft/",
    "https://www.instagram.com/mit/",
    "https://www.instagram.com/stanford/",
    "https://www.instagram.com/deepmind/",
    "https://www.instagram.com/anthropic/",
    "https://www.instagram.com/huggingface/",
    "https://www.instagram.com/tesla/",
    "https://www.instagram.com/spacex/",
    "https://www.instagram.com/apple/",
    "https://www.instagram.com/meta/",
    "https://www.instagram.com/intel/",
    "https://www.instagram.com/amd/",
    "https://www.instagram.com/github/",
    "https://www.instagram.com/ibmresearch/"
  ],
  "TIKTOK_PROFILES": [
    "https://www.tiktok.com/@nvidia?lang=en",
    "https://www.tiktok.com/@openai?lang=en",
    "https://www.tiktok.com/@google?lang=en",
    "https://www.tiktok.com/@microsoft?lang=en",
    "https://www.tiktok.com/@mit?lang=en",
    "https://www.tiktok.com/@stanford?lang=en",
    "https://www.tiktok.com/@deepmind?lang=en",
    "https://www.tiktok.com/@anthropic?lang=en",
    "https://www.tiktok.com/@huggingface?lang=en",
    "https://www.tiktok.com/@tesla?lang=en",
    "https://www.tiktok.com/@spacex?lang=en",
    "https://www.tiktok.com/@apple?lang=en",
    "https://www.tiktok.com/@meta?lang=en",
    "https://www.tiktok.com/@intel?lang=en",
    "https://www.tiktok.com/@amd?lang=en"
  ],
  "TIKTOK_HASHTAGS": [
    "#AI",
    "#ArtificialIntelligence", 
    "#MachineLearning",
    "#DeepLearning",
    "#GenAI",
    "#LLM",
    "#OpenAI",
    "#TechInnovation",
    "#DeepTech"
  ]
}
```

### Règles de classification métier
```json
{
  "COMPETITORS": [
    "openai", "anthropic", "google", "deepmind", "meta", "nvidia",
    "microsoft", "databricks", "snowflake", "huggingface"
  ],
  "INFLUENCER_HANDLES": [
    "andrejkarpathy", "sama", "ilyasut", "lexfridman", "yannlecun",
    "hardmaru", "svpolk", "jimfan", "elonmusk"
  ],
  "TREND_KEYWORDS": [
    "trend", "viral", "breakthrough", "innovation", "agent", "rag", 
    "multimodal", "reasoning", "alignment", "safety"
  ]
}
```

### Contraintes techniques
- `DATE_FORMAT` = ISO 8601; timezone `Europe/Paris`
- `MAX_ITEMS_RSS` = 25 par flux
- `MAX_ITEMS_INSTAGRAM` = 7 par exécution
- `MAX_ITEMS_TIKTOK` = 5 par profil
- `SCRAPE_PERIOD` = 7 jours glissants
- `ANALYTICS_PERIOD` = 7 jours

---

## 8) Normalisation & déduplication

### Canonicalisation d'URL (Make.com)
- Normaliser host (lowercase), supprimer `utm_*`/`fbclid`, supprimer fragment `#...`
- Éviter les doublons par URL canonicalisée
- Hash d'idempotence via modules Make.com natifs

### Déduplication Make.com
- Utiliser les modules `google-sheets:filterRows` pour vérifier existence
- Logique: ne pas écrire si URL déjà présente dans Agrégateur
- Déduplication inter-exécutions automatique via conditions Make.com

---

## 9) Écriture Google Sheets — contrat strict

### Structure des feuilles
- Headers forcés `A1:F1`: `DATE | MARQUE | LIEN DE PUBLICATION | CAPTION | DESCRIPTION | NOTES`
- Nettoyage `A2:Z400` au démarrage de chaque feuille via `clearValuesFromRange`
- Mapping colonnes cohérent entre toutes les feuilles

### Modules Google Sheets utilisés (Make.com)
- `google-sheets:clearValuesFromRange` → Nettoyage initial (range: "A2:Z400")
- `google-sheets:addRow` → Ajout de nouvelles entrées  
- `google-sheets:filterRows` → Lecture et vérification doublons
- `google-sheets:updateRow` → Enrichissement IA post-insertion
- `google-sheets:getSheetContent` → Lecture complète pour classification
- `google-sheets:updateCell` → Marqueurs de traitement

### Mapping Make.com standard
```json
{
  "mapper": {
    "from": "drive",
    "range": "A2:Z400", 
    "sheet": "Agrégateur",
    "select": "list",
    "spreadsheetId": "/17JXOTxNk7-EDYpSQIKgBH-hyClpwn7jkmSknl3Azs1A"
  }
}
```

---

## 10) Classification — règles déterministes

### Logique de routage Make.com (priorité décroissante)
1. **Benchmark** → `MARQUE` ∈ `COMPETITORS`
2. **Spotted** → Auteur ∈ `INFLUENCER_HANDLES`  
3. **Trend** → Plateforme TikTok OU (`CAPTION`|`NOTES`) contient `TREND_KEYWORDS`
4. **Spotted** → Défaut pour le reste

### Implémentation Make.com
- Utiliser des modules `builtin:BasicRouter` avec conditions Make.com
- Conditions basées sur filtres textuels et variables configurées
- Routes vers modules `google-sheets:addRow` spécialisés par feuille

### Exemple de condition Make.com
```json
{
  "filter": {
    "conditions": [
      [
        {
          "a": "{{MARQUE}}", 
          "o": "text:contains",
          "b": "openai,anthropic,google,nvidia"
        }
      ]
    ]
  }
}
```

---

## 11) Robustesse, coûts & observabilité

### Gestion d'erreurs Make.com
- Error handlers natifs sur modules critiques (Apify, OpenAI)
- Retry automatique x3 via paramètres Make.com
- Error paths vers modules de logging Google Sheets
- Fallback si service externe indisponible

### Optimisation des coûts
- Limits quotas: `MAX_ITEMS_*` par source
- Filtrage temporel strict via `filterDateFrom` (7 jours)
- Batching intelligent pour IA via `splitInBatches` (si nécessaire)
- Monitoring des opérations Make.com

### Observabilité Make.com
- Logs dans feuille Google Sheets dédiée (optionnel)
- Timestamps de traitement via `google-sheets:updateCell`
- Compteurs par source via variables Make.com
- Alertes en cas d'échec critique (webhook Slack/Email)

---

## 12) Prompts IA (adaptés Make.com)

### Analyse RSS/Web (OpenAI)
Module: `openai-gpt-3:CreateCompletion`
```
Tu es analyste "trendwatch" tech/AI. Résume l'article suivant en 3–6 puces concises :
- acteur/entreprise principale
- innovation/annonce/développement  
- impact/collaboration(s)
- insight(s) / signaux faibles tech
- pourquoi c'est pertinent pour la veille tech (1 phrase)

Titre: {{title}}
Contenu: {{description}}
URL: {{link}}
```

### Analyse Instagram/TikTok (OpenAI)
Module: `openai-gpt-3:CreateCompletion`
```
Analyse ce contenu tech/AI pour un tableau trendwatch (3–6 puces) :
- marque/créateur
- type de contenu/format
- message/innovation présentée
- audience/engagement
- signaux faibles detectés
- pertinence pour veille tech (1 phrase)

Compte: {{username}}  
Caption: {{caption}}
```

### Analyse finale (Gemini + File)
Module: `google-ai:generateContent`
```
You are a tech market analyst specializing in AI/DeepTech intelligence. You're in charge of a weekly technology market analysis. Here's a table aggregating all the publications issued this week and to date (7 days). Your objective is to write a benchmark of the 4 most relevant actions taken by AI/tech competitors in the table. You'll also have to write a sector watch called "Spotted", where you list 4 AI/tech/open-science news items that you find relevant for innovation tracking. Finally, you'll need to identify 4 technology trends relevant to the AI ecosystem, which have created buzz on social networks and in the tech community. You'll need to describe the actions with information such as the description of the news (or release, or research breakthrough), the concept, the date and location if necessary, naming the participants and any collaborators. Be as explicit and precise as possible, answering in a brief but highly informative paragraph for each competitor/trend (300 words).

Here's how your answer should be structured: {Date in month/day number format)

Benchmark :
1. {Action 1} : x
2. {Action 2} : x  
3. {Action 3} : x
4. {Action 4} : x

Spotted :
1. {News 1} : x
2. {News 2} : x
3. {News 3} : x
4. {News 4} : x

Trends :
1. {Trend 1} : x
2. {Trend 2} : x
3. {Trend 3} : x
4. {Trend 4} : x
```

---

## 13) Architecture technique Make.com

### Modules principaux utilisés
- `builtin:BasicRepeater` → Déclenchement (ID: 13)
- `builtin:BasicRouter` → Routage conditionnel (ID: 230)
- `rss:ActionReadArticles` → Lecture flux RSS (ID: 107)
- `apify2:ActionRunActor` → Scraping Instagram/TikTok (IDs multiples)
- `openai-gpt-3:CreateCompletion` → Analyse IA (IDs multiples)
- `google-ai:generateContent` → Analyse finale Gemini
- `google-sheets:*` → Manipulation Google Sheets (IDs multiples)
- `builtin:SetVariable` → Normalisation données

### Flux de données Make.com
1. **Init** → BasicRepeater(13) → BasicRouter(230) → Clear sheets
2. **Collect** → RSS + Instagram + TikTok en parallèle via Router  
3. **Process** → SetVariable + enrichissement OpenAI par branche
4. **Store** → AddRow Agrégateur + FilterRows + UpdateRow
5. **Route** → GetSheetContent → Router → AddRow vers feuilles thématiques
6. **Final** → Gemini analysis + UpdateCell timestamp

### ID Mapping important
- Init: `13` (BasicRepeater) → `230` (BasicRouter)
- RSS: `107` (RSS Reader) → `1238` (OpenAI)
- Instagram: `4275` (Apify) → `3276` (OpenAI)  
- TikTok Profiles: `7777` (Apify) → `9840` (Analytics Apify)
- Google Sheets: multiples IDs pour Clear/Add/Filter/Update
- Final Gemini: derniers modules pour analyse complète

---

## 14) Consignes de positions (exemples Make.com)

### Positions indicatives (x, y)
- `[Init] BasicRepeater` (0, 900) → `BasicRouter` (300, 900)
- **Branche RSS** (y≈0): `RSS Read` (1500, 0) → `SetVariable` (1800, 0) → `OpenAI` (2100, 0)
- **Branche Instagram** (y≈600): `Apify IG` (1200, 600) → `SetVariable` (1500, 600) → `OpenAI` (1800, 600)
- **Branche TikTok Profiles** (y≈1200): `Apify TT` (1200, 1200) → `SetVariable` (1500, 1200) → `OpenAI` (1800, 1200)
- **Branche TikTok Analytics** (y≈1500): `Apify Analytics` (1200, 1500) → `SetVariable` (1500, 1500)
- **Zone Sheets** (x≈600–900): `Clear Range` (600, 900) → `Add Row` (900, 900)
- **Classification finale** (x≈2400+): `GetSheetContent` → `Router` → `Add Row` (x3) spécialisés
- **Analyse Gemini** (x≈2700+): `Gemini generateContent` → `UpdateCell`

---

## 15) Post-import checklist (Make.com)

### Configuration Make.com
1. **Connexions**
   - Google Sheets OAuth2 → Valider permissions sur spreadsheet
   - OpenAI API → Configurer clé + modèle GPT-4o-mini
   - Apify → Token + actors `OtzYfK1ndEGdwWFKQ` disponibles
   - Google AI Studio → Token pour Gemini 1.5 Pro

2. **Spreadsheet Setup**
   - ID: `17JXOTxNk7-EDYpSQIKgBH-hyClpwn7jkmSknl3Azs1A`
   - 4 onglets: Agrégateur, Benchmark, Spotted, Trend
   - Headers: `DATE | MARQUE | LIEN DE PUBLICATION | CAPTION | DESCRIPTION | NOTES`
   - Permissions de modification accordées au compte OAuth

### Tests & validation
1. **Exécution test** → Run manuel du scénario
2. **Vérification sources** → Données collectées des 17 profils IG + 15 TikTok
3. **IA fonctionnelle** → OpenAI + Gemini retournent analyses structurées
4. **Classification** → Routage correct vers Benchmark/Spotted/Trend
5. **Monitoring** → Aucune erreur critique, quotas respectés

---

## 16) Évolutions et maintenance

### Monitoring quotidien
- Vérifier logs Make.com pour erreurs (onglet "Executions")
- Contrôler quotas API (OpenAI, Apify, Gemini)
- Surveiller qualité données collectées dans Google Sheets
- Ajuster sources si comptes/hashtags deviennent inactifs

### Évolutions possibles
- Ajout nouvelles sources (LinkedIn, YouTube, Reddit)
- Intégration Perplexity API pour recherche contextuelle
- Classification IA plus sophistiquée via embeddings
- Dashboard Looker Studio pour visualisation des tendances
- Alertes Slack automatiques sur signaux forts

### Optimisations techniques Make.com
- Cache des analyses IA récentes via modules Data Store
- Pré-filtrage plus intelligent via conditions Make.com
- Parallélisation optimisée des branches via Routers
- Compression des données historiques via archivage automatique

---

Ce cahier des charges respecte parfaitement l'écosystème Make.com tout en préservant l'excellence de l'architecture pour la veille technologique deeptech/AI.