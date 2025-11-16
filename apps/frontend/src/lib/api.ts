// src/lib/api.ts - API client pour Lovable
// En dev : utiliser le proxy Vite (vite.config.ts) qui redirige vers Railway
// En prod : utiliser VITE_API_URL si défini, sinon proxy Vercel
export const getApiBase = (): string => {
  // En développement, utiliser le proxy Vite
  if (import.meta.env.DEV) {
    return ''; // Proxy Vite redirige vers Railway
  }
  
  // En production, utiliser VITE_API_URL si défini (pour tests directs Railway)
  // Sinon, utiliser le proxy Vercel
  const apiUrl = import.meta.env.VITE_API_URL;
  if (apiUrl) {
    // URL absolue fournie (Railway direct) - utiliser telle quelle
    return apiUrl.endsWith('/') ? apiUrl.slice(0, -1) : apiUrl;
  }
  
  // Sinon, utiliser le proxy Vercel (chemin relatif)
  return ''; // Proxy Vercel gère la redirection vers Railway
};

// Calculer API_BASE à chaque fois pour éviter les problèmes de cache
// Ne pas utiliser une constante, mais une fonction qui recalcule à chaque appel
export const getApiBaseUrl = () => getApiBase();

// Pour compatibilité avec le code existant
const API_BASE = getApiBase();

// Debug: log API_BASE pour vérifier la configuration
if (import.meta.env.DEV) {
  console.log('🔧 API_BASE (dev):', API_BASE || '(using Vite proxy to Railway)');
}

const isBrowser = typeof window !== 'undefined';

const getStoredToken = (): string | null => {
  if (!isBrowser) return null;
  try {
    return localStorage.getItem('token');
  } catch {
    return null;
  }
};

const withAuthHeaders = (headers: Record<string, string> = {}) => {
  const token = getStoredToken();
  if (token) {
    return {
      ...headers,
      Authorization: `Bearer ${token}`,
    };
  }
  return headers;
};

export interface SearchParams {
  q?: string;
  hashtags?: string;
  platform?: 'instagram' | 'tiktok';
  date_from?: string;
  date_to?: string;
  sort?: 'score_trend:desc' | 'posted_at:desc' | 'like_count:desc';
  limit?: number;
  cursor?: string | null;
}

export interface PostHit {
  id: string;
  platform: string;
  username?: string;
  caption?: string;
  hashtags?: string[];
  media_type?: string;
  media_url?: string;
  thumbnail_url?: string;
  permalink: string;
  posted_at: string;
  like_count?: number;
  comment_count?: number;
  view_count?: number;
  score_trend?: number;
}

export interface SearchResponse {
  data: PostHit[];
}

export async function searchPosts(params: SearchParams): Promise<SearchResponse> {
  const searchParams = new URLSearchParams();
  if (params.q) {
    searchParams.set('tag', params.q.replace('#', ''));
  }
  searchParams.set('limit', String(params.limit || 12));

  const apiBase = getApiBase();
  const url = apiBase ? `${apiBase}/api/v1/meta/ig-hashtag?${searchParams.toString()}` : `/api/v1/meta/ig-hashtag?${searchParams.toString()}`;

  const response = await fetch(url, {
    headers: withAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`HTTP_${response.status}`);
  }

  return response.json();
}

export async function fetchMetaIGPublic(tag: string, limit: number = 12): Promise<any> {
  const apiBase = getApiBase();
  const searchParams = new URLSearchParams();
  searchParams.set('tag', tag.replace('#', ''));
  searchParams.set('limit', String(limit));
  
  const url = apiBase ? `${apiBase}/api/v1/meta/ig-public?${searchParams.toString()}` : `/api/v1/meta/ig-public?${searchParams.toString()}`;

  const response = await fetch(url, {
    headers: withAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`HTTP_${response.status}`);
  }

  return response.json();
}

