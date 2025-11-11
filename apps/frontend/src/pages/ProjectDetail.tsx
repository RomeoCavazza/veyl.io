import { useState, useEffect, useMemo, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { ProjectPanel } from '@/components/ProjectPanel';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
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
import { Hash, User, Plus, X, Heart, MessageCircle, Eye, ArrowLeft, Bell, AtSign, Trash2, ExternalLink, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
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
import { getApiBase, addProjectCreator, removeProjectCreator, addProjectHashtag, removeProjectHashtag } from '@/lib/api';

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
  const [selectedPeriod, setSelectedPeriod] = useState<'day' | 'week' | 'month'>('week');
  const [sortColumn, setSortColumn] = useState<string>('posted_at');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

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
      const updatedProject = await addProjectHashtag(id, {
        hashtag,
        platform: newHashtagPlatform,
      });
      applyProjectData(updatedProject);
      setAddHashtagOpen(false);
      setNewHashtagName('');
      toast({ title: 'Hashtag added', description: `#${hashtag} linked to the project.` });
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

  // Calcul des statistiques de posts basées sur les dates
  const calculatePostStats = () => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekAgo = new Date(today);
    weekAgo.setDate(weekAgo.getDate() - 7);
    const monthAgo = new Date(today);
    monthAgo.setMonth(monthAgo.getMonth() - 1);

    const postsToday = posts.filter(post => {
      if (!post.posted_at) return false;
      const postDate = new Date(post.posted_at);
      return postDate >= today;
    }).length;

    const postsThisWeek = posts.filter(post => {
      if (!post.posted_at) return false;
      const postDate = new Date(post.posted_at);
      return postDate >= weekAgo;
    }).length;

    const postsThisMonth = posts.filter(post => {
      if (!post.posted_at) return false;
      const postDate = new Date(post.posted_at);
      return postDate >= monthAgo;
    }).length;

    // If no dates, use approximations
    if (posts.length > 0 && !posts.some(p => p.posted_at)) {
      return {
        perDay: Math.round(posts.length / 7) || 0,
        perWeek: posts.length,
        perMonth: posts.length * 4,
      };
    }

    return {
      perDay: postsToday,
      perWeek: postsThisWeek,
      perMonth: postsThisMonth,
    };
  };

  const postStats = calculatePostStats();

  // Fonction pour calculer les stats d'un creator selon la période
  const getCreatorStats = (creatorHandle: string, period: 'day' | 'week' | 'month') => {
    const now = new Date();
    let startDate = new Date();
    
    if (period === 'day') {
      startDate.setHours(0, 0, 0, 0);
    } else if (period === 'week') {
      startDate.setDate(startDate.getDate() - 7);
    } else if (period === 'month') {
      startDate.setMonth(startDate.getMonth() - 1);
    }
    
    // Count creator posts in the period
    const creatorPosts = posts.filter((post: any) => {
      if (post.username?.toLowerCase() !== creatorHandle.toLowerCase()) return false;
      if (!post.posted_at) return true; // If no date, include
      const postDate = new Date(post.posted_at);
      return postDate >= startDate;
    });
    
    // Trouver le creator pour avoir les followers
    const creator = creators.find((c: any) => c.handle?.toLowerCase() === creatorHandle.toLowerCase());
    
    return {
      postsCount: creatorPosts.length,
      followers: creator?.followers || 0,
    };
  };

  // Function to sort posts
  const sortedPosts = useMemo(() => {
    const sorted = [...posts];
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
            creators={creators}
            onEdit={() => {
              setEditName(project.name || '');
              setEditDescription(project.description || '');
              setEditDialogOpen(true);
            }}
            onDelete={() => setDeleteDialogOpen(true)}
          />
          <div className="space-y-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between py-4">
                <CardTitle className="text-lg">Hashtags</CardTitle>
                <Button size="sm" onClick={handleAddNiche}>
                  <Plus className="h-4 w-4 mr-1" />
                  Add hashtag
                </Button>
              </CardHeader>
              <CardContent>
                {hashtagLinks.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No hashtags linked yet.</p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Hashtag</TableHead>
                        <TableHead>Platform</TableHead>
                        <TableHead>Added</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {hashtagLinks.map((link: any) => (
                        <TableRow key={link.link_id ?? link.id}>
                          <TableCell className="font-medium">#{link.name}</TableCell>
                          <TableCell className="capitalize">{link.platform || 'instagram'}</TableCell>
                          <TableCell className="text-muted-foreground">
                            {link.added_at ? formatDistanceToNow(new Date(link.added_at), { addSuffix: true, locale: fr }) : '—'}
                          </TableCell>
                          <TableCell className="text-right">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleRemoveHashtagLink(link.link_id ?? link.id)}
                              title="Remove hashtag"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between py-4">
                <CardTitle className="text-lg">Creators</CardTitle>
                <Button size="sm" onClick={handleAddCreator}>
                  <Plus className="h-4 w-4 mr-1" />
                  Add creator
                </Button>
              </CardHeader>
              <CardContent>
                {creatorLinks.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No creators linked yet.</p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Creator</TableHead>
                        <TableHead>Platform</TableHead>
                        <TableHead>Added</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {creatorLinks.map((link: any) => (
                        <TableRow key={link.id}>
                          <TableCell className="font-medium">@{link.creator_username}</TableCell>
                          <TableCell className="capitalize">{link.platform || 'instagram'}</TableCell>
                          <TableCell className="text-muted-foreground">
                            {link.added_at ? formatDistanceToNow(new Date(link.added_at), { addSuffix: true, locale: fr }) : '—'}
                          </TableCell>
                          <TableCell className="text-right">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleRemoveCreatorLink(link.id)}
                              title="Remove creator"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="watchlist" className="space-y-4">
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

          {/* Tab 1: Watchlist - Feed + Creators + Hashtags/Commentaires/Mentions */}
          <TabsContent value="watchlist" className="space-y-6">
            {/* Section: Feed Posts */}
            <div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {posts.length > 0 ? (
                  posts.map((post) => {
                    const creator = creators.find(c => c.handle === post.username);
                    return (
                      <Card 
                        key={post.id} 
                        className="overflow-hidden cursor-pointer hover:border-primary transition-colors"
                        onClick={() => {
                          setSelectedPost(post);
                          setPostDialogOpen(true);
                        }}
                      >
                        <div className="relative">
                          <img
                            src={post.media_url}
                            alt={post.caption}
                            className="w-full h-64 object-cover"
                          />
                          <div className="absolute top-2 right-2 flex gap-2">
                            <Badge variant="secondary" className="bg-black/50 text-white">
                              {post.platform}
                            </Badge>
                          </div>
                        </div>
                        <CardContent className="p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <img
                              src={creator?.profile_picture || `https://api.dicebear.com/7.x/avataaars/svg?seed=${post.username}`}
                              alt={post.username || 'creator'}
                              className="w-6 h-6 rounded-full flex-shrink-0"
                            />
                            <span 
                              className="text-sm font-medium hover:text-primary cursor-pointer"
                              onClick={(e) => {
                                e.stopPropagation();
                                navigate(`/projects/${id}/creator/${post.username}`);
                              }}
                            >
                              {post.username}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                            {post.caption}
                          </p>
                          <div className="flex items-center gap-4 text-sm">
                            <div className="flex items-center gap-1">
                              <Heart className="h-4 w-4" />
                              <span>{post.like_count?.toLocaleString() || 0}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <MessageCircle className="h-4 w-4" />
                              <span>{post.comment_count?.toLocaleString() || 0}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Eye className="h-4 w-4" />
                              <span>{post.view_count?.toLocaleString() || 0}</span>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })
                ) : (
                  <Card className="col-span-full">
                    <CardContent className="p-10 text-center text-muted-foreground">
                      No posts yet. Add creators or hashtags to start tracking content.
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>

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
                </div>
                <div className="space-y-2">
                  <Label>Platform</Label>
                  <Select value={newCreatorPlatform} onValueChange={setNewCreatorPlatform}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select platform" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="instagram">Instagram</SelectItem>
                      <SelectItem value="facebook">Facebook</SelectItem>
                      <SelectItem value="tiktok">TikTok</SelectItem>
                    </SelectContent>
                  </Select>
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
                <div className="space-y-2">
                  <Label>Platform</Label>
                  <Select value={newHashtagPlatform} onValueChange={setNewHashtagPlatform}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select platform" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="instagram">Instagram</SelectItem>
                      <SelectItem value="facebook">Facebook</SelectItem>
                      <SelectItem value="tiktok">TikTok</SelectItem>
                    </SelectContent>
                  </Select>
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
                const creator = creators.find(c => c.handle === selectedPost.username);
                const profilePic = creator?.profile_picture || `https://api.dicebear.com/7.x/avataaars/svg?seed=${selectedPost.username}`;
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
                            className="w-10 h-10 rounded-full cursor-pointer hover:opacity-80"
                            onClick={() => {
                              setPostDialogOpen(false);
                              navigate(`/projects/${id}/creator/${selectedPost.username}`);
                            }}
                          />
                          <div>
                            <div 
                              className="font-semibold text-sm cursor-pointer hover:opacity-80"
                              onClick={() => {
                                setPostDialogOpen(false);
                                navigate(`/projects/${id}/creator/${selectedPost.username}`);
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
            {/* Layout 50/50 : Project Panel + Chart/Creators */}
            <div className="grid gap-4 md:grid-cols-2">
              {/* Project Panel (Left - 50%) */}
              <ProjectPanel
                project={project}
                creators={creators}
                onEdit={() => {
                  setEditName(project.name || '');
                  setEditDescription(project.description || '');
                  setEditDialogOpen(true);
                }}
                onDelete={() => setDeleteDialogOpen(true)}
              />

              {/* Content Type Distribution Chart (Right - 50%) */}
              <Card className="bg-card border-border shadow-lg">
                <CardHeader>
                  <CardTitle className="text-white">Content Type Distribution</CardTitle>
                  <CardDescription className="text-gray-400">
                    Breakdown by media type
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '6px',
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

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

