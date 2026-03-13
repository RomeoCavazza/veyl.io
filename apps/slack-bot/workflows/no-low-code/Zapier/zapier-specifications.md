# Cahier des charges complet – Zaps Zapier Scraping + IA + Google Sheets

> Commentaires initiaux (lire avant génération):
> - Objectif: système de veille technologique AI/DeepTech via Zapier pour agréger des actualités Web/RSS, réseaux sociaux, les analyser par IA, les écrire dans un Google Sheet, puis router vers 3 feuilles thématiques.
> - Sortie finale souhaitée: des Zaps Zapier configurables directement, propres visuellement, idempotents, robustes aux limitations de plan.
> - Audience: un LLM (Claude Sonnet 4) qui doit concevoir l'architecture Zapier optimale; et un dev qui validera.
> - Style attendu: triggers efficaces, actions chainées, webhooks personnalisés, gestion des quotas Zapier.

---

## 0) Prérequis (Zapier)

### Connexions / Apps requises
- `Google Sheets` → Connexion Google Sheets (OAuth2)
- `OpenAI` → Intégration OpenAI (API Key)
- `Webhooks by Zapier` → Pour appels API custom (Apify, Gemini)
- `RSS by Zapier` → Lecture flux RSS
- `Schedule by Zapier` → Déclenchement temporel
- `Filter by Zapier` → Logique conditionnelle
- `Formatter by Zapier` → Transformation données

### Variables globales Zapier
- `SPREADSHEET_ID` = `17JXOTxNk7-EDYpSQIKgBH-hyClpwn7jkmSknl3Azs1A`
- `APIFY_TOKEN` → Token Apify pour scraping
- `GOOGLE_AI_API_KEY` → Clé Google AI Studio (Gemini)
- `TIMEZONE` = `Europe/Paris`

### Feuilles Google Sheets (même spreadsheet)
1. `Agrégateur`
2. `Benchmark` 
3. `Spotted`
4. `Trend`

### Schéma de colonnes (A→F, ordre strict)
`DATE | MARQUE | LIEN DE PUBLICATION | CAPTION | DESCRIPTION | NOTES`

### Formats standards
- `DATE`: ISO 8601 en timezone `Europe/Paris`
- `LIEN DE PUBLICATION`: URL canonicalisée
- `MARQUE`: Handle/nom normalisé

---

## 1) Architecture Zapier - Approche Multi-Zaps

> Objectif: système modulaire basé sur des Zaps spécialisés, optimisé pour les limitations Zapier.

**Structure générale (6 Zaps principaux) :**

### Zap 1: **[INIT] Préparation Sheets**
- **Trigger**: Schedule (hebdomadaire, lundis 8h)
- **Actions**: Clear ranges + Set headers (4 feuilles)

### Zap 2: **[RSS] Veille Web**  
- **Trigger**: RSS by Zapier (flux tech/AI)
- **Actions**: OpenAI → Format → Google Sheets → Classifier

### Zap 3: **[IG] Veille Instagram**
- **Trigger**: Schedule (quotidien)
- **Actions**: Webhook Apify → Format → Google Sheets

### Zap 4: **[TT] Veille TikTok**
- **Trigger**: Schedule (quotidien) 
- **Actions**: Webhook Apify → Format → Google Sheets

### Zap 5: **[ROUTE] Classification**
- **Trigger**: New row Google Sheets (Agrégateur)
- **Actions**: Filter + Route vers Benchmark/Spotted/Trend

### Zap 6: **[ANALYTICS] Analyse finale**
- **Trigger**: Schedule (hebdomadaire, dimanches)
- **Actions**: Lire Agrégateur → Gemini → Export rapport

**Contraintes Zapier :**
- Max 100 steps par Zap (plan Pro)
- Fréquence limitée selon plan
- Pas de boucles complexes
- Actions séquentielles simples

---

## 2) Zap 1: Initialisation & hygiène sheets

### Configuration
- **Trigger**: Schedule by Zapier
  - Fréquence: `Weekly on Monday at 08:00`
  - Timezone: `Europe/Paris`

