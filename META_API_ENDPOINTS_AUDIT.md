# Audit des Endpoints Meta API - Vérification App Review

## 📋 Objectif
Vérifier que chaque route API Meta est :
1. ✅ **Connectée réellement à Meta API** (via `call_meta()`, pas de mock data)
2. ✅ **A un Call-To-Action (CTA) dans le frontend** (bouton, action utilisateur)
3. ✅ **Mappée à l'ordre de la vidéo de démonstration**

---

## 🎬 Ordre de la Vidéo de Démonstration

1. **Landing Page** → Pas d'endpoint Meta
2. **OAuth** → `pages_show_list` (implicite)
3. **My Profile** → `instagram_business_basic`
4. **Search + oEmbed** → `Instagram Public Content Access`, `Meta oEmbed Read`
5. **My Projects** → `Instagram Public Content Access`, `Meta oEmbed Read`
6. **Creators** → `instagram_business_basic`, `instagram_basic`
7. **Analytics** → `instagram_business_manage_insights`, `read_insights`, `pages_read_user_content`

---

## 🔍 Détail par Endpoint

### 1. ✅ GET `/api/v1/meta/oembed` (authentifié)

**Permission:** `Meta oEmbed Read` ❌ REJETÉE

**Backend:**
- **Fichier:** `apps/backend/meta/meta_endpoints.py` (ligne 276)
- **Appelle Meta API:** ✅ OUI - `call_meta()` ligne 184
- **Mock data:** ❌ NON
- **APP REVIEW NOTES:** ✅ OUI (lignes 285-289)

**Frontend:**
- **Fonction API:** `fetchMetaOEmbed()` dans `apps/frontend/src/lib/api.ts` (ligne 153)
- **CTA:** ✅ OUI
  - **Page:** `/search` - Bouton "Embed" sur chaque post Instagram
  - **Composant:** `EmbedDialog.tsx` (ligne 48)
  - **Action:** Clic sur bouton "Embed" → Ouvre dialog → Appelle `fetchMetaOEmbed()`

**Ordre vidéo:** 4. Search + oEmbed

**Status:** ✅ **PRÊT**

---

### 2. ✅ GET `/api/v1/meta/oembed/public` (public)

**Permission:** `Meta oEmbed Read` ❌ REJETÉE

**Backend:**
- **Fichier:** `apps/backend/meta/meta_endpoints.py` (ligne 299)
- **Appelle Meta API:** ✅ OUI - `call_meta()` ligne 184 (via `_fetch_oembed_with_tokens`)
- **Mock data:** ❌ NON
- **APP REVIEW NOTES:** ✅ OUI (héritées de `_fetch_oembed_with_tokens`)

**Frontend:**
- **Fonction API:** `fetchMetaOEmbed()` dans `apps/frontend/src/lib/api.ts` (ligne 168)
- **CTA:** ✅ OUI
  - **Page:** `/demo/oembed` - Page de démonstration publique
  - **Composant:** `OEmbedDemo.tsx` (ligne 42)
  - **Action:** Entrer URL Instagram → Clic "Fetch oEmbed" → Appelle `/oembed/public`

**Ordre vidéo:** 4. Search + oEmbed (démo publique)

**Status:** ✅ **PRÊT**

---

### 3. ✅ GET `/api/v1/meta/ig-public`

**Permission:** `Instagram Public Content Access` ✅ APPROUVÉE

**Backend:**
- **Fichier:** `apps/backend/meta/meta_endpoints.py` (ligne 317)
- **Appelle Meta API:** ✅ OUI - `call_meta()` lignes 346, 357
- **Mock data:** ❌ NON (fallback DB uniquement si Meta API échoue)
- **APP REVIEW NOTES:** ✅ OUI (lignes 325-331)

**Frontend:**
- **Fonction API:** `fetchMetaIGPublic()` dans `apps/frontend/src/lib/api.ts` (ligne 112)
- **CTA:** ✅ OUI
  - **Page:** `/search` - Recherche par hashtag (ligne 152)
  - **Page:** `/projects/:id` - Bouton "Fetch" dans MyProjects (ligne 184)
  - **Action:** 
    - Search: Rechercher hashtag → Appelle automatiquement `fetchMetaIGPublic()`
    - MyProjects: Clic "Fetch" → Appelle `fetchMetaIGPublic()` pour chaque hashtag

**Ordre vidéo:** 4. Search + oEmbed, 5. My Projects

**Status:** ✅ **PRÊT**

---

### 4. ✅ GET `/api/v1/meta/ig-hashtag`

**Permission:** `Instagram Public Content Access` ✅ APPROUVÉE (alias)

**Backend:**
- **Fichier:** `apps/backend/meta/meta_endpoints.py` (ligne 495)
- **Appelle Meta API:** ✅ OUI - Alias de `/ig-public` (ligne 503)
- **Mock data:** ❌ NON