export async function fetchMetaOEmbed(permalink: string): Promise<any> {
  const apiBase = getApiBase();
  const url = apiBase ? `${apiBase}/api/v1/meta/oembed?url=${encodeURIComponent(permalink)}` : `/api/v1/meta/oembed?url=${encodeURIComponent(permalink)}`;

  const response = await fetch(url, {
    headers: withAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`HTTP_${response.status}`);
    }

  return response.json();
}

export async function fetchPagePublicPosts(pageId: string, limit = 10): Promise<any> {
  const apiBase = getApiBase();
  const params = new URLSearchParams({
    page_id: pageId,
    limit: String(limit),
  });

  const url = apiBase ? `${apiBase}/api/v1/meta/page-public?${params.toString()}` : `/api/v1/meta/page-public?${params.toString()}`;
  
  const response = await fetch(url, {
    headers: withAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error(`HTTP_${response.status}`);
  }

  return response.json();
}

export async function fetchMetaInsights(resourceId: string, platform: 'instagram' | 'facebook', metrics: string): Promise<any> {
  const apiBase = getApiBase();
  const params = new URLSearchParams({
    resource_id: resourceId,
    platform,
    metrics,
  });

  const url = apiBase ? `${apiBase}/api/v1/meta/insights?${params.toString()}` : `/api/v1/meta/insights?${params.toString()}`;

  const response = await fetch(url, {
    headers: withAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`HTTP_${response.status}`);
  }
  
  return response.json();
}

// TikTok API functions
export async function fetchTikTokProfile(userId?: string): Promise<any> {
  const apiBase = getApiBase();
  const params = new URLSearchParams();
  if (userId) {
    params.set('user_id', userId);
  }

  const url = apiBase 
    ? `${apiBase}/api/v1/tiktok/profile?${params.toString()}` 
    : `/api/v1/tiktok/profile?${params.toString()}`;

  const response = await fetch(url, {
    headers: withAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`HTTP_${response.status}`);
  }

  return response.json();
}

export async function fetchTikTokStats(userId?: string): Promise<any> {
  const apiBase = getApiBase();
  const params = new URLSearchParams();
  if (userId) {
    params.set('user_id', userId);
  }

  const url = apiBase 
    ? `${apiBase}/api/v1/tiktok/stats?${params.toString()}` 
    : `/api/v1/tiktok/stats?${params.toString()}`;

  const response = await fetch(url, {
    headers: withAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`HTTP_${response.status}`);
  }

  return response.json();
}

export async function fetchTikTokVideos(query?: string, limit: number = 10, cursor?: string): Promise<any> {
  const apiBase = getApiBase();
  const params = new URLSearchParams({
    limit: String(limit),
  });
  if (query) {
    params.set('query', query);
  }
  if (cursor) {
    params.set('cursor', cursor);
  }

  const url = apiBase 
    ? `${apiBase}/api/v1/tiktok/videos?${params.toString()}` 
    : `/api/v1/tiktok/videos?${params.toString()}`;

  const response = await fetch(url, {
    headers: withAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`HTTP_${response.status}`);
  }

  return response.json();
}

export async function searchHashtags(q: string, platform: string = 'instagram'): Promise<any[]> {
  const apiBase = getApiBase();
  const url = apiBase ? `${apiBase}/v1/search/hashtags?q=${q}&platform=${platform}` : `/v1/search/hashtags?q=${q}&platform=${platform}`;
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
    }
  });
  
  if (!response.ok) {
    throw new Error(`HTTP_${response.status}`);
  }
  
  return response.json();
}

export async function checkHealth(): Promise<{ status: string }> {
  const apiBase = getApiBase();
  const url = apiBase ? `${apiBase}/healthz` : '/healthz';
  const response = await fetch(url);
  return response.json();
}

// Nouvelles fonctions d'authentification
export async function login(email: string, password: string) {
  const apiBase = getApiBase();
  const url = apiBase ? `${apiBase}/api/v1/auth/login` : '/api/v1/auth/login';
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  if (!response.ok) {
    throw new Error('Login failed');
  }
  
  return response.json();
}

