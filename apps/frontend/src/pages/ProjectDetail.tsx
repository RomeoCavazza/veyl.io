import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Hash, User, Plus, X, Heart, MessageCircle, Eye, ArrowLeft, Settings, Bell, AtSign, Trash2 } from 'lucide-react';
import { getFakeProject, getFakeProjectPosts, fakeCreators, fakePosts } from '@/lib/fakeData';
import { useToast } from '@/hooks/use-toast';

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
        <div className="mb-6 flex items-center justify-between">
          <div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/projects')}
              className="mb-2"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Projects
            </Button>
            <h1 className="text-4xl font-bold tracking-tight">{project.name}</h1>
            {project.description && (
              <p className="text-muted-foreground mt-2">{project.description}</p>
            )}
          </div>
          <div className="flex gap-2">
            <Badge variant={project.status === 'active' ? 'default' : 'secondary'}>
              {project.status}
            </Badge>
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">{creators.length}</div>
              <div className="text-sm text-muted-foreground">Creators</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">{posts.length}</div>
              <div className="text-sm text-muted-foreground">Posts</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">{niches.length}</div>
              <div className="text-sm text-muted-foreground">Niches</div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-2xl font-bold">{project.signals_count || 0}</div>
              <div className="text-sm text-muted-foreground">Signals</div>
            </CardContent>
          </Card>
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
            {/* Watchlist Tabs */}
            <Tabs defaultValue="feed" className="space-y-4">
              <TabsList>
                <TabsTrigger value="feed">
                  <Eye className="h-4 w-4 mr-2" />
                  Feed Posts
                </TabsTrigger>
                <TabsTrigger value="hashtags">
                  <Hash className="h-4 w-4 mr-2" />
                  Hashtags
                </TabsTrigger>
                <TabsTrigger value="comments">
                  <MessageCircle className="h-4 w-4 mr-2" />
                  Comments
                </TabsTrigger>
                <TabsTrigger value="mentions">
                  <AtSign className="h-4 w-4 mr-2" />
                  Mentions
                </TabsTrigger>
              </TabsList>

              <TabsContent value="feed" className="space-y-6">
            {/* Section: Feed Posts */}
            <div>
              <h2 className="text-xl font-semibold mb-4">Posts Feed</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {posts.length > 0 ? (
                  posts.map((post) => {
                    const creator = creators.find(c => c.handle === post.username);
                    return (
                      <Card key={post.id} className="overflow-hidden">
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
                            <span className="text-sm font-medium">{post.username}</span>
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

              </TabsContent>

              {/* Hashtags Tab */}
              <TabsContent value="hashtags" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Tracked Hashtags</CardTitle>
                    <CardDescription>
                      Receive alerts when these hashtags show significant activity
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {niches.length > 0 ? niches.map((hashtag) => (
                        <div
                          key={hashtag.id}
                          className="flex items-center justify-between p-4 rounded-lg border hover:border-primary transition-colors"
                        >
                          <div className="flex items-center gap-4">
                            <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                              <Hash className="h-6 w-6 text-primary" />
                            </div>
                            <div>
                              <p className="font-semibold">#{hashtag.name}</p>
                              <p className="text-sm text-muted-foreground">
                                {(hashtag.posts || 0).toLocaleString()} posts tracked
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-4">
                            <div className="text-right">
                              <div className="flex items-center gap-2">
                                <Bell className="h-4 w-4 text-success" />
                                <span className="text-sm font-medium">{hashtag.posts ? '12' : '0'} new alerts</span>
                              </div>
                              <p className="text-xs text-success">{hashtag.growth || '+24%'} growth</p>
                            </div>
                            <Button variant="ghost" size="icon">
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          </div>
                        </div>
                      )) : (
                        <div className="text-center py-12 text-muted-foreground">
                          <Hash className="h-12 w-12 mx-auto mb-4 opacity-50" />
                          <p>No hashtags tracked yet</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Comments Tab */}
              <TabsContent value="comments" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>User Comments on Your Pages</CardTitle>
                    <CardDescription>
                      Monitor and manage user-generated content (pages_read_user_content permission)
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {[
                        {
                          id: '1',
                          user: '@fashionlover23',
                          avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=user1',
                          comment: 'Love this collection! When will it be available? 😍',
                          post: 'Summer Collection 2025',
                          timestamp: '2h ago',
                          likes: 24,
                        },
                        {
                          id: '2',
                          user: '@styleicon',
                          avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=user2',
                          comment: 'Amazing quality! Just received my order 🎉',
                          post: 'Product Launch Post',
                          timestamp: '5h ago',
                          likes: 18,
                        },
                        {
                          id: '3',
                          user: '@trendhunter',
                          avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=user3',
                          comment: 'Can you share the styling tips? 💫',
                          post: 'Behind The Scenes',
                          timestamp: '1d ago',
                          likes: 31,
                        },
                      ].map((comment) => (
                        <div
                          key={comment.id}
                          className="flex gap-4 p-4 rounded-lg border hover:border-primary transition-colors"
                        >
                          <img
                            src={comment.avatar}
                            alt={comment.user}
                            className="w-12 h-12 rounded-full"
                          />
                          <div className="flex-1 space-y-2">
                            <div className="flex items-center gap-2">
                              <p className="font-semibold">{comment.user}</p>
                              <span className="text-xs text-muted-foreground">{comment.timestamp}</span>
                            </div>
                            <p className="text-sm">{comment.comment}</p>
                            <div className="flex items-center gap-4 text-xs text-muted-foreground">
                              <span>On: {comment.post}</span>
                              <div className="flex items-center gap-1">
                                <Heart className="h-3 w-3" />
                                <span>{comment.likes} likes</span>
                              </div>
                            </div>
                            <div className="flex gap-2">
                              <Button variant="ghost" size="sm">Reply</Button>
                              <Button variant="ghost" size="sm" className="text-destructive">Delete</Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Mentions Tab */}
              <TabsContent value="mentions" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Page Mentions & Tags</CardTitle>
                    <CardDescription>
                      Posts where your page is mentioned or tagged (pages_read_user_content permission)
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {[
                        {
                          id: '1',
                          user: '@influencer_marie',
                          avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=marie',
                          content: 'Tagged your page in my latest post about sustainable fashion!',
                          post_url: 'https://instagram.com/p/xyz123',
                          timestamp: '3h ago',
                          engagement: 2847,
                        },
                        {
                          id: '2',
                          user: '@fashionblogger',
                          avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=blogger',
                          content: 'Mentioned your brand in my Instagram Story',
                          post_url: 'https://instagram.com/p/abc456',
                          timestamp: '6h ago',
                          engagement: 1523,
                        },
                      ].map((mention) => (
                        <div
                          key={mention.id}
                          className="flex gap-4 p-4 rounded-lg border hover:border-primary transition-colors"
                        >
                          <img
                            src={mention.avatar}
                            alt={mention.user}
                            className="w-12 h-12 rounded-full"
                          />
                          <div className="flex-1 space-y-2">
                            <div className="flex items-center gap-2">
                              <p className="font-semibold">{mention.user}</p>
                              <Badge variant="secondary">Mentioned</Badge>
                              <span className="text-xs text-muted-foreground">{mention.timestamp}</span>
                            </div>
                            <p className="text-sm">{mention.content}</p>
                            <div className="flex items-center gap-4 text-xs text-muted-foreground">
                              <div className="flex items-center gap-1">
                                <Eye className="h-3 w-3" />
                                <span>{mention.engagement.toLocaleString()} engagement</span>
                              </div>
                            </div>
                            <Button variant="outline" size="sm" asChild>
                              <a href={mention.post_url} target="_blank" rel="noopener noreferrer">
                                View Post
                              </a>
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </TabsContent>

          {/* Tab 2: Analytics */}
          <TabsContent value="analytics" className="space-y-6">
            {/* Quick Stats */}
            <div className="grid gap-4 md:grid-cols-4">
              <Card className="bg-card border-border shadow-lg">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-white">Total Posts</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary">{project?.posts_count || 0}</div>
                  <p className="text-xs text-gray-400 mt-1">Posts tracked</p>
                </CardContent>
              </Card>

              <Card className="bg-card border-border shadow-lg">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-white">Total Signals</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary">{project?.signals_count || 0}</div>
                  <p className="text-xs text-gray-400 mt-1">Trends detected</p>
                </CardContent>
              </Card>

              <Card className="bg-card border-border shadow-lg">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-white">Creators</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary">{project?.creators_count || 0}</div>
                  <p className="text-xs text-gray-400 mt-1">Monitored</p>
                </CardContent>
              </Card>

              <Card className="bg-card border-border shadow-lg">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-white">Last Signal</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary">
                    {project?.last_signal_at ? new Date(project.last_signal_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' }) : 'N/A'}
                  </div>
                  <p className="text-xs text-gray-400 mt-1">Latest detection</p>
                </CardContent>
              </Card>
            </div>

            {/* Analytics Content */}
            <div className="grid gap-4 md:grid-cols-2">
              <Card className="bg-card border-border shadow-lg">
                <CardHeader>
                  <CardTitle className="text-white">Engagement Overview</CardTitle>
                  <CardDescription className="text-gray-400">
                    Project performance metrics
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="p-4 rounded-lg border border-gray-700 bg-gray-800/50">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm text-gray-300">Average Engagement</span>
                        <span className="text-lg font-bold text-primary">4.2%</span>
                      </div>
                      <p className="text-xs text-success">+0.8% vs last week</p>
                    </div>
                    <div className="p-4 rounded-lg border border-gray-700 bg-gray-800/50">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm text-gray-300">Total Reach</span>
                        <span className="text-lg font-bold text-primary">{((project?.posts_count || 0) * 1250).toLocaleString()}</span>
                      </div>
                      <p className="text-xs text-success">+24.3% vs last week</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-card border-border shadow-lg">
                <CardHeader>
                  <CardTitle className="text-white">Project Stats</CardTitle>
                  <CardDescription className="text-gray-400">
                    Project configuration and status
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center p-3 rounded-lg border border-gray-700 bg-gray-800/30">
                      <span className="text-sm text-gray-300">Status:</span>
                      <Badge variant={project?.status === 'active' ? 'default' : 'secondary'}>
                        {project?.status || 'draft'}
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center p-3 rounded-lg border border-gray-700 bg-gray-800/30">
                      <span className="text-sm text-gray-300">Platforms:</span>
                      <div className="flex gap-2">
                        {(project?.platforms || []).map((p: string) => (
                          <Badge key={p} variant="outline">{p}</Badge>
                        ))}
                        {(!project?.platforms || project.platforms.length === 0) && <span className="text-gray-400">N/A</span>}
                      </div>
                    </div>
                    {project?.last_run_at && (
                      <div className="flex justify-between items-center p-3 rounded-lg border border-gray-700 bg-gray-800/30">
                        <span className="text-sm text-gray-300">Last Run:</span>
                        <span className="text-sm text-gray-400">{new Date(project.last_run_at).toLocaleDateString('fr-FR')}</span>
                      </div>
                    )}
                    {project?.created_at && (
                      <div className="flex justify-between items-center p-3 rounded-lg border border-gray-700 bg-gray-800/30">
                        <span className="text-sm text-gray-300">Created:</span>
                        <span className="text-sm text-gray-400">{new Date(project.created_at).toLocaleDateString('fr-FR')}</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Coming Soon Note */}
            <Card className="bg-card border-border shadow-lg">
              <CardHeader>
                <CardTitle className="text-white">Advanced Analytics</CardTitle>
                <CardDescription className="text-gray-400">
                  Detailed analytics including engagement trends, reach analysis, and content performance
                  will be available once data ingestion is active.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="p-4 rounded-lg border border-gray-700 bg-gray-800/50">
                  <p className="text-sm text-gray-300 mb-2">📊 Analytics Features Coming Soon:</p>
                  <ul className="text-sm text-gray-400 space-y-1 list-disc list-inside">
                    <li>Engagement trends over time</li>
                    <li>Reach & Impressions analysis</li>
                    <li>Content type distribution</li>
                    <li>Top performing creators</li>
                    <li>Hashtag performance metrics</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