### Actions séquentielles
1. **Google Sheets - Clear Range** 
   - Spreadsheet: `17JXOTxNk7-EDYpSQIKgBH-hyClpwn7jkmSknl3Azs1A`
   - Worksheet: `Agrégateur` 
   - Range: `A2:F1000`

2. **Google Sheets - Clear Range** (x3 autres feuilles)
   - Worksheets: `Benchmark`, `Spotted`, `Trend`
   - Range: `A2:F1000`

3. **Google Sheets - Update Spreadsheet Row**
   - Worksheet: `Agrégateur`
   - Row: `1`
   - Values: `DATE | MARQUE | LIEN DE PUBLICATION | CAPTION | DESCRIPTION | NOTES`

4. **Google Sheets - Update Spreadsheet Row** (x3 headers)
   - Répéter pour autres feuilles

---

## 3) Zap 2: Ingestion RSS/Web

### Configuration
- **Trigger**: RSS by Zapier
  - Feed URL: `https://rss.app/feeds/tech_feed_ai_deeptech.xml`
  - Trigger on: `New Item in Feed`

### Actions séquentielles  
1. **Filter by Zapier**
   - Condition: Publication date within 7 days
   - Skip if: Date < {{today - 7 days}}

2. **Formatter by Zapier - Text**
   - Transform: Extract domain from URL
   - Input: `{{trigger.link}}`
   - Action: `Extract Domain`

3. **OpenAI - Send Prompt** 
   - Model: `gpt-4o-mini`
   - Temperature: `0.6`
   - Prompt: 
   ```
   Tu es analyste "trendwatch" tech/AI. Résume l'article suivant en 3–6 puces concises :
   - acteur/entreprise principale
   - innovation/annonce/développement  
   - impact/collaboration(s)
   - insight(s) / signaux faibles tech
   - pourquoi c'est pertinent pour la veille tech (1 phrase)

   Titre: {{trigger.title}}
   Contenu: {{trigger.description}}
   URL: {{trigger.link}}
   ```

4. **Google Sheets - Create Spreadsheet Row**
   - Spreadsheet: `17JXOTxNk7-EDYpSQIKgBH-hyClpwn7jkmSknl3Azs1A`
   - Worksheet: `Agrégateur`
   - Values:
     - `DATE`: `{{trigger.date_published}}`
     - `MARQUE`: `{{step_2.output}}`
     - `LIEN DE PUBLICATION`: `{{trigger.link}}`
     - `CAPTION`: `{{trigger.title}}`
     - `DESCRIPTION`: `{{trigger.description}}`
     - `NOTES`: `{{step_3.output}}`

---

## 4) Zap 3: Ingestion Instagram

### Configuration
- **Trigger**: Schedule by Zapier
  - Fréquence: `Daily at 09:00`
  - Timezone: `Europe/Paris`

### Actions séquentielles
1. **Webhooks by Zapier - POST**
   - URL: `https://api.apify.com/v2/acts/apify~instagram-post-scraper/run-sync-get-dataset?token={{env.APIFY_TOKEN}}`
   - Method: `POST`
   - Headers: `Content-Type: application/json`
   - Data:
   ```json
   {
     "directUrls": [],
     "resultsType": "posts",
     "resultsLimit": 7,
     "searchType": "hashtag",
     "hashtags": ["#AI", "#DeepLearning", "#MachineLearning", "#ArtificialIntelligence", "#GenAI", "#LLM", "#OpenAI", "#TechInnovation", "#DeepTech"],
     "profileUrls": [
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
     ]
   }
   ```

2. **Formatter by Zapier - Utilities**
   - Transform: `Line-item to Text`
   - Input: `{{step_1.data}}`
   - Action: Parse JSON array

3. **Filter by Zapier**
   - Condition: Only continue if data exists
   - Skip if: `{{step_2.output}}` is empty

4. **Google Sheets - Create Spreadsheet Row**
   - Spreadsheet: `17JXOTxNk7-EDYpSQIKgBH-hyClpwn7jkmSknl3Azs1A`
   - Worksheet: `Agrégateur`
   - Values:
     - `DATE`: `{{step_2.timestamp}}`
     - `MARQUE`: `{{step_2.ownerUsername}}`
     - `LIEN DE PUBLICATION`: `{{step_2.url}}`
     - `CAPTION`: `{{step_2.caption}}`
     - `DESCRIPTION`: ``
     - `NOTES`: `[Instagram] {{step_2.caption}}`

