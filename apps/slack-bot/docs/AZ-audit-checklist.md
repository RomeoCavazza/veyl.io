# 🔍 A-Z Audit Checklist - Revolvr Bot

**Pense-bête ultime** pour audit complet du projet. Chaque lettre = feature critique à surveiller.

## A) Hygiène Git & contexte repo → `current-state.md`

**Pourquoi** : Savoir ce qu'on audite et d'où on part.

```bash
git rev-parse --is-inside-work-tree
git status -sb
git remote -v
git branch -vv
git log --oneline -n 10
git tag --list --sort=-creatordate | head -n 10
```

**Relever** : Branches divergentes, commits récents, tags.
**Red flags** : Travail non commité massif, branches orphelines.
**DoD** : Repo propre, historique clair, branches à jour.

## B) Secrets/jetons & infos sensibles → `security-legal.md`

**Pourquoi** : Fuite de clés = risque majeur.

```bash
git grep -nE '(OPENAI|SLACK|GOOGLE|GSUITE|API|TOKEN|KEY|SECRET|PASSWORD|PRIVATE_KEY|BEARER)' -- ':!*.md' ':!*.png' ':!*.jpg'
gitleaks detect --no-banner || true
```

**Relever** : Chemins/ligne; vérifier .env*, config.py, YAML/JSON.
**Red flags** : Clés en dur, tokens sous tests/fixtures.
**DoD** : Aucun secret exposé, gestion centralisée.

## C) Inventaire fichiers & taille → `current-state.md` (+ lien diag dans `system-architecture.md`)

**Pourquoi** : Cartographier rapidement.

```bash
tree -L 2 -I ".git|.venv|__pycache__|*.egg-info|node_modules|dist|build|coverage|.mypy_cache|.pytest_cache"
find . -type f -size +5M
```

**Relever** : Gros dossiers, binaires, artefacts.
**Red flags** : Binaires/archives en repo, node_modules commité.
**DoD** : Arbo claire, pas d'artefacts volumineux.

## D) Points d'entrée (API/CLI/Slack/Jobs) → `current-state.md`

**Pourquoi** : Savoir ce qui démarre quoi.

```bash
rg -n "uvicorn|FastAPI|APIRouter|@app\\.(get|post|put|delete)|Fastify" -S
rg -n "if __name__ == .__main__." -S
rg -n "argparse|click|typer" -S
rg -n "slack_sdk|SocketModeClient|RTMClient" -S bot/ || true
rg -n "(Celery|RQ|APScheduler|cron)" -S || true
```

**Relever** : Fichiers/ligne pour chaque entrypoint (API routes, CLI cmds, Slack events, jobs).
**DoD** : Tous les entrypoints identifiés et testables.

## E) Dépendances Python & Node → `dependencies-supply-chain.md`

**Pourquoi** : Surface d'attaque, dette technique.

```bash
python3 -m venv .venv && source .venv/bin/activate || true
pip install -r requirements*.txt || true
pip freeze > .audit_pip_freeze.txt || true
pipdeptree > .audit_dep_tree.txt || true

npm ci --ignore-scripts || true
npm ls --all --json > .audit_npm_tree.json || true

# Libs non utilisées (Node)
npx depcheck || true
# Exports non utilisés (TS)
npx ts-prune || true
```

**Relever** : Doublons, libs non utilisées, scripts postinstall suspects.
**DoD** : `requirements-min.txt` (~15 paquets), versions verrouillées/hashes.

## F) SBOM & vulnérabilités supply-chain → `dependencies-supply-chain.md` + `security-legal.md`

**Pourquoi** : Conformité + CVE.

```bash
syft . -o cyclonedx-json > sbom.json || true
pip-audit || true
npm audit --audit-level=high || true
trivy fs . || true
# Si image Docker:
# docker build -t revolvr:ci .
# trivy image revolvr:ci
```

**Relever** : High/Med/Low, paquets impactés, CVE.
**DoD** : Plan de MAJ, allowlist/denylist validés, SBOM à jour.

## G) Qualité code (lint/type/format) → `current-state.md`

**Pourquoi** : Dettes & cohérence.

```bash
ruff check . || true
mypy . --ignore-missing-imports || true
black --check . || true

# Front
npx eslint . || true
tsc --noEmit --strict || true
```

**Relever** : Violations majeures, modules fautifs.
**DoD** : Code passant lint/type/format, gate CI activé.

## H) Complexité, duplication, dead code → `current-state.md`

**Pourquoi** : Hotspots à refactor.

```bash
radon cc -s -a . > .audit_radon.txt || true
radon mi . > .audit_mi.txt || true
vulture . > .audit_deadcode.txt || true
# Node - cycles imports
npx madge --circular src || true
```

**Relever** : Fichiers >500L, fonctions CC>10, modules faible MI, cycles.
**DoD** : Plan ≤10 commits de refactoring, complexité maîtrisée.

## I) Tests, flakiness & couverture → `current-state.md`

**Pourquoi** : Sécurité de refactor.

