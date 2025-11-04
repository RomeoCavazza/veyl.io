# Guide de Nettoyage des Déploiements

## Problème identifié
- 1000+ déploiements sur Railway/Vercel causés par des intégrations GitHub automatiques
- Chaque commit déclenchait un déploiement automatique

## Solutions implémentées

### 1. Optimisation CI/CD GitHub Actions ✅
- Filtrage par chemins (paths) pour ne déployer que sur changements de code source
- Exclusion des fichiers de documentation (docs/, README.md, *.md)
- Vérification conditionnelle avant déploiement

### 2. Actions à effectuer manuellement

#### Railway - Désactiver Auto-Deploy depuis GitHub

1. **Aller sur Railway Dashboard**
   - https://railway.app/dashboard
   - Sélectionner le projet `insidr-production`

2. **Désactiver GitHub Integration**
   - Settings → Source → GitHub
   - Désactiver "Auto Deploy" ou "Continuous Deployment"
   - Garder uniquement le déploiement via GitHub Actions (workflow CI/CD)

3. **Alternative : Utiliser uniquement Railway CLI**
   - Si vous voulez garder Railway mais sans auto-deploy
   - Utiliser `railway up` manuellement ou via GitHub Actions uniquement

#### Vercel - Désactiver Auto-Deploy depuis GitHub

1. **Aller sur Vercel Dashboard**
   - https://vercel.com/dashboard
   - Sélectionner le projet `veyl.io` ou `insidr`

2. **Désactiver GitHub Integration**
   - Settings → Git → GitHub
   - Désactiver "Automatic deployments from Git"
   - Ou configurer pour ne déployer que sur certains branches/tags

3. **Alternative : Ignorer certains commits**
   - Utiliser `[skip deploy]` dans le message de commit
   - Ou configurer les paths dans Vercel settings

### 3. Nettoyer l'historique des déploiements (optionnel)

**⚠️ ATTENTION : Ne peut pas supprimer l'historique GitHub des commits**

Les déploiements sont liés à l'historique Git. Pour "nettoyer" :

1. **Railway** : Pas possible de supprimer l'historique des déploiements
   - Les déploiements restent dans l'historique
   - Mais les futurs déploiements seront réduits de 80-90%

2. **Vercel** : Peut supprimer les déploiements individuels
   - Dashboard → Deployments → Supprimer les anciens déploiements
   - Mais ça ne change pas le compteur total

3. **GitHub** : Nettoyer l'historique Git (RISQUÉ)
   - Utiliser `git rebase -i` ou `git filter-branch`
   - ⚠️ **DANGEREUX** : Peut casser les intégrations
   - ⚠️ **RECOMMANDÉ** : Ne pas le faire si d'autres personnes utilisent le repo

### 4. Configuration recommandée

**Workflow optimal :**
- ✅ GitHub Actions gère les déploiements (avec filtrage par paths)
- ❌ Désactiver les intégrations GitHub directes Railway/Vercel
- ✅ Déploiements uniquement sur changements de code source
- ✅ Déploiements manuels possibles via `workflow_dispatch`

## Résultat attendu

- **Réduction de 80-90%** des déploiements futurs
- Déploiements uniquement sur changements réels de code
- Meilleure sécurité et contrôle
- Réduction des coûts et de la surface d'attaque

## Commandes utiles

```bash
# Vérifier les intégrations GitHub
gh repo view --json url

# Vérifier les workflows GitHub Actions
gh workflow list

# Voir les déploiements récents
gh run list --limit 10
```