---

## 5) Zap 4: Ingestion TikTok

### Configuration  
- **Trigger**: Schedule by Zapier
  - Fréquence: `Daily at 10:00`
  - Timezone: `Europe/Paris`

### Actions séquentielles
1. **Webhooks by Zapier - POST** (Profiles)
   - URL: `https://api.apify.com/v2/acts/apify~tiktok-scraper/run-sync-get-dataset?token={{env.APIFY_TOKEN}}`
   - Method: `POST`
   - Data:
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
     "shouldDownloadVideos": false
   }
   ```

2. **Webhooks by Zapier - POST** (Analytics)
   - URL: `https://api.apify.com/v2/acts/apify~tiktok-scraper/run-sync-get-dataset?token={{env.APIFY_TOKEN}}`
   - Data:
   ```json
   {
     "analytics_period": "7",
     "country": "FR", 
     "hashtag_list": ["#AI", "#ArtificialIntelligence", "#MachineLearning", "#DeepLearning", "#GenAI", "#LLM", "#OpenAI", "#TechInnovation", "#DeepTech"],
     "result_type": "analytics"
   }
   ```

3. **Formatter by Zapier - Utilities**
   - Combine outputs from steps 1 & 2
   - Normalize data format

4. **Google Sheets - Create Spreadsheet Row**
   - Similar to Instagram with TikTok-specific fields

---

## 6) Zap 5: Classification automatique

### Configuration
- **Trigger**: Google Sheets - New Spreadsheet Row
  - Spreadsheet: `17JXOTxNk7-EDYpSQIKgBH-hyClpwn7jkmSknl3Azs1A`
  - Worksheet: `Agrégateur`
  - Trigger Column: `A` (DATE)

### Actions séquentielles
1. **Filter by Zapier - Multiple Filters**
   - Path A: `{{trigger.MARQUE}}` contains competitors
     - Values: `openai,anthropic,google,deepmind,meta,nvidia,microsoft,databricks,snowflake,huggingface`
     - Action: Route to Benchmark

   - Path B: `{{trigger.MARQUE}}` contains influencers  
     - Values: `andrejkarpathy,sama,ilyasut,lexfridman,yannlecun,hardmaru,svpolk,jimfan,elonmusk`
     - Action: Route to Spotted

   - Path C: `{{trigger.CAPTION}}` or `{{trigger.NOTES}}` contains trends
     - Values: `trend,viral,breakthrough,innovation,agent,rag,multimodal,reasoning,alignment,safety`
     - Action: Route to Trend

   - Path D: Default
     - Action: Route to Spotted

2. **Google Sheets - Create Spreadsheet Row** (Benchmark)
   - Condition: Path A triggered
   - Worksheet: `Benchmark`
   - Copy all trigger data

3. **Google Sheets - Create Spreadsheet Row** (Spotted)
   - Condition: Path B or D triggered  
   - Worksheet: `Spotted`
   - Copy all trigger data

4. **Google Sheets - Create Spreadsheet Row** (Trend)
   - Condition: Path C triggered
   - Worksheet: `Trend`
   - Copy all trigger data

---

## 7) Zap 6: Analyse finale et reporting

### Configuration
- **Trigger**: Schedule by Zapier
  - Fréquence: `Weekly on Sunday at 18:00`
  - Timezone: `Europe/Paris`

### Actions séquentielles
1. **Google Sheets - Lookup Spreadsheet Rows**
   - Spreadsheet: `17JXOTxNk7-EDYpSQIKgBH-hyClpwn7jkmSknl3Azs1A`
   - Worksheet: `Agrégateur`
   - Lookup Column: `A` (DATE)
   - Lookup Value: `>= {{today - 7 days}}`

2. **Formatter by Zapier - Text**
   - Action: Join data into CSV format
   - Input: All rows from step 1
   - Separator: newline