```bash
pytest -q || pytest -q -k smoke || true
pytest -q --durations=20 || true
coverage run -m pytest || true
coverage report -m || true
# Front (si présent)
npm test -- --watchAll=false || true
```

**Relever** : Tests lents, zones peu couvertes, E2E manquants.
**DoD** : 80% couverture, tests verts, 3 smoke tests MVP.

## J) API snapshot & conformité → `api-snapshot.md`

**Pourquoi** : Contrat unique et vérifié.

```bash
rg -n "@app\\.(get|post|put|delete)|@router\\." -S api/ || true
# Démarrer l'API localement si possible, puis :
curl -s http://127.0.0.1:8001/openapi.json > openapi.json || true
schemathesis run http://127.0.0.1:8001/openapi.json -c all > .audit_schemathesis.txt || true
```

**Relever** : Routes, schémas, erreurs Schemathesis.
**DoD** : OpenAPI YAML unique, schémas validés, endpoints testables.

## K) Modèle de données & migrations → `data-model-lineage.md`

**Pourquoi** : Cohérence stockage/flux.

```bash
rg -n "SQLModel|sqlalchemy|alembic|Base\\(" -S
alembic current || true
alembic history | tail -n 10 || true
```

**Relever** : Tables, contraintes, indexes, horodatage UTC.
**DoD** : Modèles cohérents, migrations à jour, ERD clair.

## L) Flux scraping & pipelines → `current-state.md` (+ interface dans `system-architecture.md`)

**Pourquoi** : Stabilité & légalité.

```bash
rg -n "playwright|selenium|bs4|requests|httpx" -S
rg -n "captcha|proxy|stealth|user-agent|headless" -S
rg -n "hashtag|engagement|metadata|parse" -S
```

**Relever** : Input/output, anti-bot, fréquence, statut.
**DoD** : `ScraperAdapter` fonctionnel, pipelines stables.

## M) Sécurité applicative (code patterns) → `security-legal.md`

**Pourquoi** : Vulnérabilités fréquentes.

```bash
# Python
rg -n "eval\\(|exec\\(|pickle\\.load|yaml\\.load\\(|subprocess\\.(Popen|run|call)|requests\\.[gs]et\\(|verify=False|ssl._create_unverified_context" -S
rg -n "open\\(.+\\,\\s*['\"](w|a)" -S
rg -n "Jinja2.Environment\\(.+autoescape=False" -S
rg -n "allow_origins=.*\\*" -S

# Node
rg -n "child_process\\.(exec|execSync)|new Function\\(|eval\\(|fs\\.(write|append)FileSync|res\\.send\\(.+\\+ .*\\)" -S
```

**Relever** : Lignes à risque (RCE/SSRF/path traversal/CSRF/CORS).
**DoD** : Patterns dangereux éliminés, sécurisés appliqués.

## N) Auth, rate-limit, RBAC, CORS → `security-legal.md`

**Pourquoi** : Périmètre et abus.

```bash
rg -n "Depends\\(|OAuth2|JWT|APIKey|Session" -S api/
rg -n "rate|limiter|slowapi|throttle" -S
rg -n "CORS|CORSMiddleware|allow_origins" -S
```

**Relever** : Endpoints publics, limites manquantes, CORS "*".
**DoD** : Auth implémenté, rate-limit actif, CORS whitelist.

## O) Config & feature flags → `current-state.md`

**Pourquoi** : Variabilité & secrets.

```bash
rg -n "dotenv|os\\.environ|getenv|pydantic\\.Settings" -S
rg -n "FeatureFlag|Unleash|ConfigCat|flipper" -S || true
```

**Relever** : Paramétrage par env, flags critiques; mode DEMO activable.
**DoD** : Configuration externalisée, feature flags pour déploiement.

## P) Observabilité (logs/traces/metrics) → `ops-deploy.md`

**Pourquoi** : Diagnostiquer prod.

```bash
rg -n "logging\\.|structlog|Loguru|logger\\." -S
rg -n "opentelemetry|OTEL" -S
rg -n "prometheus_client|Histogram|Counter|Gauge" -S
```

**Relever** : Logs JSON, traceIDs, métriques latence/erreurs/queues.
**DoD** : OTel middlewares, Prom metrics, SLO définis.

## Q) Docker & images → `ops-deploy.md`

**Pourquoi** : Reproductibilité & sécurité.

```bash
rg -n "FROM\\s+python|node|alpine|slim" -S Dockerfile*
docker build -t revolvr:ci . || true
trivy image revolvr:ci || true
```

**Relever** : Base slim, user non-root, no cache, pins OS.
**DoD** : Multi-stage, USER 10001, PIP_NO_CACHE_DIR=1, image durcie.

## R) CI/CD (gates) → `ops-deploy.md`

**Pourquoi** : Empêcher régressions en PR.

```bash
rg -n "name:|on:|jobs:" -S .github/workflows || true
```

**Relever** : Étapes présentes (lint/tests/scans/sbom/build/deploy).
**DoD** : Gates bloquants actifs, déploiement automatisé.

## S) Front React/TS (sanity) → `current-state.md`

**Pourquoi** : Qualité UI/UX et dette.