**Frontend:**
- **Fonction API:** `searchPosts()` dans `apps/frontend/src/lib/api.ts` (ligne 99)
- **CTA:** ✅ OUI (utilisé par `searchPosts()`)

**Ordre vidéo:** 4. Search + oEmbed

**Status:** ✅ **PRÊT**

---

### 5. ✅ GET `/api/v1/meta/page-public`

**Permission:** `pages_read_user_content` ❌ REJETÉE

**Backend:**
- **Fichier:** `apps/backend/meta/meta_endpoints.py` (ligne 506)
- **Appelle Meta API:** ✅ OUI - `call_meta()` ligne 533
- **Mock data:** ❌ NON
- **APP REVIEW NOTES:** ✅ OUI (lignes 515-521)

**Frontend:**
- **Fonction API:** `fetchPagePublicPosts()` dans `apps/frontend/src/lib/api.ts` (ligne 214)
- **CTA:** ✅ OUI
  - **Page:** `/analytics` - Tab "Pages" (ligne 95)
  - **Composant:** `Analytics.tsx` (ligne 83-113)
  - **Action:** Entrer Facebook Page ID → Clic "Fetch Page Posts" → Appelle `fetchPagePublicPosts()`

**Ordre vidéo:** 7. Analytics

**Status:** ✅ **PRÊT**

---

### 6. ✅ GET `/api/v1/meta/insights`

**Permissions:** 
- `instagram_business_manage_insights` ❌ REJETÉE
- `read_insights` ❌ REJETÉE
- `instagram_manage_insights` ❌ REJETÉE (alias)

**Backend:**
- **Fichier:** `apps/backend/meta/meta_endpoints.py` (ligne 653)
- **Appelle Meta API:** ✅ OUI - `call_meta()` ligne 716
- **Mock data:** ❌ NON
- **APP REVIEW NOTES:** ✅ OUI (lignes 661-667)

**Frontend:**
- **Fonction API:** `fetchMetaInsights()` dans `apps/frontend/src/lib/api.ts` (ligne 244)
- **CTA:** ✅ OUI
  - **Page:** `/analytics` - Tab "Instagram" (ligne 63)
  - **Composant:** `InstagramInsights.tsx` (ligne 34)
  - **Composant:** `Analytics.tsx` (ligne 57-81)
  - **Action:** 
    - Analytics: Entrer resource_id → Clic "Fetch Insights" → Appelle `fetchMetaInsights()`
    - InstagramInsights: Chargement automatique avec `resource_id=me` (ligne 34)

**Ordre vidéo:** 7. Analytics

**Status:** ✅ **PRÊT**

---

### 7. ✅ GET `/api/v1/meta/ig-business-profile`

**Permission:** `instagram_business_basic` ❌ REJETÉE

**Backend:**
- **Fichier:** `apps/backend/meta/meta_endpoints.py` (ligne 774)
- **Appelle Meta API:** ✅ OUI - `call_meta()` ligne 830
- **Mock data:** ❌ NON
- **APP REVIEW NOTES:** ✅ OUI (lignes 782-788)

**Frontend:**
- **Fonction API:** `fetchInstagramBusinessProfile()` dans `apps/frontend/src/lib/api.ts` (ligne 275)
- **CTA:** ✅ OUI
  - **Page:** `/profile` - Chargement automatique (ligne 45)
  - **Page:** `/projects/:id/creator/:username` - Chargement automatique (ligne 192)
  - **Action:** 
    - Profile: Connexion OAuth → Affichage automatique du profil Instagram Business
    - CreatorDetail: Navigation vers page créateur → Appelle `fetchInstagramBusinessProfile('me')`

**Ordre vidéo:** 3. My Profile, 6. Creators

**Status:** ✅ **PRÊT**

---

### 8. ⚠️ GET `/api/v1/meta/ig-profile`

**Permission:** `instagram_basic` ❌ REJETÉE

**Backend:**
- **Fichier:** `apps/backend/meta/meta_endpoints.py` (ligne 872)
- **Appelle Meta API:** ✅ OUI - `call_meta()` ligne 910
- **Mock data:** ❌ NON
- **APP REVIEW NOTES:** ✅ OUI (lignes 884-888)

**Frontend:**
- **Fonction API:** ❌ **MANQUANTE** - Pas de fonction dans `api.ts`
- **CTA:** ❌ **MANQUANT** - Pas d'utilisation dans le frontend
- **Action:** ❌ **À IMPLÉMENTER**

**Ordre vidéo:** 6. Creators (pour les comptes personnels Instagram)

**Status:** ⚠️ **ENDPOINT BACKEND PRÊT, MAIS PAS UTILISÉ DANS LE FRONTEND**

**Recommandation:** 
- Ajouter `fetchInstagramProfile()` dans `api.ts`
- Utiliser dans `CreatorDetail.tsx` comme fallback si `fetchInstagramBusinessProfile()` échoue

---

### 9. ✅ POST `/api/v1/meta/link-posts-to-hashtag`