3. **Webhooks by Zapier - POST** (Gemini)
   - URL: `https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={{env.GOOGLE_AI_API_KEY}}`
   - Method: `POST`
   - Data:
   ```json
   {
     "contents": [{
       "parts": [{
         "text": "You are a tech market analyst specializing in AI/DeepTech intelligence. You're in charge of a weekly technology market analysis. Here's a table aggregating all the publications issued this week and to date (7 days). Your objective is to write a benchmark of the 4 most relevant actions taken by AI/tech competitors in the table. You'll also have to write a sector watch called \"Spotted\", where you list 4 AI/tech/open-science news items that you find relevant for innovation tracking. Finally, you'll need to identify 4 technology trends relevant to the AI ecosystem, which have created buzz on social networks and in the tech community.\n\nData:\n{{step_2.output}}"
       }]
     }],
     "generationConfig": {"temperature": 0.7}
   }
   ```

4. **Google Sheets - Update Spreadsheet Row** 
   - Create summary row with Gemini analysis
   - Timestamp the report generation

---

## 8) Paramétrage explicite (sources tech/AI)

### Variables Zapier (Storage)
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

### Contraintes Zapier
- `DATE_FORMAT` = ISO 8601; timezone `Europe/Paris`
- `MAX_ITEMS_RSS` = illimité (trigger natif)
- `MAX_ITEMS_INSTAGRAM` = 7 par jour
- `MAX_ITEMS_TIKTOK` = 5 par profil  
- `SCRAPE_PERIOD` = 7 jours glissants
- `TASK_LIMIT` = selon plan Zapier (Starter: 750, Professional: 2000)

---

## 9) Gestion des limitations Zapier

### Optimisations plan Starter (750 tasks/mois)
- RSS trigger: ~30 tasks/mois (1/jour)
- Instagram: ~30 tasks/mois (1/jour)
- TikTok: ~30 tasks/mois (1/jour) 
- Classification: ~90 tasks/mois (3/jour moyenne)
- Analytics: ~4 tasks/mois (1/semaine)
- **Total estimé**: ~200 tasks/mois

### Optimisations plan Professional (2000+ tasks/mois)
- Fréquence accrue possible
- Multi-step Zaps complexes
- Webhooks illimités
- Filtres avancés

### Gestion des erreurs Zapier
- Auto-retry natif (3x)
- Error notifications par email
- Fallback paths dans filtres
- Monitoring via Dashboard Zapier

---

## 10) Normalisation & déduplication

### Canonicalisation d'URL (Zapier)
- Utiliser `Formatter by Zapier - Text`
- Actions: `Extract Domain`, `Remove Query Parameters`
- Normalisation: lowercase, suppression UTM
- Hash d'idempotence via `Formatter - Utilities`

### Déduplication Zapier
- **Filter by Zapier** sur nouvelles entrées
- Lookup Google Sheets avant insertion
- Skip si URL déjà présente
- Conditions: `{{trigger.url}}` NOT IN existing data

---

## 11) Écriture Google Sheets — contrat strict

### Structure des feuilles Zapier
- Headers fixes via Zap d'initialisation
- Range clear: `A2:F1000` (éviter limites)
- Mapping colonnes automatique via actions
- Timestamps ISO 8601 via Formatter

### Actions Google Sheets utilisées
- `Clear Range` → Nettoyage initial 
- `Create Spreadsheet Row` → Ajout de nouvelles entrées
- `Update Spreadsheet Row` → Headers + corrections
- `Lookup Spreadsheet Rows` → Lecture pour classification
- `Find Spreadsheet Row` → Vérification doublons

### Mapping Zapier standard
```
DATE → {{trigger.date_published}} ou {{formatted_date}}
MARQUE → {{extracted_domain}} ou {{username}}
LIEN DE PUBLICATION → {{trigger.link}} ou {{canonical_url}}
CAPTION → {{trigger.title}} ou {{caption}}
DESCRIPTION → {{trigger.description}} ou vide
NOTES → {{openai_output}} ou {{manual_note}}
```

---

## 12) Classification — logique Zapier