export async function register(email: string, password: string, name?: string) {
  const apiBase = getApiBase();
  const url = apiBase ? `${apiBase}/api/v1/auth/register` : '/api/v1/auth/register';
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, name })
  });
  
  if (!response.ok) {
    throw new Error('Registration failed');
  }
  
  return response.json();
}

export async function getMe(token: string) {
  const apiBase = getApiBase();
  const url = apiBase ? `${apiBase}/api/v1/auth/me` : '/api/v1/auth/me';
  const response = await fetch(url, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (!response.ok) {
    throw new Error('Failed to get user info');
  }
  
  return response.json();
}

// Projects API
export interface ProjectCreate {
  name?: string;
  description?: string;
  platforms?: string[];
  scope_type?: string;
  scope_query?: string;
  hashtag_names?: string[];
  creator_usernames?: string[];
}

export interface Project {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  status: string;
  platforms: string[];
  scope_type?: string;
  scope_query?: string;
  creators_count?: number;
  posts_count?: number;
  signals_count?: number;
  last_run_at?: string;
  last_signal_at?: string;
  created_at: string;
  updated_at: string;
  hashtags?: Array<{
    id: number;
    link_id?: number;
    name: string;
    platform_id?: number;
    platform?: string;
    added_at?: string;
  }>;
  creators?: Array<{
    id: number;
    creator_username: string;
    platform_id?: number;
    platform?: string;
    added_at?: string;
  }>;
}

export async function createProject(project: ProjectCreate): Promise<Project> {
  const token = localStorage.getItem('token');
  
  // Utiliser getApiBase() pour déterminer l'URL de base
  // En dev : proxy Vite (''), en prod : VITE_API_URL ou proxy Vercel ('')
  const apiBase = getApiBase();
  // IMPORTANT: Utiliser '/' (slash) pour la route, FastAPI gère les deux versions
  const url = apiBase ? `${apiBase}/api/v1/projects` : '/api/v1/projects';
  
  console.log('API: Creating project at:', url);
  console.log('API: Using proxy:', import.meta.env.DEV ? 'Vite' : 'Vercel');
  console.log('API: Request body:', JSON.stringify(project, null, 2));
  
  const response = await fetch(url, {
    mode: 'cors',
    credentials: 'same-origin', // Utiliser same-origin pour le proxy Vercel
    redirect: 'follow', // Suivre les redirections normalement
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token || ''}`,
    },
    body: JSON.stringify(project),
  });
  
  console.log('API: Response status:', response.status);
  console.log('API: Response type:', response.type);
  console.log('API: Response redirected:', response.redirected);
  
  if (!response.ok) {
    const errorText = await response.text();
    console.error('API: Error response:', errorText);
    let error;
    try {
      error = JSON.parse(errorText);
    } catch {
      error = { detail: errorText || 'Failed to create project' };
    }
    throw new Error(error.detail || `HTTP ${response.status}: Failed to create project`);
  }
  
  const data = await response.json();
  console.log('API: Project created successfully:', data);
  return data;
}

export async function getProjects(): Promise<Project[]> {
  const token = localStorage.getItem('token');
  
  // Utiliser getApiBase() pour déterminer l'URL de base
  const apiBase = getApiBase();
  const url = apiBase ? `${apiBase}/api/v1/projects` : '/api/v1/projects';
  
  const response = await fetch(url, {
    mode: 'cors',
    credentials: apiBase ? 'include' : 'same-origin', // include pour Railway direct, same-origin pour proxy
    headers: {
      'Authorization': `Bearer ${token || ''}`,
    },
  });
  
  if (!response.ok) {
    throw new Error('Failed to get projects');
  }
  
  return response.json();
}

export async function addProjectCreator(projectId: string, payload: { username: string; platform?: string }): Promise<Project> {
  const token = localStorage.getItem('token');
  const apiBase = getApiBase();
  const url = apiBase ? `${apiBase}/api/v1/projects/${projectId}/creators` : `/api/v1/projects/${projectId}/creators`;

  const response = await fetch(url, {
    mode: 'cors',
    credentials: 'same-origin',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token || ''}`,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    let detail = errorText;
    try {
      const parsed = JSON.parse(errorText);
      detail = parsed.detail || errorText;
    } catch (err) {
      /* ignore */
    }
    throw new Error(detail || `HTTP ${response.status}: Failed to add creator`);
  }

  return response.json();
}

export async function removeProjectCreator(projectId: string, creatorLinkId: number): Promise<void> {
  const token = localStorage.getItem('token');
  const apiBase = getApiBase();
  const url = apiBase ? `${apiBase}/api/v1/projects/${projectId}/creators/${creatorLinkId}` : `/api/v1/projects/${projectId}/creators/${creatorLinkId}`;

  const response = await fetch(url, {
    mode: 'cors',
    credentials: 'same-origin',
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token || ''}`,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    let detail = errorText;
    try {
      const parsed = JSON.parse(errorText);
      detail = parsed.detail || errorText;
    } catch (err) {
      /* ignore */
    }
    throw new Error(detail || `HTTP ${response.status}: Failed to remove creator`);
  }
}

export async function addProjectHashtag(projectId: string, payload: { hashtag: string; platform?: string }): Promise<Project> {
  const token = localStorage.getItem('token');
  const apiBase = getApiBase();
  const url = apiBase ? `${apiBase}/api/v1/projects/${projectId}/hashtags` : `/api/v1/projects/${projectId}/hashtags`;

  const response = await fetch(url, {
    mode: 'cors',
    credentials: 'same-origin',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token || ''}`,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    let detail = errorText;
    try {
      const parsed = JSON.parse(errorText);
      detail = parsed.detail || errorText;
    } catch (err) {
      /* ignore */
    }
    throw new Error(detail || `HTTP ${response.status}: Failed to add hashtag`);
  }

  return response.json();
}

export async function removeProjectHashtag(projectId: string, linkId: number): Promise<void> {
  const token = localStorage.getItem('token');
  const apiBase = getApiBase();
  const url = apiBase ? `${apiBase}/api/v1/projects/${projectId}/hashtags/${linkId}` : `/api/v1/projects/${projectId}/hashtags/${linkId}`;

  const response = await fetch(url, {
    mode: 'cors',
    credentials: 'same-origin',
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token || ''}`,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    let detail = errorText;
    try {
      const parsed = JSON.parse(errorText);
      detail = parsed.detail || errorText;
    } catch (err) {
      /* ignore */
    }
    throw new Error(detail || `HTTP ${response.status}: Failed to remove hashtag`);
  }
}

export interface ProjectPost {
  id: string;
  author?: string;
  caption?: string;
  media_url?: string;
  permalink?: string;
  posted_at?: string;
  platform?: string;
  like_count?: number;
  comment_count?: number;
  score_trend?: number;
}

export async function getProjectPosts(projectId: string, platform?: string): Promise<ProjectPost[]> {
  const token = localStorage.getItem('token');
  const apiBase = getApiBase();
  const params = new URLSearchParams();
  if (platform) {
    params.set('platform', platform);
  }
  const url = apiBase 
    ? `${apiBase}/api/v1/projects/${projectId}/posts${params.toString() ? '?' + params.toString() : ''}` 
    : `/api/v1/projects/${projectId}/posts${params.toString() ? '?' + params.toString() : ''}`;

  const response = await fetch(url, {
    mode: 'cors',
    credentials: 'same-origin',
    headers: {
      'Authorization': `Bearer ${token || ''}`,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    let detail = errorText;
    try {
      const parsed = JSON.parse(errorText);
      detail = parsed.detail || errorText;
    } catch (err) {
      /* ignore */
    }
    throw new Error(detail || `HTTP ${response.status}: Failed to load project posts`);
  }
  
  return response.json();
}