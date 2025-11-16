import { useState, useEffect, useMemo, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { ProjectPanel } from '@/components/ProjectPanel';
import { InstagramInsights } from '@/components/InstagramInsights';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Plus, X, Heart, MessageCircle, Eye, ArrowLeft, Bell, AtSign, Trash2, ExternalLink, ArrowUpDown, ArrowUp, ArrowDown, TrendingUp, RefreshCcw, Code2, Sparkles } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';
import { useToast } from '@/hooks/use-toast';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

// Import getApiBase from api.ts
import { getApiBase, addProjectCreator, removeProjectCreator, addProjectHashtag, removeProjectHashtag, getProjectPosts, fetchMetaIGPublic, fetchTikTokVideos } from '@/lib/api';

const PLATFORM_OPTIONS = ['instagram', 'facebook', 'tiktok'] as const;
const formatPlatformLabel = (value: string) => value.charAt(0).toUpperCase() + value.slice(1);

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [project, setProject] = useState<any>(null);
  const [posts, setPosts] = useState<any[]>([]);
  const [creators, setCreators] = useState<any[]>([]);
  const [niches, setNiches] = useState<any[]>([]);
  const [creatorLinks, setCreatorLinks] = useState<any[]>([]);
  const [hashtagLinks, setHashtagLinks] = useState<any[]>([]);
  const [addCreatorOpen, setAddCreatorOpen] = useState(false);
  const [newCreatorUsername, setNewCreatorUsername] = useState('');
  const [newCreatorPlatform, setNewCreatorPlatform] = useState('instagram');
  const [isSavingCreator, setIsSavingCreator] = useState(false);
  const [creatorSuggestions, setCreatorSuggestions] = useState<string[]>([]);
  const [addHashtagOpen, setAddHashtagOpen] = useState(false);
  const [newHashtagName, setNewHashtagName] = useState('');
  const [newHashtagPlatform, setNewHashtagPlatform] = useState('instagram');
  const [isSavingHashtag, setIsSavingHashtag] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedPost, setSelectedPost] = useState<any>(null);
  const [postDialogOpen, setPostDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [editName, setEditName] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [sortColumn, setSortColumn] = useState<string>('posted_at');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [refreshTrigger, setRefreshTrigger] = useState(Date.now());
  const [fetchingPostId, setFetchingPostId] = useState<string | null>(null);
  const [embedDialogOpen, setEmbedDialogOpen] = useState(false);
  const [selectedPlatformFilter, setSelectedPlatformFilter] = useState<string | 'all'>('all');
  const [isFetchingMeta, setIsFetchingMeta] = useState(false);
  const [isFetchingTikTok, setIsFetchingTikTok] = useState(false);

  const pieData: Array<{ name: string; value: number; color: string }> = [];
  const reachData: Array<{ date: string; organic: number; paid: number }> = [];
  const engagementTrendData: Array<{ date: string; engagement: number; reach: number; impressions: number }> = [];
  const topPerformingCreators: Array<{ username: string; posts: number; avg_engagement: number; total_reach: number }> = [];

  const applyProjectData = useCallback((projectData: any) => {
    setProject(projectData);

    const projectCreators = projectData.creators || [];
    setCreatorLinks(projectCreators);
    const creatorCards = projectCreators.map((c: any) => ({
      handle: c.creator_username,
      platform: c.platform || projectData.platforms?.[0] || 'instagram',
      profile_picture: `https://api.dicebear.com/7.x/avataaars/svg?seed=${c.creator_username}`,
      linkId: c.id,
    }));
    if (creatorCards.length === 0 && projectData.scope_query) {
      const queryUsers = projectData.scope_query
        .split(',')
        .map((q: string) => q.trim())
        .filter((entry: string) => entry.startsWith('@'))
        .map((entry: string) => entry.replace('@', ''));
      setCreators(
        queryUsers.map((username: string) => ({
          handle: username,
          platform: projectData.platforms?.[0] || 'instagram',
          profile_picture: `https://api.dicebear.com/7.x/avataaars/svg?seed=${username}`,
        }))
      );
    } else {
      setCreators(creatorCards);
    }

    const projectHashtags = projectData.hashtags || [];
    setHashtagLinks(projectHashtags);
    const hashtagEntries = projectHashtags.map((link: any, idx: number) => ({
      id: link.id ?? idx + 1,
      linkId: link.link_id ?? link.id,
      name: link.name,
      posts: link.posts ?? 0,
      growth: link.growth ?? '0%',
      engagement: link.engagement ?? 0,
      platform: link.platform,
    }));
    if (hashtagEntries.length === 0 && projectData.scope_query) {
      const queryHashtags = projectData.scope_query
        .split(',')
        .map((q: string) => q.trim())
        .filter((entry: string) => entry.startsWith('#'))
        .map((entry: string) => entry.replace('#', ''))
        .map((name: string, idx: number) => ({
          id: idx + 1,
          linkId: idx + 1,
          name,
          posts: 0,
          growth: '0%',
          engagement: 0,
          platform: projectData.platforms?.[0] || 'instagram',
        }));
      setNiches(queryHashtags);
    } else {
      setNiches(hashtagEntries);
    }

    setEditName(projectData.name || 'Untitled project');
    setEditDescription(projectData.description || '');
  }, []);

  const fetchProjectPosts = useCallback(async (platformFilter?: string) => {
    if (!id) return;
    try {
      // Convertir le filtre frontend en filtre backend
      let backendPlatform: string | undefined = undefined;
      if (platformFilter === 'meta') {
        backendPlatform = 'meta'; // Backend gère 'meta' = instagram + facebook
      } else if (platformFilter === 'tiktok') {
        backendPlatform = 'tiktok';
      } else if (platformFilter === 'instagram') {
        backendPlatform = 'instagram';
      } else if (platformFilter === 'facebook') {
        backendPlatform = 'facebook';
      }
      // Si 'all', backendPlatform reste undefined (pas de filtre)
      
      const postsData = await getProjectPosts(id, backendPlatform);
      setPosts(postsData);
    } catch (error) {
      console.error('Error loading project posts:', error);
    }
  }, [id]);

  // Fetch posts from API - adaptatif selon la vue
  const handleFetch = async () => {
    if (!project || !id) return;
    
    const isFetching = isFetchingMeta || isFetchingTikTok;
    if (isFetching) return; // Éviter les appels multiples
    
    // Déterminer quelles plateformes fetcher selon la vue
    const shouldFetchMeta = selectedPlatformFilter === 'all' || selectedPlatformFilter === 'meta';
    const shouldFetchTikTok = selectedPlatformFilter === 'all' || selectedPlatformFilter === 'tiktok';
    
    if (shouldFetchMeta) setIsFetchingMeta(true);
    if (shouldFetchTikTok) setIsFetchingTikTok(true);
    
    try {
      const projectHashtags = project?.hashtags || hashtagLinks || [];
      let fetchedCount = 0;
      
      // Fetch Meta si nécessaire
      if (shouldFetchMeta) {
        const metaHashtags = projectHashtags.filter((h: any) => 
          (h.platform === 'instagram' || h.platform === 'facebook') && h.name
        );
        
        if (metaHashtags.length > 0) {
          for (const hashtag of metaHashtags.slice(0, 3)) {
            try {
              console.log(`📡 [FETCH] Calling Meta API for #${hashtag.name}...`);
              const response = await fetchMetaIGPublic(hashtag.name, 10);
              const source = response.meta?.source || 'unknown';
              if (source === 'instagram_public_content_api') {
                console.log(`✅ [FETCH] Meta API SUCCESS for #${hashtag.name} (${response.data?.length || 0} posts from API)`);
                fetchedCount++;
              } else {
                console.log(`⚠️ [FETCH] Meta returned DB fallback for #${hashtag.name} (source: ${source})`);
              }
            } catch (error: any) {
              console.error(`❌ [FETCH] Meta API FAILED for #${hashtag.name}:`, error.message);
              // Continue avec les autres hashtags
            }
          }
        }
      }
      
      // Fetch TikTok si nécessaire
      if (shouldFetchTikTok) {
        const tiktokHashtags = projectHashtags.filter((h: any) => 
          h.platform === 'tiktok' && h.name
        );
        
        if (tiktokHashtags.length > 0) {
          for (const hashtag of tiktokHashtags.slice(0, 3)) {
            try {
              console.log(`📡 [FETCH] Calling TikTok API for #${hashtag.name}...`);
              const response = await fetchTikTokVideos(hashtag.name, 10);
              const source = response.meta?.source || 'unknown';
              const videoCount = response.data?.length || 0;
              
              if (source === 'tiktok_video_list_api') {
                console.log(`✅ [FETCH] TikTok API SUCCESS for #${hashtag.name} (${videoCount} videos from API)`);
                fetchedCount++;
              } else if (source === 'database_fallback' && videoCount > 0) {
                console.log(`⚠️ [FETCH] TikTok returned DB fallback for #${hashtag.name} (${videoCount} videos from DB)`);
                fetchedCount++; // Compter aussi les résultats DB fallback
              } else {
                console.log(`⚠️ [FETCH] TikTok returned 0 results for #${hashtag.name} (source: ${source})`);
              }
            } catch (error: any) {
              console.error(`❌ [FETCH] TikTok API FAILED for #${hashtag.name}:`, error.message);
              // Continue avec les autres hashtags
            }
          }
        } else {
          // Pas de hashtags TikTok trouvés
          console.log(`⚠️ [FETCH] No TikTok hashtags found in project`);
        }
      }
      
      if (fetchedCount === 0) {
        toast({
          title: 'No hashtags found',
          description: `Add ${shouldFetchMeta && shouldFetchTikTok ? 'Meta or TikTok' : shouldFetchMeta ? 'Meta' : 'TikTok'} hashtags to fetch posts`,
          variant: 'destructive',
        });
        return;
      }

      // Recharger les posts du projet avec le filtre actuel
      const platformFilter = selectedPlatformFilter === 'all' ? undefined : selectedPlatformFilter;
      await fetchProjectPosts(platformFilter);
      setRefreshTrigger(Date.now());
      
      const platformText = shouldFetchMeta && shouldFetchTikTok ? 'Meta and TikTok' : shouldFetchMeta ? 'Meta' : 'TikTok';
      toast({
        title: 'Posts fetched',
        description: `Posts from ${platformText} API have been added to the project`,
      });
    } catch (error: any) {
      toast({
        title: 'Error fetching posts',
        description: error.message || 'Failed to fetch posts from API',
        variant: 'destructive',
      });
    } finally {
      setIsFetchingMeta(false);
      setIsFetchingTikTok(false);
    }
  };

  const fetchProject = useCallback(async () => {
    if (!id) return;
      setLoading(true);
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/auth');
          return;
        }

        const response = await fetch(`/api/v1/projects/${id}`, {
          mode: 'cors',
          credentials: 'same-origin',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error(`Failed to load project: ${response.status}`);
        }

        const projectData = await response.json();
        console.log('Project loaded:', projectData);
      applyProjectData(projectData);
    } catch (error: any) {
      console.error('Error loading project:', error);
      toast({
        title: 'Error',
        description: error.message || 'Failed to load project',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  }, [id, navigate, toast, applyProjectData]);

  useEffect(() => {
    fetchProject();
  }, [fetchProject]);

  useEffect(() => {
    // Recharger les posts quand le filtre change
    const platformFilter = selectedPlatformFilter === 'all' ? undefined : selectedPlatformFilter;
    fetchProjectPosts(platformFilter);
  }, [fetchProjectPosts, selectedPlatformFilter]);

  const handleAddCreator = () => {
    setNewCreatorUsername('');
    setNewCreatorPlatform('instagram');
    setAddCreatorOpen(true);
  };

  const handleAddNiche = () => {
    setNewHashtagName('');
    setNewHashtagPlatform('instagram');
    setAddHashtagOpen(true);
  };

  const handleSaveCreator = async () => {
    if (!id) return;
    const username = newCreatorUsername.trim();
    if (!username) {
      toast({ title: 'Username required', description: 'Enter a creator username', variant: 'destructive' });
      return;
    }
    setIsSavingCreator(true);
    try {
      const updatedProject = await addProjectCreator(id, {
        username,
        platform: newCreatorPlatform,
      });
      applyProjectData(updatedProject);
      await fetchProjectPosts();
      await fetchProject();
      setAddCreatorOpen(false);
      setNewCreatorUsername('');
      toast({ title: 'Creator added', description: `@${username} linked to the project.` });
      } catch (error: any) {
      console.error('Error adding creator:', error);
        toast({
          title: 'Error',
        description: error?.message || 'Unable to add creator',
          variant: 'destructive',
        });
      } finally {
      setIsSavingCreator(false);
      }
    };

  const handleRemoveCreatorLink = async (linkId: number) => {
    if (!id) return;
    try {
      await removeProjectCreator(id, linkId);
      await fetchProject();
      await fetchProjectPosts();
      toast({ title: 'Creator removed' });
    } catch (error: any) {
      console.error('Error removing creator:', error);
    toast({
        title: 'Error',
        description: error?.message || 'Unable to remove creator',
        variant: 'destructive',
      });
    }
  };

  const handleSaveHashtag = async () => {
    if (!id) return;
    const hashtag = newHashtagName.trim().replace(/^#/, '');
    if (!hashtag) {
      toast({ title: 'Hashtag required', description: 'Enter a hashtag', variant: 'destructive' });
      return;
    }
    setIsSavingHashtag(true);
    try {
      // Utiliser 'instagram' par défaut - le backend cherche sur TOUTES les plateformes de toute façon
      const updatedProject = await addProjectHashtag(id, {
        hashtag,
        platform: 'instagram', // Le backend auto-link sur toutes les plateformes
      });
      applyProjectData(updatedProject);
      
      // 🔥 AUTO-FETCH: Appeler TOUTES les APIs (Meta + TikTok) après l'ajout du hashtag
      // Le backend cherche déjà sur toutes les plateformes, donc on fetch aussi toutes les APIs
      const fetchPromises = [];
      
      // Fetch Meta API
      fetchPromises.push(
        fetchMetaIGPublic(hashtag, 10)
          .then((response) => {
            const source = response.meta?.source || 'unknown';
            if (source === 'instagram_public_content_api') {
              console.log(`✅ [AUTO-FETCH] Meta API SUCCESS: ${response.data?.length || 0} posts from API`);
            } else {
              console.log(`⚠️ [AUTO-FETCH] Meta returned DB fallback: ${response.data?.length || 0} posts (source: ${source})`);
            }
          })
          .catch((error: any) => {
            console.error(`❌ [AUTO-FETCH] Meta API FAILED for #${hashtag}:`, error.message);
          })
      );
      
      // Fetch TikTok API
      fetchPromises.push(
        fetchTikTokVideos(hashtag, 10)
          .then((response) => {
            const source = response.meta?.source || 'unknown';
            if (source === 'tiktok_video_list_api') {
              console.log(`✅ [AUTO-FETCH] TikTok API SUCCESS: ${response.data?.length || 0} videos from API`);
            } else {
              console.log(`⚠️ [AUTO-FETCH] TikTok returned DB fallback: ${response.data?.length || 0} videos (source: ${source})`);
            }
          })
          .catch((error: any) => {
            console.error(`❌ [AUTO-FETCH] TikTok API FAILED for #${hashtag}:`, error.message);
          })
      );
      
      // Attendre que tous les fetches soient terminés (en parallèle)
      await Promise.allSettled(fetchPromises);
      
      // Recharger avec le filtre actuel
      const platformFilter = selectedPlatformFilter === 'all' ? undefined : selectedPlatformFilter;
      await fetchProjectPosts(platformFilter);
      await fetchProject();
      setAddHashtagOpen(false);
      setNewHashtagName('');
      toast({ 
        title: 'Hashtag added', 
        description: `#${hashtag} linked to the project. Fetching posts from all platforms...` 
      });
    } catch (error: any) {
      console.error('Error adding hashtag:', error);
    toast({
        title: 'Error',
        description: error?.message || 'Unable to add hashtag',
        variant: 'destructive',
      });
    } finally {
      setIsSavingHashtag(false);
    }
  };

  const handleRemoveHashtagLink = async (linkId: number) => {
    if (!id) return;
    try {
      await removeProjectHashtag(id, linkId);
      await fetchProject();
      await fetchProjectPosts();
      toast({ title: 'Hashtag removed' });
    } catch (error: any) {
      console.error('Error removing hashtag:', error);
      toast({
        title: 'Error',
        description: error?.message || 'Unable to remove hashtag',
        variant: 'destructive',
      });
    }
  };

  // Filter posts by platform
  const filteredPosts = useMemo(() => {
    if (selectedPlatformFilter === 'all') {
      return posts;
    }
    return posts.filter((post: any) => {
      const postPlatform = post.platform || 'instagram';
      if (selectedPlatformFilter === 'meta') {
        return postPlatform === 'instagram' || postPlatform === 'facebook';
      }
      return postPlatform === selectedPlatformFilter;
    });
  }, [posts, selectedPlatformFilter]);

  // Function to sort posts
  const sortedPosts = useMemo(() => {
    const sorted = [...filteredPosts];
    sorted.sort((a: any, b: any) => {
      let aVal: any = a[sortColumn];
      let bVal: any = b[sortColumn];

      // Gérer les valeurs nulles/undefined
      if (aVal === null || aVal === undefined) aVal = '';
      if (bVal === null || bVal === undefined) bVal = '';

      // Tri par date
      if (sortColumn === 'posted_at' || sortColumn === 'fetched_at') {
        const aDate = aVal ? new Date(aVal).getTime() : 0;
        const bDate = bVal ? new Date(bVal).getTime() : 0;
        return sortDirection === 'asc' ? aDate - bDate : bDate - aDate;
      }

      // Tri numérique
      if (sortColumn === 'like_count' || sortColumn === 'comment_count' || sortColumn === 'view_count' || sortColumn === 'score') {
        const aNum = Number(aVal) || 0;
        const bNum = Number(bVal) || 0;
        return sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
      }

      // Tri textuel
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        const cmp = aVal.localeCompare(bVal);
        return sortDirection === 'asc' ? cmp : -cmp;
      }

      return 0;
    });
    return sorted;
  }, [posts, sortColumn, sortDirection]);

  // 🔍 Autocomplétion creators: fetch depuis l'API quand l'utilisateur tape
  useEffect(() => {
    const fetchCreatorSuggestions = async () => {
      if (newCreatorUsername.trim().length < 2) {
        setCreatorSuggestions([]);
        return;
      }
      
      try {
        const token = localStorage.getItem('token');
        const apiBase = getApiBase();
        const response = await fetch(
          `${apiBase}/api/v1/projects/creators/search?q=${encodeURIComponent(newCreatorUsername)}&limit=10`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );
        
        if (response.ok) {
          const data = await response.json();
          // Filtrer ceux déjà liés au projet
          const linkedUsernames = new Set(creatorLinks.map((link: any) => link.creator_username));
          const filtered = data.creators
            .map((c: any) => c.username)
            .filter((username: string) => !linkedUsernames.has(username));
          setCreatorSuggestions(filtered);
        }
      } catch (error) {
        console.error('Error fetching creator suggestions:', error);
      }
    };
    
    const debounceTimer = setTimeout(fetchCreatorSuggestions, 300);
    return () => clearTimeout(debounceTimer);
  }, [newCreatorUsername, creatorLinks]);

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('desc');
    }
  };

  const getSortIcon = (column: string) => {
    if (sortColumn !== column) {
      return <ArrowUpDown className="h-4 w-4 ml-1 opacity-50" />;
    }
    return sortDirection === 'asc' ? <ArrowUp className="h-4 w-4 ml-1" /> : <ArrowDown className="h-4 w-4 ml-1" />;
  };

  if (loading || !project) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="container py-8">
          <div className="text-center">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container py-8">
        {/* Header */}
        <div className="mb-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/projects')}
            className="mb-2"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Projects
          </Button>
        </div>

        <div className="grid gap-4 md:grid-cols-2 mb-6">
              <ProjectPanel
                project={project}
                onEdit={() => {
                  setEditName(project.name || '');
                  setEditDescription(project.description || '');
                  setEditDialogOpen(true);
                }}
                onDelete={() => setDeleteDialogOpen(true)}
              />
          <div className="space-y-4">
            <Card>
              <CardHeader className="py-3">
                <CardTitle className="text-base">Tracking</CardTitle>
                  </CardHeader>
              <CardContent className="space-y-5">
                <div>
                  <p className="text-xs uppercase tracking-wide text-muted-foreground mb-1">Hashtags</p>
                  {hashtagLinks.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No hashtags linked yet.</p>
                  ) : (
                    <div className="space-y-1">
                      {hashtagLinks.map((link: any) => (
                        <div
                          key={link.link_id ?? link.id}
                          className="flex items-center justify-between border-b border-border/40 py-2 last:border-b-0"
                        >
                          <div className="flex items-center gap-2 text-sm">
                            <span className="font-medium">#{link.name}</span>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-5 w-5 text-muted-foreground hover:text-destructive"
                            onClick={() => handleRemoveHashtagLink(link.link_id ?? link.id)}
                            title="Remove hashtag"
                          >
                            <X className="h-3 w-3" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="mt-2 h-7 px-2 text-xs text-muted-foreground justify-start"
                    onClick={handleAddNiche}
                  >
                    <Plus className="h-3 w-3 mr-1" />
                    Add hashtag
                  </Button>
                </div>

                <div>
                  <p className="text-xs uppercase tracking-wide text-muted-foreground mb-1">Creators</p>
                  {creatorLinks.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No creators linked yet.</p>
                  ) : (
                    <div className="space-y-1">
                      {creatorLinks.map((link: any) => (
                        <div
                          key={link.id}
                          className="flex items-center justify-between border-b border-border/40 py-2 last:border-b-0"
                        >
                          <button
                            type="button"
                            className="flex items-center gap-2 text-sm text-left hover:text-primary transition-colors"
                            onClick={() => navigate(`/projects/${id}/creator/${link.creator_username}`)}
                          >
                            <img
                              src={`https://unavatar.io/instagram/${link.creator_username}`}
                              alt={link.creator_username}
                              className="h-6 w-6 rounded-full object-cover bg-muted"
                              onError={(event) => {
                                (event.target as HTMLImageElement).src = `https://api.dicebear.com/7.x/initials/svg?seed=${link.creator_username}`;
                              }}
                            />
                            <span className="font-medium">@{link.creator_username}</span>
                            <span className="text-xs text-muted-foreground">
                              · {formatPlatformLabel(link.platform || 'instagram')}
                            </span>
                          </button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-5 w-5 text-muted-foreground hover:text-destructive"
                            onClick={() => handleRemoveCreatorLink(link.id)}
                            title="Remove creator"
                          >
                            <X className="h-3 w-3" />
                          </Button>
                              </div>
                      ))}
                            </div>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="mt-2 h-7 px-2 text-xs text-muted-foreground justify-start"
                    onClick={handleAddCreator}
                  >
                    <Plus className="h-3 w-3 mr-1" />
                    Add creator
                  </Button>
                    </div>
                  </CardContent>
                </Card>

          </div>
            </div>

        {/* Tabs */}
        <Tabs defaultValue="watchlist" className="space-y-4">
          <div className="flex items-center justify-between mb-4">
            <TabsList>
              <TabsTrigger value="watchlist">
                Watchlist
              </TabsTrigger>
              <TabsTrigger value="grid">
                Grid
              </TabsTrigger>
              <TabsTrigger value="analytics">
                Analytics
              </TabsTrigger>
            </TabsList>
            
            <div className="flex gap-2 items-center">
              {/* Platform Filter */}
              <div className="flex gap-1 border rounded-md p-0.5">
                <Button
                  variant={selectedPlatformFilter === 'all' ? 'default' : 'ghost'}
                  size="sm"
                  className="h-7 px-2 text-xs"
                  onClick={() => setSelectedPlatformFilter('all')}
                >
                  All
                </Button>
                <Button
                  variant={selectedPlatformFilter === 'meta' ? 'default' : 'ghost'}
                  size="sm"
                  className="h-7 px-2 text-xs"
                  onClick={() => setSelectedPlatformFilter('meta')}
                >
                  Meta
                </Button>
                <Button
                  variant={selectedPlatformFilter === 'tiktok' ? 'default' : 'ghost'}
                  size="sm"
                  className="h-7 px-2 text-xs"
                  onClick={() => setSelectedPlatformFilter('tiktok')}
                >
                  TikTok
                </Button>
              </div>

              {/* Fetch Button - adaptatif selon la vue */}
              <Button
                onClick={handleFetch}
                disabled={isFetchingMeta || isFetchingTikTok}
                variant="outline"
                size="sm"
                className="gap-1.5 h-8 text-xs"
              >
                {(isFetchingMeta || isFetchingTikTok) ? (
                  <>
                    <RefreshCcw className="h-3 w-3 animate-spin" />
                    Fetching...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-3 w-3" />
                    Fetch {selectedPlatformFilter === 'all' ? 'All' : selectedPlatformFilter === 'meta' ? 'Meta' : 'TikTok'}
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Tab 1: Watchlist - Feed + Creators + Hashtags/Commentaires/Mentions */}
          <TabsContent value="watchlist" className="space-y-6">
            {/* Section: Feed Posts */}
            <div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {sortedPosts.length > 0 ? (
                  sortedPosts.map((post) => {
                    const creator = creators.find(c => c.handle === post.author || c.handle === post.username);
                    const isImage = post.media_url ? /\.(jpg|jpeg|png|gif|webp)$/i.test(post.media_url.split('?')[0]) : false;
                    const embedUrl = post.permalink ? `${post.permalink.replace(/\/$/, '')}/embed` : undefined;
                    return (
                      <Card 
                        key={post.id} 
                        className="overflow-hidden hover:shadow-lg transition-shadow"
                        onClick={() => {
                          setSelectedPost(post);
                          setPostDialogOpen(true);
                        }}
                      >
                        <div className="aspect-square relative overflow-hidden bg-muted">
                          {post.platform === 'tiktok' ? (
                            // TikTok: Afficher thumbnail ou placeholder avec gradient (comme Search)
                            post.media_url ? (
                              <img
                                src={post.media_url}
                                alt={post.caption || post.author || 'TikTok video'}
                                className="w-full h-full object-cover"
                                onError={(e) => {
                                  // Si l'image échoue, afficher le placeholder
                                  const img = e.target as HTMLImageElement;
                                  img.style.display = 'none';
                                  const placeholder = img.parentElement?.querySelector('.tiktok-placeholder') as HTMLElement;
                                  if (placeholder) placeholder.style.display = 'flex';
                                }}
                              />
                            ) : null
                          ) : post.media_url && isImage ? (
                            <img
                              src={post.media_url}
                              alt={post.caption || post.author}
                              className="object-cover w-full h-full"
                            />
                          ) : embedUrl ? (
                            <iframe
                              src={embedUrl}
                              title={post.id}
                              className="w-full h-full"
                              allow="autoplay; clipboard-write; encrypted-media; picture-in-picture"
                            />
                          ) : null}
                          {/* Placeholder TikTok si pas de media_url ou si image échoue (comme Search) */}
                          {post.platform === 'tiktok' && (
                            <div className={`tiktok-placeholder w-full h-full bg-gradient-to-br from-pink-500 via-red-500 to-blue-500 flex flex-col items-center justify-center text-white ${post.media_url ? 'hidden' : ''}`}>
                              <svg className="w-16 h-16 mb-2" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"/>
                              </svg>
                              <span className="text-sm font-medium">TikTok Video</span>
                            </div>
                          )}
                          {/* Placeholder générique si pas de media */}
                          {!post.media_url && !embedUrl && post.platform !== 'tiktok' && (
                            <div className="w-full h-full flex items-center justify-center bg-muted/50">
                              <span className="text-muted-foreground text-sm">No media</span>
                            </div>
                          )}
                          <Badge className="absolute top-2 right-2 bg-accent">
                            {post.platform?.toUpperCase() || 'INSTAGRAM'}
                          </Badge>
                        </div>
                        
                        <CardContent className="p-4 space-y-3">
                          <div className="flex items-center gap-2">
                            <img
                              src={`https://unavatar.io/instagram/${post.author || post.username || 'instagram'}`}
                              alt={post.author || post.username || 'creator'}
                              className="w-8 h-8 rounded-full object-cover bg-muted"
                              onError={(event) => {
                                (event.target as HTMLImageElement).src = `https://api.dicebear.com/7.x/initials/svg?seed=${post.author || post.username || 'IG'}`;
                              }}
                            />
                            <div className="flex-1 min-w-0">
                              <p className="font-semibold text-sm truncate">{post.author || post.username || 'Unknown User'}</p>
                              <p className="text-xs text-muted-foreground truncate">
                                @{post.author || post.username || 'unknown'}
                              </p>
                            </div>
                          </div>

                          <p className="text-sm line-clamp-2">{post.caption}</p>

                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Heart className="h-4 w-4" />
                              <span>{(post.like_count ?? 0) > 0 ? post.like_count.toLocaleString() : '—'}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <MessageCircle className="h-4 w-4" />
                              <span>{(post.comment_count ?? 0) > 0 ? post.comment_count.toLocaleString() : '—'}</span>
                            </div>
                            {post.score_trend !== undefined && (
                              <div className="flex items-center gap-1 text-success">
                                <TrendingUp className="h-4 w-4" />
                                <span>{post.score_trend}</span>
                              </div>
                            )}
                          </div>

                          <div className="pt-2 border-t flex flex-wrap gap-2">
                            {post.permalink && (
                              <Button
                                variant="outline"
                                size="sm"
                                className="flex-1"
                                asChild
                              >
                                <a href={post.permalink} target="_blank" rel="noopener noreferrer">
                                  <ExternalLink className="h-3 w-3 mr-1" />
                                  View post
                                </a>
                              </Button>
                            )}
                            <Button
                              variant="outline"
                              size="sm"
                              className="flex-1"
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedPost(post);
                                setEmbedDialogOpen(true);
                              }}
                            >
                              <Code2 className="h-3 w-3 mr-1" />
                              Embed
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })
                ) : (
                  <Card className="col-span-full">
                    <CardContent className="p-10 text-center text-muted-foreground">
                      {selectedPlatformFilter !== 'all' 
                        ? `No ${selectedPlatformFilter === 'meta' ? 'Meta' : 'TikTok'} posts yet. Add ${selectedPlatformFilter === 'meta' ? 'Instagram/Facebook' : 'TikTok'} creators or hashtags to start tracking content.`
                        : 'No posts yet. Add creators or hashtags to start tracking content.'}
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>

          </TabsContent>

          {/* Tab 3: Grid - Table View */}
          <TabsContent value="grid" className="space-y-4">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Posts ({sortedPosts.length})</CardTitle>
                <CardDescription>
                  Tabular view of all posts with sorting
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[60px]">Image</TableHead>
                        <TableHead>Link</TableHead>
                        <TableHead 
                          className="cursor-pointer hover:bg-muted/50"
                          onClick={() => handleSort('caption')}
                        >
                          <div className="flex items-center">
                            Description
                            {getSortIcon('caption')}
                          </div>
                        </TableHead>
                        <TableHead 
                          className="cursor-pointer hover:bg-muted/50"
                          onClick={() => handleSort('posted_at')}
                        >
                          <div className="flex items-center">
                            Added
                            {getSortIcon('posted_at')}
                          </div>
                        </TableHead>
                        <TableHead 
                          className="text-right cursor-pointer hover:bg-muted/50"
                          onClick={() => handleSort('like_count')}
                        >
                          <div className="flex items-center justify-end">
                            Likes
                            {getSortIcon('like_count')}
                          </div>
                        </TableHead>
                        <TableHead 
                          className="text-right cursor-pointer hover:bg-muted/50"
                          onClick={() => handleSort('comment_count')}
                        >
                          <div className="flex items-center justify-end">
                            Comments
                            {getSortIcon('comment_count')}
                          </div>
                        </TableHead>
                        <TableHead className="text-right">Platform</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {sortedPosts.length > 0 ? (
                        sortedPosts.map((post: any) => (
                            <TableRow
                              key={post.id}
                              className="cursor-pointer hover:bg-muted/50"
                              onClick={() => {
                                setSelectedPost(post);
                                setPostDialogOpen(true);
                              }}
                            >
                              <TableCell>
                              {post.permalink ? (
                                <div className="w-12 h-12 rounded overflow-hidden">
                                  <iframe
                                    src={`${post.permalink.replace(/\/$/, '')}/embed`}
                                    className="w-full h-full border-0 pointer-events-none"
                                    scrolling="no"
                                />
                                </div>
                              ) : (
                                <div className="w-12 h-12 rounded bg-muted flex items-center justify-center text-xs text-muted-foreground">
                                  No img
                                </div>
                              )}
                              </TableCell>
                              <TableCell>
                              {post.permalink ? (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-8 px-2"
                                  asChild
                                  onClick={(e) => e.stopPropagation()}
                                >
                                  <a href={post.permalink} target="_blank" rel="noopener noreferrer">
                                    <ExternalLink className="h-3 w-3" />
                                  </a>
                                </Button>
                              ) : (
                                <span className="text-muted-foreground text-xs">-</span>
                              )}
                              </TableCell>
                              <TableCell>
                                <p className="max-w-md line-clamp-2 text-sm">
                                  {post.caption || '-'}
                                </p>
                              </TableCell>
                              <TableCell>
                              {post.posted_at || post.fetched_at ? (
                                  <div className="text-sm">
                                  <div>{new Date(post.posted_at || post.fetched_at).toLocaleDateString('en-US')}</div>
                                    <div className="text-xs text-muted-foreground">
                                    {formatDistanceToNow(new Date(post.posted_at || post.fetched_at), { addSuffix: true })}
                                    </div>
                                  </div>
                                ) : (
                                  <span className="text-muted-foreground">-</span>
                                )}
                              </TableCell>
                              <TableCell className="text-right">
                                <div className="flex items-center justify-end gap-1">
                                  <Heart className="h-4 w-4" />
                                  <span>{post.like_count?.toLocaleString() || 0}</span>
                                </div>
                              </TableCell>
                              <TableCell className="text-right">
                                <div className="flex items-center justify-end gap-1">
                                  <MessageCircle className="h-4 w-4" />
                                  <span>{post.comment_count?.toLocaleString() || 0}</span>
                                </div>
                              </TableCell>
                              <TableCell className="text-right">
                                <Badge variant="outline">{post.platform || 'instagram'}</Badge>
                              </TableCell>
                            </TableRow>
                        ))
                      ) : (
                        <TableRow>
                          <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                            {selectedPlatformFilter !== 'all' 
                              ? `No ${selectedPlatformFilter === 'meta' ? 'Meta' : 'TikTok'} posts yet. Add ${selectedPlatformFilter === 'meta' ? 'Instagram/Facebook' : 'TikTok'} creators or hashtags first.`
                              : 'No posts yet. Add creators or hashtags first.'}
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <Dialog open={addCreatorOpen} onOpenChange={setAddCreatorOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add creator</DialogTitle>
                <DialogDescription>Link a new creator to this project.</DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="new-creator-username">Username</Label>
                  <Input
                    id="new-creator-username"
                    placeholder="selenagomez"
                    value={newCreatorUsername}
                    onChange={(e) => setNewCreatorUsername(e.target.value)}
                  />
                {creatorSuggestions.length > 0 && (
                  <div className="space-y-1 pt-1 max-h-40 overflow-y-auto border border-border rounded-md p-2">
                    {creatorSuggestions.map((handle) => (
                      <button
                        key={handle}
                        type="button"
                        className="w-full text-left text-xs py-1 px-2 rounded-md hover:bg-muted transition-colors"
                        onClick={() => setNewCreatorUsername(handle)}
                      >
                        @{handle}
                      </button>
                    ))}
                  </div>
                )}
                </div>
                <div className="space-y-2">
                  <span className="text-xs font-medium text-muted-foreground">Platform</span>
                  <div className="flex gap-2">
                    {PLATFORM_OPTIONS.map((option) => (
                      <Button
                        key={option}
                        type="button"
                        variant={newCreatorPlatform === option ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setNewCreatorPlatform(option)}
                      >
                        {formatPlatformLabel(option)}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setAddCreatorOpen(false)}>Cancel</Button>
                <Button onClick={handleSaveCreator} disabled={isSavingCreator}>
                  {isSavingCreator ? 'Saving…' : 'Save'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          <Dialog open={addHashtagOpen} onOpenChange={setAddHashtagOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add hashtag</DialogTitle>
                <DialogDescription>Link a new hashtag to this project.</DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="new-hashtag-name">Hashtag</Label>
                  <Input
                    id="new-hashtag-name"
                    placeholder="fashion"
                    value={newHashtagName}
                    onChange={(e) => setNewHashtagName(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground">
                    Posts will be fetched from all platforms (Meta & TikTok). Filter by platform in the view.
                  </p>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setAddHashtagOpen(false)}>Cancel</Button>
                <Button onClick={handleSaveHashtag} disabled={isSavingHashtag}>
                  {isSavingHashtag ? 'Saving…' : 'Save'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Post Detail Dialog - Style Instagram */}
          <Dialog open={postDialogOpen} onOpenChange={setPostDialogOpen}>
            <DialogContent className="max-w-5xl max-h-[90vh] p-0 gap-0 overflow-hidden">
              {selectedPost && (() => {
                const handle = selectedPost.username || selectedPost.author || 'instagram';
                const handleSlug = handle.replace('@', '');
                const profilePic = `https://unavatar.io/instagram/${handle}`;
                const postedDate = selectedPost.posted_at ? new Date(selectedPost.posted_at) : new Date();
                const relativeTime = formatDistanceToNow(postedDate, { addSuffix: true, locale: fr });
                const caption = selectedPost.caption || '';
                const hashtags = selectedPost.hashtags || caption.match(/#\w+/g) || [];
                const mentions = selectedPost.mentions || caption.match(/@\w+/g) || [];

                return (
                  <div className="flex bg-background">
                    {/* Photo on the left */}
                    <div className="flex-shrink-0 w-full md:w-[60%] bg-black flex items-center justify-center">
                      <img
                        src={selectedPost.media_url}
                        alt={selectedPost.caption}
                        className="max-h-[90vh] w-full object-contain"
                      />
                    </div>

                    {/* Info panel on the right */}
                    <div className="flex flex-col w-full md:w-[40%] max-h-[90vh] border-l border-border">
                      {/* Header */}
                      <div className="flex items-center justify-between p-4 border-b border-border">
                        <div className="flex items-center gap-3">
                          <img
                            src={profilePic}
                            alt={selectedPost.username}
                          className="w-10 h-10 rounded-full cursor-pointer hover:opacity-80 object-cover bg-muted"
                          onError={(event) => {
                            (event.target as HTMLImageElement).src = `https://api.dicebear.com/7.x/initials/svg?seed=${handle}`;
                          }}
                            onClick={() => {
                              setPostDialogOpen(false);
                              navigate(`/projects/${id}/creator/${handleSlug}`);
                            }}
                          />
                          <div>
                            <div 
                              className="font-semibold text-sm cursor-pointer hover:opacity-80"
                              onClick={() => {
                                setPostDialogOpen(false);
                                navigate(`/projects/${id}/creator/${handleSlug}`);
                              }}
                            >
                              {selectedPost.username}
                            </div>
                            {selectedPost.location && (
                              <div className="text-xs text-muted-foreground">{selectedPost.location}</div>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Description */}
                      <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        <div className="text-sm whitespace-pre-wrap">
                          <span className="font-semibold mr-2">{selectedPost.username}</span>
                          {(() => {
                            // Formater la caption avec hashtags et mentions en texte normal mais stylisés
                            const parts: (string | JSX.Element)[] = [];
                            let lastIndex = 0;
                            
                            // Regex pour trouver hashtags et mentions
                            const regex = /(#\w+|@\w+)/g;
                            let match;
                            
                            while ((match = regex.exec(caption)) !== null) {
                              // Ajouter le texte avant le match
                              if (match.index > lastIndex) {
                                parts.push(caption.substring(lastIndex, match.index));
                              }
                              
                              // Ajouter le hashtag ou mention stylisé
                              const isHashtag = match[0].startsWith('#');
                              parts.push(
                                <span
                                  key={match.index}
                                  className="text-primary hover:underline cursor-pointer"
                                >
                                  {match[0]}
                                </span>
                              );
                              
                              lastIndex = regex.lastIndex;
                            }
                            
                            // Ajouter le reste du texte
                            if (lastIndex < caption.length) {
                              parts.push(caption.substring(lastIndex));
                            }
                            
                            return parts.length > 0 ? parts : <span>{caption}</span>;
                          })()}
                        </div>

                        {/* Stats */}
                        <div className="pt-4 border-t border-border space-y-2">
                          <div className="flex items-center gap-4 text-sm">
                            <div className="flex items-center gap-1">
                              <Heart className="h-4 w-4 text-red-500" />
                              <span className="font-semibold">{selectedPost.like_count?.toLocaleString() || '0'}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <MessageCircle className="h-4 w-4" />
                              <span className="font-semibold">{selectedPost.comment_count?.toLocaleString() || '0'}</span>
                            </div>
                            {selectedPost.view_count && (
                              <div className="flex items-center gap-1">
                                <Eye className="h-4 w-4" />
                                <span className="font-semibold">{selectedPost.view_count.toLocaleString()}</span>
                              </div>
                            )}
                          </div>
                          <div className="text-xs text-muted-foreground">{relativeTime}</div>
                        </div>

                        {/* Comments */}
                        <div className="pt-4 border-t border-border space-y-3">
                          <h4 className="font-semibold text-sm mb-3">Comments</h4>
                          {[
                            {
                              id: '1',
                              user: 'fashionlover23',
                              avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=user1',
                              comment: 'Love this collection! When will it be available? 😍',
                              timestamp: '2h',
                              likes: 24,
                            },
                            {
                              id: '2',
                              user: 'styleicon',
                              avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=user2',
                              comment: 'Amazing quality! Just received my order 🎉',
                              timestamp: '5h',
                              likes: 18,
                            },
                          ].map((comment) => (
                            <div key={comment.id} className="flex items-start gap-3">
                              <img src={comment.avatar} alt={comment.user} className="w-8 h-8 rounded-full flex-shrink-0" />
                              <div className="flex-1">
                                <div className="mb-1">
                                  <span className="font-semibold text-sm">{comment.user}</span>
                                </div>
                                <div className="text-sm mb-2">{comment.comment}</div>
                                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                                  <span>{comment.timestamp}</span>
                                  <div className="flex items-center gap-1 cursor-pointer hover:opacity-80">
                                    <Heart className="h-3 w-3" />
                                    <span>{comment.likes}</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })()}
            </DialogContent>
          </Dialog>

          {/* Dialog: Edit project */}
          <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Edit project</DialogTitle>
                <DialogDescription>
                  Edit the project name and description
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    placeholder="Project name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={editDescription}
                    onChange={(e) => setEditDescription(e.target.value)}
                    placeholder="Project description"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={async () => {
                  try {
                    const token = localStorage.getItem('token');
                    const apiBase = getApiBase();
                    const url = apiBase ? `${apiBase}/api/v1/projects/${id}` : `/api/v1/projects/${id}`;
                    
                    const response = await fetch(url, {
                      method: 'PUT',
                      headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token || ''}`,
                      },
                      body: JSON.stringify({
                        name: editName,
                        description: editDescription,
                      }),
                    });

                    if (!response.ok) {
                      throw new Error('Failed to update project');
                    }

                    const updatedProject = await response.json();
                    applyProjectData(updatedProject);
                    setEditDialogOpen(false);
                    toast({
                      title: 'Success',
                      description: 'Project updated successfully',
                    });
                  } catch (error: any) {
                    toast({
                      title: 'Error',
                      description: error.message || 'Error during modification',
                      variant: 'destructive',
                    });
                  }
                }}>
                  Save
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Dialog: Delete project */}
          <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Delete project</DialogTitle>
                <DialogDescription>
                  Are you sure you want to delete the project "{project.name}"? This action is irreversible.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
                  Cancel
                </Button>
                <Button 
                  variant="destructive"
                  onClick={async () => {
                    try {
                      const token = localStorage.getItem('token');
                      const apiBase = getApiBase();
                      const url = apiBase ? `${apiBase}/api/v1/projects/${id}` : `/api/v1/projects/${id}`;
                      
                      const response = await fetch(url, {
                        method: 'DELETE',
                        headers: {
                          'Authorization': `Bearer ${token || ''}`,
                        },
                      });

                      if (!response.ok) {
                        throw new Error('Failed to delete project');
                      }

                      toast({
                        title: 'Success',
                        description: 'Project deleted successfully',
                      });
                      navigate('/projects');
                    } catch (error: any) {
                      toast({
                        title: 'Error',
                        description: error.message || 'Error during deletion',
                        variant: 'destructive',
                      });
                    }
                  }}
                >
                  Delete
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Tab 2: Analytics */}
          <TabsContent value="analytics" className="space-y-6">
            {/* Instagram Insights - Auto refresh avec les graphs */}
            <InstagramInsights projectId={project.id} triggerRefresh={refreshTrigger} />

            {/* Analytics Content - Charts */}
            <div className="grid gap-4 md:grid-cols-2">
              <Card className="bg-card border-border shadow-lg">
                <CardHeader>
                  <CardTitle className="text-white">Engagement Trends</CardTitle>
                  <CardDescription className="text-gray-400">
                    Daily engagement rate over time
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={engagementTrendData}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-gray-700" />
                      <XAxis
                        dataKey="date"
                        tickFormatter={(value) =>
                          new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
                        }
                        className="text-gray-400"
                      />
                      <YAxis className="text-gray-400" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '6px',
                        }}
                      />
                      <Area
                        type="monotone"
                        dataKey="engagement"
                        stroke="hsl(var(--primary))"
                        fill="hsl(var(--primary))"
                        fillOpacity={0.2}
                        name="Engagement Rate (%)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card className="bg-card border-border shadow-lg">
                <CardHeader>
                  <CardTitle className="text-white">Top Performing Creators</CardTitle>
                  <CardDescription className="text-gray-400">
                    By average engagement rate
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={topPerformingCreators} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" className="stroke-gray-700" />
                      <XAxis type="number" className="text-gray-400" />
                      <YAxis dataKey="username" type="category" width={100} className="text-gray-400" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '6px',
                        }}
                      />
                      <Bar dataKey="avg_engagement" fill="hsl(var(--accent))" name="Avg Engagement (%)" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            <Card className="bg-card border-border shadow-lg">
              <CardHeader>
                <CardTitle className="text-white">Reach & Impressions</CardTitle>
                <CardDescription className="text-gray-400">
                  Organic vs Paid reach over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart data={reachData}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-gray-700" />
                    <XAxis
                      dataKey="date"
                      tickFormatter={(value) =>
                        new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
                      }
                      className="text-gray-400"
                    />
                    <YAxis className="text-gray-400" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '6px',
                      }}
                    />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="organic"
                      stackId="1"
                      stroke="hsl(var(--primary))"
                      fill="hsl(var(--primary))"
                      fillOpacity={0.8}
                      name="Organic Reach"
                    />
                    <Area
                      type="monotone"
                      dataKey="paid"
                      stackId="1"
                      stroke="hsl(var(--accent))"
                      fill="hsl(var(--accent))"
                      fillOpacity={0.8}
                      name="Paid Reach"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