### Implémentation Filter by Zapier
```javascript
// Benchmark Path
{{trigger.MARQUE}} contains "openai" OR
{{trigger.MARQUE}} contains "anthropic" OR  
{{trigger.MARQUE}} contains "google" OR
{{trigger.MARQUE}} contains "nvidia"
// ... autres competitors

// Spotted Path  
{{trigger.MARQUE}} contains "andrejkarpathy" OR
{{trigger.MARQUE}} contains "sama" OR
{{trigger.MARQUE}} contains "lexfridman"
// ... autres influencers

// Trend Path
{{trigger.CAPTION}} contains "trend" OR
{{trigger.NOTES}} contains "viral" OR
{{trigger.NOTES}} contains "breakthrough"
// ... autres keywords

// Default: Spotted
```

### Actions conditionnelles
- **Path Continue If**: Condition met → Create Row destination
- **Path Stop**: Condition not met → Skip action
- **Multiple Paths**: Parallel execution possible

---

## 13) Prompts IA (adaptés Zapier)

### Analyse RSS/Web (OpenAI)
Action: `OpenAI - Send Prompt`
```
Tu es analyste "trendwatch" tech/AI. Résume l'article suivant en 3–6 puces concises :
- acteur/entreprise principale
- innovation/annonce/développement  
- impact/collaboration(s)
- insight(s) / signaux faibles tech
- pourquoi c'est pertinent pour la veille tech (1 phrase)

Titre: {{trigger.title}}
Contenu: {{trigger.description}}
URL: {{trigger.link}}
```

### Analyse finale (Gemini via Webhook)
Action: `Webhooks by Zapier - POST`
```
You are a tech market analyst specializing in AI/DeepTech intelligence. You're in charge of a weekly technology market analysis. Here's aggregated data from this week. Provide:

1. Benchmark (4 key competitor actions)
2. Spotted (4 innovation signals)  
3. Trends (4 social/tech trends)

Format each as informative paragraph (300 words max).

Data: {{formatted_data}}
```

---

## 14) Monitoring & observabilité

### Dashboard Zapier natif
- Task usage tracking
- Error rate monitoring  
- Success rate metrics
- Execution time analysis

### Alertes configurables
- Email sur échecs Zap
- Slack notifications (optionnel)
- Task limit warnings
- Performance degradation alerts

### Logs automatiques  
- Execution history (30 jours)
- Step-by-step debugging
- Data flow visualization
- Filter condition results

---

## 15) Post-setup checklist (Zapier)

### Configuration initiale
1. **Connexions d'apps**
   - Google Sheets → Autoriser accès spreadsheet
   - OpenAI → Configurer API key
   - RSS by Zapier → Tester flux RSS
   - Webhooks → Valider endpoints Apify/Gemini

2. **Variables d'environnement**
   - Storage Zapier pour listes de sources
   - API keys dans connexions sécurisées
   - URL spreadsheet configurée

3. **Tests des 6 Zaps**
   - Init → Vérifier nettoyage sheets
   - RSS → Tester trigger + OpenAI
   - Instagram → Valider webhook Apify  
   - TikTok → Confirmer scraping
   - Classification → Vérifier filtres
   - Analytics → Tester rapport Gemini

### Validation & optimisation
1. **Limitation de plan** → Ajuster fréquences selon quotas
2. **Performance** → Optimiser filtres et conditions
3. **Qualité données** → Valider mapping colonnes
4. **Robustesse** → Tester gestion d'erreurs

---

## 16) Évolutions et maintenance

### Monitoring quotidien Zapier
- Dashboard usage tasks
- Vérifier échecs d'exécution
- Contrôler qualité données sheets
- Ajuster sources si inactives

### Évolutions possibles
- Ajout nouveaux triggers (LinkedIn, YouTube)
- Multi-step Zaps plus complexes (plan supérieur)
- Intégrations avancées (Slack, Discord)
- Automation cross-platform

### Optimisations Zapier
- Filtres plus précis pour réduire tasks
- Groupement d'actions pour efficacité  
- Webhooks personnalisés pour flexibility
- Storage Zapier pour cache données

---

Ce cahier des charges adapte parfaitement l'architecture de veille tech/AI aux spécificités et contraintes de Zapier, tout en préservant la qualité et la richesse du système de surveillance technologique.
