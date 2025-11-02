import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Hash, User, Plus, X, Heart, MessageCircle, Eye, ArrowLeft, Settings, Bell, AtSign, Trash2, ExternalLink, Edit, Copy } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';
import { getFakeProject, getFakeProjectPosts, fakeCreators, fakePosts } from '@/lib/fakeData';
import { engagementTrendData, topPerformingCreators } from '@/lib/mockData';
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

// Importer getApiBase depuis api.ts
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

  // Mock data for charts
  const pieData = [
    { name: 'Images', value: 45, color: 'hsl(var(--primary))' },
    { name: 'Videos', value: 35, color: 'hsl(var(--accent))' },
    { name: 'Carousels', value: 20, color: 'hsl(var(--success))' },
  ];

  const reachData = [
    { date: '2025-01-15', organic: 45000, paid: 15000 },
    { date: '2025-01-16', organic: 52000, paid: 18000 },
    { date: '2025-01-17', organic: 48000, paid: 22000 },
    { date: '2025-01-18', organic: 61000, paid: 25000 },
    { date: '2025-01-19', organic: 58000, paid: 28000 },
    { date: '2025-01-20', organic: 72000, paid: 32000 },
    { date: '2025-01-21', organic: 68000, paid: 30000 },
  ];

  useEffect(() => {
    // Charger projet depuis API
    const loadProject = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/auth');
          return;
        }

        // Charger projet depuis API
        // Utiliser le proxy Vercel (chemin relatif)
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
        
               // Extraire créateurs depuis creators (nouvelle structure)
               const projectCreators = projectData.creators || [];
               const creatorsData = projectCreators.map((c: any) => ({
                 handle: c.creator_username,
                 platform: projectData.platforms[0] || 'instagram',
                 profile_picture: `https://api.dicebear.com/7.x/avataaars/svg?seed=${c.creator_username}`,
               }));
               setCreators(creatorsData);
               
               // Si pas de créateurs mais scope_query contient des users, extraire
               if (creatorsData.length === 0 && projectData.scope_query) {
                 const queryUsers = projectData.scope_query.split(',').map((q: string) => q.trim().replace('@', ''));
                 setCreators(queryUsers.map((username: string) => ({
                   handle: username,
                   platform: projectData.platforms[0] || 'instagram',
                   profile_picture: `https://api.dicebear.com/7.x/avataaars/svg?seed=${username}`,
                 })));
               }
        
        // Extraire hashtags depuis scope_query ou séparer par virgule
        const query = projectData.scope_query || '';
        const hashtagsFromQuery = query.split(',').map((q: string) => q.trim()).filter(Boolean);
        setNiches(hashtagsFromQuery.map((name: string, idx: number) => ({
          id: idx + 1,
          name: name.replace('#', ''),
          posts: 0,
          growth: '0%',
          engagement: 0,
        })));
        
        // Pour l'instant, utiliser fake posts (à remplacer par vraie API)
        const projectPosts = getFakeProjectPosts(id || '');
        setPosts(projectPosts);
        
      } catch (error: any) {
        console.error('Error loading project:', error);
        toast({
          title: 'Error',
          description: error.message || 'Failed to load project',
          variant: 'destructive',
        });
        // Fallback sur fake data
        const fakeProject = getFakeProject(id || '');
        if (fakeProject) {
          setProject(fakeProject);
          setPosts(getFakeProjectPosts(id || ''));
          setCreators(fakeCreators);
          setNiches([
            { id: 1, name: 'fashion', posts: 1247, growth: '+34%', engagement: 8.2 },
            { id: 2, name: 'makeup', posts: 892, growth: '+28%', engagement: 7.5 },
            { id: 3, name: 'fitness', posts: 1456, growth: '+22%', engagement: 9.1 },
          ]);
        }
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

    // Si pas de dates, utiliser des approximations
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
            <TabsTrigger value="analytics">
              Analytics
            </TabsTrigger>
          </TabsList>

          {/* Tab 1: Watchlist - Feed + Creators + Hashtags/Commentaires/Mentions */}
          <TabsContent value="watchlist" className="space-y-6">
            {/* Panneau Projet */}
            <Card className="bg-card border-border">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle>{project.name}</CardTitle>
                    {project.description && (
                      <CardDescription>{project.description}</CardDescription>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={project.status === 'active' ? 'default' : 'secondary'}>
                      {project.status}
                    </Badge>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <Settings className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => {
                          setEditName(project.name || '');
                          setEditDescription(project.description || '');
                          setEditDialogOpen(true);
                        }}>
                          <Edit className="h-4 w-4 mr-2" />
                          Modifier le projet
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={async () => {
                          try {
                            const token = localStorage.getItem('token');
                            const apiBase = getApiBase();
                            const url = apiBase ? `${apiBase}/api/v1/projects` : `/api/v1/projects`;
                            
                            const response = await fetch(url, {
                              method: 'POST',
                              headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${token || ''}`,
                              },
                              body: JSON.stringify({
                                name: `${project.name} (copie)`,
                                description: project.description,
                                platforms: project.platforms || [],
                                scope_type: project.scope_type,
                                scope_query: project.scope_query,
                                hashtag_names: project.hashtag_names || [],
                                creator_usernames: project.creator_usernames || [],
                              }),
                            });

                            if (!response.ok) {
                              throw new Error('Failed to duplicate project');
                            }

                            const duplicatedProject = await response.json();
                            toast({
                              title: 'Succès',
                              description: 'Projet dupliqué avec succès',
                            });
                            navigate(`/projects/${duplicatedProject.id}`);
                          } catch (error: any) {
                            toast({
                              title: 'Erreur',
                              description: error.message || 'Erreur lors de la duplication',
                              variant: 'destructive',
                            });
                          }
                        }}>
                          <Copy className="h-4 w-4 mr-2" />
                          Dupliquer le projet
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem 
                          onClick={() => setDeleteDialogOpen(true)}
                          className="text-destructive focus:text-destructive"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Supprimer le projet
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Créateurs</p>
                    <p className="text-2xl font-bold text-primary">{creators.length}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Posts (Jour)</p>
                    <p className="text-2xl font-bold text-primary">{postStats.perDay}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Posts (Semaine)</p>
                    <p className="text-2xl font-bold text-primary">{postStats.perWeek}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Posts (Mois)</p>
                    <p className="text-2xl font-bold text-primary">{postStats.perMonth}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Section: Creators */}
            {creators.length > 0 && (
              <div>
                <h2 className="text-xl font-semibold mb-4">Creators ({creators.length})</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {creators.map((creator) => (
                    <Card
                      key={creator.id || creator.handle}
                      className="cursor-pointer hover:border-primary transition-colors"
                      onClick={() => navigate(`/projects/${id}/creator/${creator.handle.replace('@', '')}`)}
                    >
                      <CardContent className="p-6">
                        <div className="flex flex-col items-center text-center gap-4">
                          <img
                            src={creator.profile_picture || `https://api.dicebear.com/7.x/avataaars/svg?seed=${creator.handle}`}
                            alt={creator.handle}
                            className="w-20 h-20 rounded-full"
                          />
                          <div>
                            <h3 className="font-semibold">{creator.handle}</h3>
                            {creator.followers && (
                              <p className="text-sm text-muted-foreground">
                                {creator.followers.toLocaleString()} followers
                              </p>
                            )}
                          </div>
                          {creator.avg_engagement && (
                            <div className="w-full p-3 bg-primary/10 rounded-lg">
                              <div className="text-center">
                                <span className="font-medium">{creator.avg_engagement}%</span>
                                <p className="text-xs text-muted-foreground">Engagement</p>
                              </div>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

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
                            {creator?.profile_picture && (
                              <img
                                src={creator.profile_picture}
                                alt={creator.handle}
                                className="w-6 h-6 rounded-full"
                              />
                            )}
                            <span 
                              className="text-sm font-medium hover:text-primary"
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
                          <div className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-4">
                              <div className="flex items-center gap-1">
                                <Heart className="h-4 w-4" />
                                <span>{post.like_count?.toLocaleString() || 0}</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <MessageCircle className="h-4 w-4" />
                                <span>{post.comment_count?.toLocaleString() || 0}</span>
                              </div>
                            </div>
                            <Button variant="ghost" size="sm">
                              <Eye className="h-4 w-4" />
                            </Button>
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
                    {/* Photo à gauche */}
                    <div className="flex-shrink-0 w-full md:w-[60%] bg-black flex items-center justify-center">
                      <img
                        src={selectedPost.media_url}
                        alt={selectedPost.caption}
                        className="max-h-[90vh] w-full object-contain"
                      />
                    </div>

                    {/* Panneau infos à droite */}
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
                        <div className="flex items-start gap-3">
                          <img src={profilePic} alt={selectedPost.username} className="w-8 h-8 rounded-full flex-shrink-0" />
                          <div className="flex-1">
                            <span className="font-semibold text-sm mr-2">{selectedPost.username}</span>
                            <span className="text-sm">{caption}</span>
                          </div>
                        </div>

                        {/* Hashtags */}
                        {hashtags.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {hashtags.map((tag: string, idx: number) => {
                              const tagText = tag.startsWith('#') ? tag : `#${tag}`;
                              return (
                                <Badge key={idx} variant="secondary" className="cursor-pointer hover:bg-primary/20">
                                  <Hash className="h-3 w-3 mr-1" />
                                  {tagText.replace('#', '')}
                                </Badge>
                              );
                            })}
                          </div>
                        )}

                        {/* Mentions */}
                        {mentions.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {mentions.map((mention: string, idx: number) => {
                              const mentionText = mention.startsWith('@') ? mention : `@${mention}`;
                              return (
                                <Badge key={idx} variant="outline" className="cursor-pointer hover:bg-primary/20">
                                  <AtSign className="h-3 w-3 mr-1" />
                                  {mentionText.replace('@', '')}
                                </Badge>
                              );
                            })}
                          </div>
                        )}

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

                        {/* Commentaires */}
                        <div className="pt-4 border-t border-border space-y-3">
                          <h4 className="font-semibold text-sm mb-3">Commentaires</h4>
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
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="font-semibold text-sm">{comment.user}</span>
                                  <span className="text-sm">{comment.comment}</span>
                                </div>
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

          {/* Dialog: Modifier le projet */}
          <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Modifier le projet</DialogTitle>
                <DialogDescription>
                  Modifiez le nom et la description du projet
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Nom</label>
                  <Input
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    placeholder="Nom du projet"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Description</label>
                  <Input
                    value={editDescription}
                    onChange={(e) => setEditDescription(e.target.value)}
                    placeholder="Description du projet"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setEditDialogOpen(false)}>
                  Annuler
                </Button>
                <Button onClick={async () => {
                  try {
                    const token = localStorage.getItem('token');
                    const apiBase = getApiBase();
                    const url = apiBase ? `${apiBase}/api/v1/projects/${id}` : `/api/v1/projects/${id}`;
                    
                    const response = await fetch(url, {
                      method: 'PATCH',
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
                      title: 'Succès',
                      description: 'Projet modifié avec succès',
                    });
                  } catch (error: any) {
                    toast({
                      title: 'Erreur',
                      description: error.message || 'Erreur lors de la modification',
                      variant: 'destructive',
                    });
                  }
                }}>
                  Enregistrer
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Dialog: Supprimer le projet */}
          <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Supprimer le projet</DialogTitle>
                <DialogDescription>
                  Êtes-vous sûr de vouloir supprimer le projet "{project.name}" ? Cette action est irréversible.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
                  Annuler
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
                        title: 'Succès',
                        description: 'Projet supprimé avec succès',
                      });
                      navigate('/projects');
                    } catch (error: any) {
                      toast({
                        title: 'Erreur',
                        description: error.message || 'Erreur lors de la suppression',
                        variant: 'destructive',
                      });
                    }
                  }}
                >
                  Supprimer
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Tab 2: Analytics */}
          <TabsContent value="analytics" className="space-y-6">
            {/* Panneau Projet (identique à Watchlist) */}
            <Card className="bg-card border-border">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle>{project.name}</CardTitle>
                    {project.description && (
                      <CardDescription>{project.description}</CardDescription>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={project.status === 'active' ? 'default' : 'secondary'}>
                      {project.status}
                    </Badge>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <Settings className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => {
                          setEditName(project.name || '');
                          setEditDescription(project.description || '');
                          setEditDialogOpen(true);
                        }}>
                          <Edit className="h-4 w-4 mr-2" />
                          Modifier le projet
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={async () => {
                          try {
                            const token = localStorage.getItem('token');
                            const apiBase = getApiBase();
                            const url = apiBase ? `${apiBase}/api/v1/projects` : `/api/v1/projects`;
                            
                            const response = await fetch(url, {
                              method: 'POST',
                              headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${token || ''}`,
                              },
                              body: JSON.stringify({
                                name: `${project.name} (copie)`,
                                description: project.description,
                                platforms: project.platforms || [],
                                scope_type: project.scope_type,
                                scope_query: project.scope_query,
                                hashtag_names: project.hashtag_names || [],
                                creator_usernames: project.creator_usernames || [],
                              }),
                            });

                            if (!response.ok) {
                              throw new Error('Failed to duplicate project');
                            }

                            const duplicatedProject = await response.json();
                            toast({
                              title: 'Succès',
                              description: 'Projet dupliqué avec succès',
                            });
                            navigate(`/projects/${duplicatedProject.id}`);
                          } catch (error: any) {
                            toast({
                              title: 'Erreur',
                              description: error.message || 'Erreur lors de la duplication',
                              variant: 'destructive',
                            });
                          }
                        }}>
                          <Copy className="h-4 w-4 mr-2" />
                          Dupliquer le projet
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem 
                          onClick={() => setDeleteDialogOpen(true)}
                          className="text-destructive focus:text-destructive"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Supprimer le projet
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Créateurs</p>
                    <p className="text-2xl font-bold text-primary">{creators.length}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Posts (Jour)</p>
                    <p className="text-2xl font-bold text-primary">{postStats.perDay}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Posts (Semaine)</p>
                    <p className="text-2xl font-bold text-primary">{postStats.perWeek}</p>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Posts (Mois)</p>
                    <p className="text-2xl font-bold text-primary">{postStats.perMonth}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Header Stats + PieChart */}
            <div className="grid gap-4 md:grid-cols-3">
              {/* Right: Content Type Distribution PieChart */}
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

