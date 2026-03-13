# Cahier des charges complet – Workflow n8n Scraping + IA + Google Sheets

## 0) Prérequis (n8n)

### Crédentials / variables d’env
- `GOOGLESHEETS_OAUTH` → Credentials Google Sheets (OAuth2)
- `OPENAI_API_KEY` (IA texte sur Web/RSS)
- `GOOGLE_AI_API_KEY` (Gemini 1.5 Pro/Flash Vision pour IG/TikTok)
- `APIFY_TOKEN` (lancement des scrapers Apify)
- `SPREADSHEET_ID` = `17JXOTxNk7-EDYpSQIKgBH-hyClpwn7jkmSknl3Azs1A` (ID du Google Sheet cible)
- `TIMEZONE` = `Europe/Paris`

### Feuilles attendues dans le même spreadsheet (`SPREADSHEET_ID`)
1. `Agrégateur général`
2. `Benchmark`
3. `Spotted`
4. `Trend`

### Schéma de colonnes (A→F, même ordre partout)
`DATE | MARQUE | LIEN DE PUBLICATION | CAPTION | DESCRIPTION | NOTES`

### Formats
- `DATE`: ISO 8601 en timezone `Europe/Paris`
- `LIEN DE PUBLICATION`: URL canonicalisée (voir §8)

---

## 1) Lignes directrices de mise en page (graphique) pour n8n

- Colonne A (x≈200–450): Triggers et initialisation Sheets
- Colonne B (x≈700–1000): Branche Web/RSS
- Colonne C (x≈1150–1450): Branche Instagram
- Colonne D (x≈1600–1900): Branche TikTok
- Colonne E (x≈2050–2300): IA / Vision et mapping par branche
- Colonne F (x≈2400–2650): Agrégations par branche
- Colonne G (x≈2800–3050): Merge global + dédup final
- Colonne H (x≈3200–3450): Append `Agrégateur général`
- Colonne I (x≈3500–3800): Classification + Append `Benchmark`/`Spotted`/`Trend`

Règles:
- Espacement vertical constant (~120–160px) entre nodes d’une même branche
- Connecteurs rectilignes, pas de croisements inutiles
- Nommage des nodes avec préfixes clairs: `[Init]`, `[RSS]`, `[IG]`, `[TT]`, `[Merge]`, `[Route]`

---

## 2) Initialisation & hygiène des sheets

### Nœuds
1. **Cron** – planif hebdo (ex. `0 8 * * 1`) + exécution manuelle possible
2. **Google Sheets – Create Tabs if Missing (x4)** – crée les 4 feuilles si absentes
3. **Google Sheets – Clear (x4)** – `A2:F400` pour chaque feuille
4. **Google Sheets – Set headers (x4)** – écrit `A1:F1` avec l’en‑tête exact

---

## 3) Ingestion Web (RSS)

### Sources
- `RSS_FEEDS` (liste fixe) OU génération amont via rss.app (si utilisée, fournir l’URL finale du feed)

### Étapes
1. **RSS Feed Read (xN)** – lit chaque flux `RSS_FEEDS`
2. **Function – Normalize RSS** → map vers `{platform:'web', date, url, title, brand, caption, description, source}`
3. **Function – Filter+Dedup+Sort (7j)** → filtre <7 jours, dédup sur URL canonicalisée, tri date desc, limite `MAX_ITEMS_WEB`
4. **Split In Batches (BATCH_WEB)** – découpage pour IA texte
5. **OpenAI (Chat)** – résumé en 3–6 puces (voir §12)
6. **Set** – mapping vers colonnes Sheets (NOTES = sortie IA)
7. **Aggregate All (web)** – rassemblement des items web enrichis

---

## 4) Ingestion Instagram (Apify + Vision)

### Étapes
1. **HTTP Request – Apify Run (POST)** – `instagram-post-scraper` (params: profils/hashtags, `resultsLimit`)
2. **Function – Normalize IG** → `{platform:'instagram', date, url, brand, caption, mediaUrl}`
3. **Split In Batches (BATCH_SOCIAL)**
4. **HTTP Request (GET) – Download media** – récupère binaire `mediaUrl`
5. **Move Binary Data – to JSON (base64)** – produit `mediaBase64` + `mimeType`
6. **HTTP Request – Gemini 1.5 Pro Vision** – `generateContent` avec `inlineData` (voir §12)
7. **Set** – mapping vers colonnes Sheets (`DESCRIPTION` vide, `NOTES` = sortie Gemini)
8. **Aggregate All (IG)**

