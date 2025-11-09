import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { ProjectPanel } from '@/components/ProjectPanel';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
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
import { getApiBase } from '@/lib/api';

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [project, setProject] = useState<any>(null);
  const [posts, setPosts] = useState<any[]>([]);
  const [creators, setCreators] = useState<any[]>([]);
  const [niches, setNiches] = useState<any[]>([]);
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

  useEffect(() => {
    // Load project from API
    const loadProject = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/auth');
          return;
        }

        // Load project from API
        // Use Vercel proxy (relative path)
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
        
        setProject(projectData);
        
               // Extract creators from creators (new structure)
               const projectCreators = projectData.creators || [];
               const creatorsData = projectCreators.map((c: any) => ({
                 handle: c.creator_username,
                 platform: projectData.platforms[0] || 'instagram',
                 profile_picture: `https://api.dicebear.com/7.x/avataaars/svg?seed=${c.creator_username}`,
               }));
               setCreators(creatorsData);
               
               // If no creators but scope_query contains users, extract
               if (creatorsData.length === 0 && projectData.scope_query) {
                 const queryUsers = projectData.scope_query.split(',').map((q: string) => q.trim().replace('@', ''));
                 setCreators(queryUsers.map((username: string) => ({
                   handle: username,
                   platform: projectData.platforms[0] || 'instagram',
                   profile_picture: `https://api.dicebear.com/7.x/avataaars/svg?seed=${username}`,
                 })));
               }
        
        // Extract hashtags from scope_query or separate by comma
        const query = projectData.scope_query || '';
        const hashtagsFromQuery = query.split(',').map((q: string) => q.trim()).filter(Boolean);
        setNiches(hashtagsFromQuery.map((name: string, idx: number) => ({
          id: idx + 1,
          name: name.replace('#', ''),
          posts: 0,
          growth: '0%',
          engagement: 0,
        })));
        
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
    };

    if (id) {
      loadProject();
    }
  }, [id, navigate, toast]);

  const handleAddCreator = () => {
    toast({
      title: 'Add Creator',
      description: 'Feature coming soon',
    });
  };

  const handleAddNiche = () => {
    toast({
      title: 'Add Niche',
      description: 'Feature coming soon',
    });
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

              {/* Section: Creators (Right - 50%) */}
              {creators.length > 0 && (
                <Card className="bg-card border-border flex flex-col">
                  <CardHeader className="flex-shrink-0">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">Creators ({creators.length})</CardTitle>
                      <Select value={selectedPeriod} onValueChange={(value: 'day' | 'week' | 'month') => setSelectedPeriod(value)}>
                        <SelectTrigger className="w-32 h-8">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="day">Day</SelectItem>
                          <SelectItem value="week">Week</SelectItem>
                          <SelectItem value="month">Month</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </CardHeader>
                  <CardContent className="flex-1 overflow-hidden">
                    <div className="space-y-3 h-[400px] overflow-y-auto pr-2">
                      {creators.map((creator) => {
                        const stats = getCreatorStats(creator.handle, selectedPeriod);
                        return (
                          <div
                            key={creator.id || creator.handle}
                            className="flex items-center gap-3 p-2 rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
                            onClick={() => navigate(`/projects/${id}/creator/${creator.handle.replace('@', '')}`)}
                          >
                            <img
                              src={creator.profile_picture || `https://api.dicebear.com/7.x/avataaars/svg?seed=${creator.handle}`}
                              alt={creator.handle}
                              className="w-10 h-10 rounded-full flex-shrink-0"
                            />
                            <div className="flex-1 min-w-0">
                              <p className="font-medium text-sm truncate">{creator.handle}</p>
                              <div className="flex items-center gap-3 mt-1">
                                <p className="text-xs text-muted-foreground">
                                  {stats.followers.toLocaleString()} followers
                                </p>
                                <p className="text-xs text-muted-foreground">
                                  {stats.postsCount} {selectedPeriod === 'day' ? 'post' : selectedPeriod === 'week' ? 'posts/week' : 'posts/month'}
                                </p>
                              </div>
                            </div>
                            {creator.avg_engagement && (
                              <Badge variant="outline" className="flex-shrink-0">{creator.avg_engagement}%</Badge>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Section: Feed Posts */}
            <div>
              <h2 className="text-xl font-semibold mb-4">Posts Feed</h2>
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
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })
                ) : (
                  <div className="col-span-full text-center py-12 text-muted-foreground">
                    No posts found
                  </div>
                )}
              </div>
            </div>
          </TabsContent>

          {/* Tab 2: Grid - Posts table */}
          <TabsContent value="grid" className="space-y-6">
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle>Posts ({sortedPosts.length})</CardTitle>
                <CardDescription>
                  Tabular view of all posts with sorting and filters
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[60px]">Image</TableHead>
                        <TableHead 
                          className="cursor-pointer hover:bg-muted/50"
                          onClick={() => handleSort('username')}
                        >
                          <div className="flex items-center">
                            Auteur
                            {getSortIcon('username')}
                          </div>
                        </TableHead>
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
                            Date
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
                        <TableHead 
                          className="text-right cursor-pointer hover:bg-muted/50"
                          onClick={() => handleSort('score')}
                        >
                          <div className="flex items-center justify-end">
                            Score
                            {getSortIcon('score')}
                          </div>
                        </TableHead>
                        <TableHead className="text-right">Platform</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {sortedPosts.length > 0 ? (
                        sortedPosts.map((post: any) => {
                          const creator = creators.find((c: any) => c.handle?.toLowerCase() === post.username?.toLowerCase());
                          return (
                            <TableRow
                              key={post.id}
                              className="cursor-pointer hover:bg-muted/50"
                              onClick={() => {
                                setSelectedPost(post);
                                setPostDialogOpen(true);
                              }}
                            >
                              <TableCell>
                                <img
                                  src={post.media_url}
                                  alt={post.caption}
                                  className="w-12 h-12 rounded object-cover"
                                />
                              </TableCell>
                              <TableCell>
                                <div className="flex items-center gap-2">
                                  <img
                                    src={creator?.profile_picture || `https://api.dicebear.com/7.x/avataaars/svg?seed=${post.username}`}
                                    alt={post.username}
                                    className="w-6 h-6 rounded-full"
                                  />
                                  <span className="font-medium">{post.username}</span>
                                </div>
                              </TableCell>
                              <TableCell>
                                <p className="max-w-md line-clamp-2 text-sm">
                                  {post.caption || '-'}
                                </p>
                              </TableCell>
                              <TableCell>
                                {post.posted_at ? (
                                  <div className="text-sm">
                                    <div>{new Date(post.posted_at).toLocaleDateString('fr-FR')}</div>
                                    <div className="text-xs text-muted-foreground">
                                      {formatDistanceToNow(new Date(post.posted_at), { addSuffix: true, locale: fr })}
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
                                {post.score ? (
                                  <Badge variant={post.score > 7 ? 'default' : post.score > 4 ? 'secondary' : 'outline'}>
                                    {post.score.toFixed(1)}
                                  </Badge>
                                ) : (
                                  <span className="text-muted-foreground">-</span>
                                )}
                              </TableCell>
                              <TableCell className="text-right">
                                <Badge variant="outline">{post.platform || 'instagram'}</Badge>
                              </TableCell>
                            </TableRow>
                          );
                        })
                      ) : (
                        <TableRow>
                          <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                            No posts found
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

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
                  <label className="text-sm font-medium">Name</label>
                  <Input
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    placeholder="Project name"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Description</label>
                  <Input
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
                    setProject(updatedProject);
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