**Permission:** Aucune (utilitaire interne)

**Backend:**
- **Fichier:** `apps/backend/meta/meta_endpoints.py` (ligne 961)
- **Appelle Meta API:** ❌ NON (utilitaire DB uniquement)
- **Mock data:** ❌ NON

**Frontend:**
- **Fonction API:** N/A (utilitaire backend)
- **CTA:** N/A

**Ordre vidéo:** N/A (utilitaire interne)

**Status:** ✅ **OK** (utilitaire interne, pas pour App Review)

---

## 📊 Résumé

### Endpoints pour App Review (8)

| Endpoint | Permission | Backend Meta API | Frontend CTA | Status |
|----------|-----------|------------------|--------------|--------|
| `/oembed` | Meta oEmbed Read | ✅ | ✅ | ✅ PRÊT |
| `/oembed/public` | Meta oEmbed Read | ✅ | ✅ | ✅ PRÊT |
| `/ig-public` | Instagram Public Content Access | ✅ | ✅ | ✅ PRÊT |
| `/ig-hashtag` | Instagram Public Content Access | ✅ | ✅ | ✅ PRÊT |
| `/page-public` | pages_read_user_content | ✅ | ✅ | ✅ PRÊT |
| `/insights` | instagram_business_manage_insights, read_insights | ✅ | ✅ | ✅ PRÊT |
| `/ig-business-profile` | instagram_business_basic | ✅ | ✅ | ✅ PRÊT |
| `/ig-profile` | instagram_basic | ✅ | ❌ | ⚠️ **MANQUE CTA** |

### Endpoints utilitaires (1)

| Endpoint | Type | Status |
|----------|------|--------|
| `/link-posts-to-hashtag` | Utilitaire DB | ✅ OK |

---

## ⚠️ Action Requise

### 1. Endpoint `/ig-profile` non utilisé dans le frontend

**Problème:** L'endpoint `/ig-profile` (permission `instagram_basic`) est implémenté dans le backend mais n'est pas utilisé dans le frontend.

**Solution:**
1. Ajouter `fetchInstagramProfile()` dans `apps/frontend/src/lib/api.ts`
2. Utiliser dans `CreatorDetail.tsx` comme fallback si `fetchInstagramBusinessProfile()` échoue (pour les comptes personnels Instagram)

**Code à ajouter dans `api.ts`:**
```typescript
export async function fetchInstagramProfile(username?: string, userId?: string): Promise<any> {
  const apiBase = getApiBase();
  const params = new URLSearchParams();
  if (username) params.set('username', username);
  if (userId) params.set('user_id', userId);
  
  const url = apiBase 
    ? `${apiBase}/api/v1/meta/ig-profile?${params.toString()}`
    : `/api/v1/meta/ig-profile?${params.toString()}`;
  
  const response = await fetch(url, {
    headers: withAuthHeaders(),
  });
  
  if (!response.ok) {
    let errorData: any = null;
    try {
      errorData = await response.json();
    } catch {
      errorData = { detail: `HTTP ${response.status}` };
    }
    
    const error = new Error(errorData?.detail?.message || errorData?.detail || `HTTP ${response.status}`);
    (error as any).status = response.status;
    (error as any).detail = errorData?.detail;
    throw error;
  }
  
  return response.json();
}
```

**Code à ajouter dans `CreatorDetail.tsx` (après ligne 208):**
```typescript
// Si fetchInstagramBusinessProfile échoue, essayer instagram_basic
if (creatorPlatform === 'instagram' && matchedCreator.creator_username) {
  try {
    const profile = await fetchInstagramBusinessProfile('me');
    // ... code existant ...
  } catch (error) {
    // Fallback: essayer instagram_basic si on a un user_id
    try {
      const { fetchInstagramProfile } = await import('@/lib/api');
      // Note: instagram_basic nécessite un user_id, pas un username
      // Pour l'instant, on utilise les données du projet
      console.warn('Instagram Business profile not available, using project data');
    } catch (basicError) {
      console.warn('Failed to fetch Instagram profile, using project data:', basicError);
    }
    setCreator(baseCreator);
  }
}
```

---

## ✅ Checklist Finale

- [x] Tous les endpoints appellent `call_meta()` (pas de mock data)
- [x] Tous les endpoints ont des APP REVIEW NOTES dans le backend
- [x] 7/8 endpoints ont un CTA dans le frontend
- [ ] ⚠️ `/ig-profile` manque un CTA dans le frontend
- [x] Tous les endpoints sont mappés à l'ordre de la vidéo

---

## 🎯 Conclusion

**7/8 endpoints sont prêts pour App Review.** 

L'endpoint `/ig-profile` (permission `instagram_basic`) est implémenté dans le backend mais n'est pas encore utilisé dans le frontend. Il est recommandé de l'ajouter comme fallback dans `CreatorDetail.tsx` pour supporter les comptes Instagram personnels (non Business).