---

## 5) Ingestion TikTok (Apify + Vision)

### Étapes
1. **HTTP Request – Apify Run (POST)** – `tiktok-scraper` (params: profils/hashtags, `maxItems`)
2. **Function – Normalize TT** → `{platform:'tiktok', date, url, brand, caption, mediaUrl}`
3. **Split In Batches (BATCH_SOCIAL)**
4. **HTTP Request (GET) – Download media**
5. **Move Binary Data – to JSON (base64)**
6. **HTTP Request – Gemini 1.5 Pro Vision** – `generateContent` avec `inlineData`
7. **Set** – mapping vers colonnes Sheets (`DESCRIPTION` vide, `NOTES` = sortie Gemini)
8. **Aggregate All (TT)**

---

## 6) Consolidation, priorisation, routage

### Étapes
1. **Merge (append)** – Web + IG + TikTok
2. **Function – Final Canonicalize + Dedupe + Sort** – par URL canonicalisée, tri date desc, limit `MAX_ITEMS_TOTAL`
3. **Google Sheets – Append Agrégateur général (1 appel)** – Range `A:F`, mapping auto
4. **Set – Config (règles)** – listes `COMPETITORS`, `INFLUENCER_HANDLES`, `TREND_KEYWORDS`
5. **Function – Classifier** – priorité: Benchmark > Spotted > Trend (voir §10)
6. **Switch** – route vers feuille correspondante
7. **Google Sheets – Append (x3)** – `Benchmark`, `Spotted`, `Trend`

---

## 7) Paramétrage explicite (placeholders à fournir)

### Variables de contenu
- `TOPIC_KEYWORDS` (string[])
- `RSS_FEEDS` (string[])
- `INSTAGRAM_PROFILES` (string[])
- `INSTAGRAM_HASHTAGS` (string[])
- `TIKTOK_PROFILES` (string[])
- `TIKTOK_HASHTAGS` (string[])

### Règles métier
- `COMPETITORS` (string[])
- `INFLUENCER_HANDLES` (string[])
- `TREND_KEYWORDS` (string[])

### Contraintes techniques
- `DATE_FORMAT` = ISO 8601; timezone `Europe/Paris`
- `BATCH_WEB` = 8; `BATCH_SOCIAL` = 4
- `MAX_ITEMS_RSS` = 25 par flux
- `MAX_ITEMS_INSTAGRAM` = 7 par exécution
- `MAX_ITEMS_TIKTOK` = 5 par profil
- `MAX_ITEMS_TOTAL` = 150
- `THROTTLE_GEMINI_MS` = 500
- `SCRAPE_PERIOD` = 7 jours glissants
- `ANALYTICS_PERIOD` = 7 jours
- `DRY_RUN` (bool)

### Preset: Tech / AI / Deeptech (exemple concret)
```json
{
  "TOPIC_KEYWORDS": [
    "ai", "artificial intelligence", "genai", "llm", "foundation model",
    "autonomous agent", "rag", "vector database", "gpu", "semiconductor",
    "quantum", "robotics", "biotech", "longevity", "fusion", "space",
    "cybersecurity", "privacy", "cryptography", "opensource", "open-science",
    "tech policy", "geopolitics", "export control", "chips act", "m&a",
    "fundraising", "ipo", "regulation", "eu ai act"
  ],
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
  "INSTAGRAM_HASHTAGS": [
    "#AI",
    "#DeepLearning", 
    "#MachineLearning",
    "#ArtificialIntelligence",
    "#GenAI",
    "#LLM",
    "#OpenAI",
    "#TechInnovation",
    "#DeepTech"
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
  ],
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
---

## 8) Normalisation & déduplication

### Canonicalisation d’URL
- Normaliser host (lowercase), supprimer `utm_*`/`fbclid`, supprimer fragment `#...`, enlever trailing slash
- Résoudre redirections si possible
- Hash d’idempotence = `sha256(canonicalUrl)`

### Déduplication
- Avant IA (par `canonicalUrl`)
- Après merge (par `LIEN DE PUBLICATION`)
- Inter‑exécutions: ignorer URLs déjà présentes dans `Agrégateur général` (lecture colonne C)

---

## 9) Écriture Google Sheets — contrat strict

- Création des 4 tabs si absents
- Headers forcés `A1:F1`:
  `DATE | MARQUE | LIEN DE PUBLICATION | CAPTION | DESCRIPTION | NOTES`
