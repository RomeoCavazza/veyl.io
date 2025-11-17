import { useState, useEffect, useMemo, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { ProjectPanel } from '@/components/ProjectPanel';
import { InstagramInsights } from '@/components/InstagramInsights';
import { ProjectPostsList } from '@/components/ProjectPostsList';
import { ProjectPostsTable } from '@/components/ProjectPostsTable';
import { PostDetailDialog } from '@/components/PostDetailDialog';
import { ProjectAnalytics } from '@/components/ProjectAnalytics';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Plus, X, Heart, MessageCircle, Eye, ArrowLeft, Bell, AtSign, Trash2, ExternalLink, ArrowUpDown, ArrowUp, ArrowDown, TrendingUp, RefreshCcw, Code2, Sparkles } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

import { getProject, updateProject, deleteProject, addProjectCreator, removeProjectCreator, addProjectHashtag, removeProjectHashtag, getProjectPosts, fetchMetaIGPublic, fetchTikTokVideos, linkProjectHashtagPosts, searchCreators, type Project } from '@/lib/api';
import type { ProjectPost } from '@/types/project';
import type { CreatorLink, HashtagLink, CreatorCard, HashtagEntry, ProjectData } from '@/types/project';
import { getErrorMessage } from '@/lib/utils';

const PLATFORM_OPTIONS = ['instagram', 'facebook', 'tiktok'] as const;
const formatPlatformLabel = (value: string) => value.charAt(0).toUpperCase() + value.slice(1);

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [project, setProject] = useState<Project | null>(null);
  const [posts, setPosts] = useState<ProjectPost[]>([]);
  const [creators, setCreators] = useState<CreatorCard[]>([]);
  const [creatorLinks, setCreatorLinks] = useState<CreatorLink[]>([]);
  const [hashtagLinks, setHashtagLinks] = useState<HashtagLink[]>([]);
  const [addCreatorOpen, setAddCreatorOpen] = useState(false);
  const [newCreatorUsername, setNewCreatorUsername] = useState('');
  const [newCreatorPlatform, setNewCreatorPlatform] = useState('instagram');
  const [isSavingCreator, setIsSavingCreator] = useState(false);
  const [creatorSuggestions, setCreatorSuggestions] = useState<string[]>([]);
  const [addHashtagOpen, setAddHashtagOpen] = useState(false);
  const [newHashtagName, setNewHashtagName] = useState('');
  const [isSavingHashtag, setIsSavingHashtag] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedPost, setSelectedPost] = useState<ProjectPost | null>(null);
  const [postDialogOpen, setPostDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [editName, setEditName] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [sortColumn, setSortColumn] = useState<string>('posted_at');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [refreshTrigger, setRefreshTrigger] = useState(Date.now());
  const [embedDialogOpen, setEmbedDialogOpen] = useState(false);
  const [selectedPlatformFilter, setSelectedPlatformFilter] = useState<string | 'all'>('all');
  const [isFetchingMeta, setIsFetchingMeta] = useState(false);
  const [isFetchingTikTok, setIsFetchingTikTok] = useState(false);

  const reachData: Array<{ date: string; organic: number; paid: number }> = [];
  const engagementTrendData: Array<{ date: string; engagement: number; reach: number; impressions: number }> = [];
  const topPerformingCreators: Array<{ username: string; posts: number; avg_engagement: number; total_reach: number }> = [];

  const applyProjectData = useCallback((projectData: Project) => {
    setProject(projectData);

    const projectCreators = projectData.creators || [];
    setCreatorLinks(projectCreators);
    const creatorCards: CreatorCard[] = projectCreators.map((c: CreatorLink) => ({
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
    const hashtagEntries: HashtagEntry[] = projectHashtags.map((link: HashtagLink, idx: number) => ({
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
        // Niches are now handled via hashtagLinks
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
      
      // Fetch Meta si nécessaire - NE PAS FILTRER PAR PLATFORM (comme Search)
      // Le hashtag peut être créé avec n'importe quelle platform mais on veut fetcher Meta
      if (shouldFetchMeta) {
        // Prendre TOUS les hashtags (pas de filtre par platform), comme dans Search
        const allHashtags = projectHashtags.filter((h: HashtagLink) => h.name);
        
        if (allHashtags.length > 0) {
          for (const hashtag of allHashtags.slice(0, 3)) {
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
            } catch (error: unknown) {
              console.error(`❌ [FETCH] Meta API FAILED for #${hashtag.name}:`, getErrorMessage(error));
              // Continue avec les autres hashtags
            }
          }
        }
      }
      
      // Fetch TikTok si nécessaire - NE PAS FILTRER PAR PLATFORM (comme Search)
      // Le hashtag peut être créé avec platform='instagram' mais on veut quand même fetcher TikTok
      if (shouldFetchTikTok) {
        // Prendre TOUS les hashtags (pas de filtre par platform), comme dans Search
        const allHashtags = projectHashtags.filter((h: HashtagLink) => h.name);
        
        if (allHashtags.length > 0) {
          for (const hashtag of allHashtags.slice(0, 3)) {
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
            } catch (error: unknown) {
              console.error(`❌ [FETCH] TikTok API FAILED for #${hashtag.name}:`, getErrorMessage(error));
              // Continue avec les autres hashtags - on fera le re-link après pour charger depuis DB
            }
          }
        } else {
          // Pas de hashtags trouvés
          console.log(`⚠️ [FETCH] No hashtags found in project`);
        }
      }
      
      // 🔗 RE-LINK: Toujours re-linker les posts au hashtag après le fetch (même si API échoué)
      // Cela permet de charger les posts depuis la DB même si l'API a échoué
      const allHashtags = projectHashtags.filter((h: HashtagLink) => h.name);
      for (const hashtag of allHashtags.slice(0, 3)) {
        const hashtagLink = projectHashtags.find((h: HashtagLink) => 
          (h.name?.toLowerCase() === hashtag.name?.toLowerCase() || 
           h.name?.toLowerCase() === `#${hashtag.name?.toLowerCase()}`)
        );
        
        if (hashtagLink) {
          const linkId = hashtagLink.link_id || hashtagLink.id;
          if (linkId) {
            try {
              console.log(`🔗 [RE-LINK] Re-linking posts to hashtag #${hashtag.name} (link_id: ${linkId})...`);
              if (id) {
                const linkResult = await linkProjectHashtagPosts(id, linkId, 100);
                console.log(`✅ [RE-LINK] Re-linked ${linkResult.newly_linked || 0} posts to #${hashtag.name}`);
              }
            } catch (error: unknown) {
              console.error(`❌ [RE-LINK] Error re-linking posts:`, getErrorMessage(error));
              // Continue même si le re-link échoue
            }
          }
        }
      }

      // 💾 FALLBACK DB: Toujours recharger les posts depuis la DB (comme Search)
      // Même si l'API a échoué, les posts de la DB devraient apparaître après le re-link
      const platformFilter = selectedPlatformFilter === 'all' ? undefined : selectedPlatformFilter;
      await fetchProjectPosts(platformFilter);
      setRefreshTrigger(Date.now());
      
      if (fetchedCount === 0 && allHashtags.length === 0) {
        toast({
          title: 'No hashtags found',
          description: `Add ${shouldFetchMeta && shouldFetchTikTok ? 'Meta or TikTok' : shouldFetchMeta ? 'Meta' : 'TikTok'} hashtags to fetch posts`,
          variant: 'destructive',
        });
        return;
      }
      
      const platformText = shouldFetchMeta && shouldFetchTikTok ? 'Meta and TikTok' : shouldFetchMeta ? 'Meta' : 'TikTok';
      toast({
        title: 'Posts fetched',
        description: `Posts from ${platformText} API have been added to the project`,
      });
    } catch (error: unknown) {
      toast({
        title: 'Error fetching posts',
        description: getErrorMessage(error),
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
        const projectData = await getProject(id);
        console.log('Project loaded:', projectData);
        applyProjectData(projectData);
    } catch (error: unknown) {
      console.error('Error loading project:', error);
      toast({
        title: 'Error',
        description: getErrorMessage(error),
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
      } catch (error: unknown) {
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
    } catch (error: unknown) {
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
      let updatedProject;
      let hashtagAlreadyExists = false;
      
      try {
        updatedProject = await addProjectHashtag(id, {
          hashtag,
          platform: 'instagram', // Le backend auto-link sur toutes les plateformes
        });
        applyProjectData(updatedProject);
      } catch (error: unknown) {
        // Si le hashtag existe déjà (409), on continue quand même pour faire le fetch + re-link
        const errorMsg = getErrorMessage(error);
        if (errorMsg.includes('409') || errorMsg.includes('already linked')) {
          hashtagAlreadyExists = true;
          console.log(`ℹ️ [HASHTAG] Hashtag #${hashtag} already exists, will fetch and re-link anyway`);
          // Recharger le projet pour avoir les hashtags à jour
          await fetchProject();
          updatedProject = project;
        } else {
          throw error; // Re-lancer les autres erreurs
        }
      }
      
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
          .catch((error: unknown) => {
            console.error(`❌ [AUTO-FETCH] Meta API FAILED for #${hashtag}:`, getErrorMessage(error));
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
          .catch((error: unknown) => {
            console.error(`❌ [AUTO-FETCH] TikTok API FAILED for #${hashtag}:`, getErrorMessage(error));
          })
      );
      
      // Attendre que tous les fetches soient terminés (en parallèle)
      await Promise.allSettled(fetchPromises);
      
      // 🔗 RE-LINK: Après le fetch, re-linker les posts au hashtag (car les nouveaux posts ne sont pas auto-linkés)
      // Trouver le hashtag (qu'on vient d'ajouter ou qui existait déjà) pour le re-linker
      await fetchProject(); // Recharger pour avoir les hashtags à jour
      const updatedHashtagLinks = project?.hashtags || hashtagLinks || [];
      const addedHashtagLink = updatedHashtagLinks.find((h: HashtagLink) => 
        h.name?.toLowerCase() === hashtag.toLowerCase() || 
        h.name?.toLowerCase() === `#${hashtag.toLowerCase()}`
      );
      
      // Utiliser link_id (ID du ProjectHashtag) et non id (ID du Hashtag)
      const linkId = addedHashtagLink?.link_id || addedHashtagLink?.id;
      if (linkId) {
        try {
          console.log(`🔗 [RE-LINK] Re-linking posts to hashtag #${hashtag} (link_id: ${linkId})...`);
          if (id) {
            const linkResult = await linkProjectHashtagPosts(id, linkId, 100);
            console.log(`✅ [RE-LINK] Re-linked ${linkResult.newly_linked || 0} posts to #${hashtag}`);
          }
        } catch (error: unknown) {
          console.error(`❌ [RE-LINK] Error re-linking posts:`, error.message);
          // Continue même si le re-link échoue
        }
      }
      
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
    } catch (error: unknown) {
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
    } catch (error: unknown) {
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
    return posts.filter((post: ProjectPost) => {
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
    sorted.sort((a: ProjectPost, b: ProjectPost) => {
      let aVal: unknown = a[sortColumn as keyof ProjectPost];
      let bVal: unknown = b[sortColumn as keyof ProjectPost];

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
        const data = await searchCreators(newCreatorUsername, 10);
        // Filtrer ceux déjà liés au projet
        const linkedUsernames = new Set(creatorLinks.map((link: CreatorLink) => link.creator_username));
        const filtered = data.creators
          .map((c: { username: string }) => c.username)
          .filter((username: string) => !linkedUsernames.has(username));
        setCreatorSuggestions(filtered);
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
                      {hashtagLinks.map((link: HashtagLink) => (
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
                      {creatorLinks.map((link: CreatorLink) => (
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
            <ProjectPostsList
              posts={sortedPosts}
              creators={creators}
              selectedPlatformFilter={selectedPlatformFilter}
              onPostClick={(post) => {
                setSelectedPost(post);
                setPostDialogOpen(true);
              }}
              onEmbedClick={(post) => {
                setSelectedPost(post);
                setEmbedDialogOpen(true);
              }}
            />
          </TabsContent>

          {/* Tab 3: Grid - Table View */}
          <TabsContent value="grid" className="space-y-4">
            <ProjectPostsTable
              posts={sortedPosts}
              selectedPlatformFilter={selectedPlatformFilter}
              sortColumn={sortColumn}
              sortDirection={sortDirection}
              onSort={handleSort}
              onPostClick={(post) => {
                setSelectedPost(post);
                setPostDialogOpen(true);
              }}
            />
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

          <PostDetailDialog
            post={selectedPost}
            projectId={id || ''}
            open={postDialogOpen}
            onOpenChange={setPostDialogOpen}
          />

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
                    if (!id) return;
                    const updatedProject = await updateProject(id, {
                      name: editName,
                      description: editDescription,
                    });
                    applyProjectData(updatedProject);
                    setEditDialogOpen(false);
                    toast({
                      title: 'Success',
                      description: 'Project updated successfully',
                    });
                  } catch (error: unknown) {
                    toast({
                      title: 'Error',
                      description: getErrorMessage(error),
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
                      if (!id) return;
                      await deleteProject(id);
                      toast({
                        title: 'Success',
                        description: 'Project deleted successfully',
                      });
                      navigate('/projects');
                    } catch (error: unknown) {
                      toast({
                        title: 'Error',
                        description: getErrorMessage(error),
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
            <InstagramInsights projectId={project.id} triggerRefresh={refreshTrigger} />
            <ProjectAnalytics
              engagementTrendData={engagementTrendData}
              topPerformingCreators={topPerformingCreators}
              reachData={reachData}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