```bash
rg -n "useEffect\\(.+\\)\\s*{[^}]*setState" -S frontend/ || true
npx eslint . || true
tsc --noEmit --strict || true
npx madge --circular src || true
```

**Relever** : Hooks suspects, cycles, erreurs TS strict.
**DoD** : Code TS strict, pas de cycles, hooks propres.

## T) LLM usage & guardrails → `ai-llm-strategy.md`

**Pourquoi** : Anti-hallucinations et coût.

```bash
rg -n "openai|anthropic|gpt|claude|llm|prompt" -S
rg -n "jsonschema|pydantic\\s*model|TypedDict" -S
```

**Relever** : Sorties contraintes JSON, RAG (vector DB), allowlist.
**DoD** : Guardrails actifs, coûts trackés, pas d'hallucinations.

## U) Vector DB & RAG → `ai-llm-strategy.md` + `system-architecture.md`

**Pourquoi** : Pertinence & coût.

```bash
rg -n "pgvector|weaviate|chroma|faiss" -S || true
rg -n "chunk|embed|similarity|cosine|BM25" -S || true
```

**Relever** : Indexation, tailles chunk, sources; politiques TTL.
**DoD** : RAG fonctionnel, embeddings optimisés.

## V) Legal & RGPD, ToS scraping → `security-legal.md`

**Pourquoi** : Conformité.

**Relever** : Données personnelles touchées, finalités, minimisation, TTL, opt-out.
**DoD** : DPIA court, mentions légales, DPA, Mode DEMO/PROD distingué.

## W) Slack/GSuite APIs → `current-state.md` + `security-legal.md`

**Pourquoi** : Périmètre des intégrations.

```bash
rg -n "slack_sdk|googleapiclient|gmail|sheets|drive" -S
```

**Relever** : Scopes OAuth, stockage tokens, masquage logs.
**DoD** : Scopes restreints, tokens sécurisés, rotation.

## X) Extraction MVP Insighter → `current-state.md` + `system-architecture.md`

**Pourquoi** : Livrer vite.

**Relever** : Arbo cible, endpoints /competitors, /posts, /summary, SQLite, scraper Instagram stub, 3 smoke tests.
**DoD** : API up, tests verts, OpenAPI ok, scraper stub fonctionnel.

## Y) Packaging & README → `index.md`

**Pourquoi** : Utilisable par d'autres.

```bash
rg -n "^#|Install|Usage|Endpoints|Run" -S README* || true
```

**Relever** : Instructions datées/erronées.
**DoD** : README MVP + pointeurs vers /docs/.

## Z) Hotspots "à surveiller en continu" → `index.md`

**Watch list** :
- Secrets & tokens exposés
- Scrapers cassés (sélecteurs, captchas)
- Vulnérabilités High (pip-audit/npm audit/trivy)
- Endpoints sans validation/rate-limit
- Jobs/background en échec
- Coûts LLM (explosion tokens)
- Latence 95e API > 2s
- Couverture tests < 80%
- CORS/CSP relâchés
- Dépendances nouvelles non-allowlistées

---

## 📦 Mini "packs de commande" prêts à coller

### Pack Python qualité
```bash
ruff check . && mypy . --ignore-missing-imports && black --check .
radon cc -s -a . && vulture .
pytest -q --durations=20 && coverage run -m pytest && coverage report -m
```

### Pack sécurité
```bash
bandit -r . -q
gitleaks detect --no-banner
pip-audit
npm audit --audit-level=high
syft . -o cyclonedx-json > sbom.json
trivy fs .
```

### Pack API
```bash
rg -n "@app\\.(get|post|put|delete)|@router\\." -S api/
curl -s http://127.0.0.1:8001/openapi.json > openapi.json
schemathesis run http://127.0.0.1:8001/openapi.json -c all
```

### Pack scrapers
```bash
rg -n "playwright|selenium|bs4|requests|httpx|captcha|proxy|stealth|user-agent|headless|hashtag|engagement|metadata|parse" -S
```

---

## 🗺️ Mapping "résultats → fichiers"

- `index.md` : Résumé global + DoD MVP + Z "watch list"
- `current-state.md` : A, C, D, E(context), G, H, I, L, O, S, W, X(résumé)
- `product-vision-roadmap.md` : Objectifs & étapes (sans commandes)
- `system-architecture.md` : B(diag), D(entrypoints), L(interfaces), U(RAG), X(cible)
- `data-model-lineage.md` : K, L(flux), contraintes, TTL
- `api-snapshot.md` : J, K(schemathesis), OpenAPI unique
- `security-legal.md` : B, F, M, N, P(sécu), V, W(scopes), SBOM/CVE High
- `dependencies-supply-chain.md` : E, F, politiques pins & allowlist
- `ops-deploy.md` : P(obs détaillée), Q, R(CI/CD), déploiements
- `ai-llm-strategy.md` : T, U, guardrails/coûts

---

**Utilisation** : Cocher chaque lettre au fur et à mesure, ranger résultats dans fichiers appropriés, mettre à jour régulièrement.