- Nettoyage `A2:F400` au démarrage
- Append idempotent: ne pas écrire si URL déjà présente
- Mapping colonnes:
  - `DATE`: ISO 8601
  - `MARQUE`: handle/nom normalisé
  - `LIEN DE PUBLICATION`: `canonicalUrl`
  - `CAPTION`: court texte source
  - `DESCRIPTION`: extrait (RSS) | vide (IG/TT)
  - `NOTES`: sortie IA

---

## 10) Classification — règles déterministes

Priorité de bucket:
1. **Benchmark** si `MARQUE` ∈ `COMPETITORS`
2. **Spotted** si auteur ∈ `INFLUENCER_HANDLES`
3. **Trend** si `platform` ∈ {instagram, tiktok} OU (`CAPTION`|`NOTES`) contient un terme de `TREND_KEYWORDS`
4. Sinon → **Spotted**

Sortie fonction: `{ bucket: 'Benchmark'|'Spotted'|'Trend', confidence: 0..1 }`

---

## 11) Robustesse, coûts & observabilité

- Ratelimit: `Wait` entre lots Vision (`THROTTLE_GEMINI_MS`); OpenAI temp=0.6–0.7
- Retry: exponentiel x3 sur 429/5xx (Gemini/Apify)
- On‑Error: workflow dédié (Slack/Email) avec payload: nœud, message, entrée fautive
- Logs optionnels: sheet `Logs` (timestamp, node, event, url, status, error?)
- Caps coûts: limites par branche (web/social) et limite globale `MAX_ITEMS_TOTAL`

---

## 12) Prompts IA

### Analyse RSS/Web (OpenAI)
```
Tu es analyste "trendwatch" tech/AI. Résume l'article suivant en 3–6 puces concises :
- acteur/entreprise principale
- innovation/annonce/développement  
- impact/collaboration(s)
- insight(s) / signaux faibles tech
- pourquoi c'est pertinent pour la veille tech (1 phrase)

Titre: {{$json.title}}
Contenu: {{$json.description}}
URL: {{$json.url}}
```

### Analyse Instagram/TikTok (Gemini Vision)
```
Analyse ce contenu tech/AI pour un tableau trendwatch (3–6 puces) :
- marque/créateur
- type de contenu/format
- message/innovation présentée
- audience/engagement
- signaux faibles detectés
- pertinence pour veille tech (1 phrase)

Caption: {{$json.caption}}
```

### Appel Gemini Vision (corps JSON — inlineData requis)
```
{
  "contents": [{
    "parts": [
      {"text": "Analyse ce post pour un tableau trendwatch (3–6 puces)...\nCaption: {{$json.caption}}"},
      {"inlineData": {"mimeType": "={{$json.mimeType || 'image/jpeg'}}", "data": "={{$json.mediaBase64}}"}}
    ]
  }],
  "generationConfig": {"temperature": 0.7}
}
```

---

## 13) Consignes de positions (exemples indicatifs)

> Ces positions sont données à titre de guide pour Claude afin de produire un graphe propre. Elles peuvent être ajustées, mais doivent respecter l’ordre logique par colonnes.

- `[Init] Cron` (250, 280) → `Create Tabs` (420, 280) → `Clear Sheets` (620, 280) → `Set Headers` (820, 280)
- Branche **RSS** (y≈160–520): `RSS List/Read` (900–1100, 180–220) → `Normalize` (1350, 200) → `Filter+Dedup` (1550, 200) → `Split` (1750, 200) → `OpenAI` (1950, 200) → `Set Map` (2150, 200) → `Aggregate Web` (2450, 200)
- Branche **IG** (y≈360–720): `Apify IG` (1150, 400) → `Normalize` (1350, 400) → `Split` (1550, 400) → `Download` (1750, 400) → `Base64` (1950, 400) → `Gemini` (2150, 400) → `Set Map` (2350, 400) → `Aggregate IG` (2550, 400)
- Branche **TT** (y≈560–920): `Apify TT` (1150, 600) → `Normalize` (1350, 600) → `Split` (1550, 600) → `Download` (1750, 600) → `Base64` (1950, 600) → `Gemini` (2150, 600) → `Set Map` (2350, 600) → `Aggregate TT` (2550, 600)
- `[Merge] All Sources` (2850, 400) → `Final Dedupe+Sort` (3050, 400) → `Append Agrégateur` (3250, 400)
- `[Route] Classifier` (3450, 400) → `Append Benchmark` (3650, 320) | `Append Spotted` (3650, 420) | `Append Trend` (3650, 520)

---

## 14) Prompt « Claude → JSON n8n » (strict)

```
Tu es chargé de produire un workflow n8n complet, importable, suivant ce cahier des charges (sections 0→13). Contraintes STRICTES:
- Réponds UNIQUEMENT par un JSON valide, top‑level: name, nodes, connections, settings, tags?, triggerCount?, versionId?, updatedAt?.
- Chaque nœud spécifie: id unique, name, type (ex: "n8n-nodes-base.httpRequest"), typeVersion, parameters, position [x,y].
- Utilise les variables d’env ($env.GOOGLE_AI_API_KEY, $env.APIFY_TOKEN, $env.SPREADSHEET_ID, etc.).
- Implémente toutes les branches: Init Sheets, RSS+OpenAI, Instagram+Vision (download+base64+inlineData), TikTok+Vision, Merge, Dédup final, Append Agrégateur, Classifier+Append 3 tabs.
- Respecte les colonnes Google Sheets et l’idempotence (dédup par URL canonicalisée) comme défini.
- Ajoute les Wait/Retry/Batch nécessaires (THROTTLE_GEMINI_MS, BATCH_WEB, BATCH_SOCIAL).
- Place les nodes selon les colonnes/positions indicatives (§1 et §13) pour un graphe lisible.
- Interdis texte hors JSON.
```

---

## 15) Post‑import checklist (à faire une fois le JSON importé)

1. Créer/valider les Credentials n8n
   - Google Sheets OAuth2 (`GOOGLESHEETS_OAUTH`) — vérifier le compte et les scopes
   - OpenAI (`OPENAI_API_KEY`)
   - Google AI Studio (`GOOGLE_AI_API_KEY`)
   - Apify (`APIFY_TOKEN`)
   - Slack (si on active l’alerte) — incoming webhook ou OAuth app
2. Variables d’environnement (n8n Settings → Variables)
   - `SPREADSHEET_ID`, `TIMEZONE`
   - Listes: `RSS_FEEDS`, `INSTAGRAM_PROFILES`, `INSTAGRAM_HASHTAGS`, `TIKTOK_PROFILES`, `TIKTOK_HASHTAGS`
   - Règles: `COMPETITORS`, `INFLUENCER_HANDLES`, `TREND_KEYWORDS`
   - Limites: `BATCH_WEB`, `BATCH_SOCIAL`, `MAX_ITEMS_WEB`, `MAX_ITEMS_TOTAL`, `THROTTLE_GEMINI_MS`
3. Google Sheet
   - Créer un spreadsheet avec onglets: `Agrégateur général`, `Benchmark`, `Spotted`, `Trend`
   - Récupérer l’ID et le mettre dans `SPREADSHEET_ID`
   - Partager le fichier avec le compte OAuth utilisé par n8n
4. Tests de connectivité
   - Lancer les branches RSS/IG/TT en mode “Run Once” (petit échantillon)
   - Vérifier: dates ISO, URL canonicalisées, headers présents, append OK
5. Observabilité
   - Activer le workflow d’erreur (Slack/Email) si présent
   - Option: ajouter une sheet `Logs` si besoin
6. Coûts & quotas
   - Régler `BATCH_*` et `THROTTLE_GEMINI_MS` selon ton quota actuel
   - Ajuster `MAX_ITEMS_*` pour plafonner les coûts

---

## 16) Clarifications techniques & conformité

- Google Sheets
  - Scopes recommandés: `spreadsheets`, `drive.file` (création/écriture fichier possédé par l’app)
  - Timezone: vérifier que n8n et le spreadsheet sont en `Europe/Paris`
- Apify
  - Utiliser des actors maintenus (IDs et versions stables); renseigner input: profils/hashtags, `maxItems`, proxy (si requis)
  - Contenu privé/supprimé: fallback texte‑only si download échoue
- OpenAI / Gemini
  - OpenAI: choisir le modèle (ex: `gpt-4o-mini`), `temperature` 0.6–0.7, limites tokens
  - Gemini Vision: taille base64 ≲ 20 Mo; fournir `mimeType` exact; retry exponentiel sur 429/5xx
- Slack (optionnel)
  - Préparer un Incoming Webhook ou une app OAuth; canal des alertes défini
- Sécurité
  - Stocker les clés en Credentials n8n (non en clair); limiter l’accès par rôle
  - Respect des ToS/lois locales du scraping; filtrer données personnelles si besoin
- Exploitation
  - `DRY_RUN` pour pré‑prod; sauvegarde hebdo du workflow JSON et du Sheet
  - Cron: valider l’heure effective après import (décalage DST)
