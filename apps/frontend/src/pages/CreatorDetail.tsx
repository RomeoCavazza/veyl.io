import { useParams, useNavigate } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArrowLeft, Heart, MessageCircle, Eye, Grid3x3, Table, BarChart3, TrendingUp } from 'lucide-react';
import { fakeCreators, fakePosts } from '@/lib/fakeData';
import { engagementTrendData, topPerformingCreators } from '@/lib/mockData';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';

export default function CreatorDetail() {
  const { id, username } = useParams<{ id: string; username: string }>();
  const navigate = useNavigate();

  // Simuler chargement créateur
  const creator = fakeCreators.find(c => c.handle.replace('@', '') === username);

  // Simuler posts du créateur
  const creatorPosts = fakePosts.filter(p => p.username === creator?.handle.replace('@', '') || p.username === username);

  if (!creator) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="container py-8">
          <div className="text-center">Creator not found</div>
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
            onClick={() => navigate(`/projects/${id}`)}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Project
          </Button>

          {/* Creator Info - Panneau unique */}
          <Card>
            <CardContent className="p-6">
              <div className="flex gap-6">
                {/* Photo de profil à gauche */}
                <div className="flex-shrink-0">
                  <img
                    src={creator.profile_picture || `https://api.dicebear.com/7.x/avataaars/svg?seed=${creator.handle}`}
                    alt={creator.handle}
                    className="w-32 h-32 rounded-full border-2 border-border"
                  />
                </div>

                {/* Informations à droite */}
                <div className="flex-1 space-y-4">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <CardTitle className="text-2xl">{creator.handle}</CardTitle>
                      {creator.verified && (
                        <Badge variant="default">Verified</Badge>
                      )}
                    </div>
                    {creator.full_name && (
                      <CardDescription className="text-base mb-2">{creator.full_name}</CardDescription>
                    )}
                    {creator.bio && (
                      <p className="text-sm text-muted-foreground mt-2">{creator.bio}</p>
                    )}
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-4 pt-4 border-t border-border">
                    <div>
                      <p className="text-2xl font-bold text-primary">{creator.followers.toLocaleString()}</p>
                      <p className="text-xs text-muted-foreground">Followers</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-primary">{creator.following?.toLocaleString() || 'N/A'}</p>
                      <p className="text-xs text-muted-foreground">Following</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-primary">{creatorPosts.length}</p>
                      <p className="text-xs text-muted-foreground">Posts</p>
                    </div>
                  </div>

                  {/* Badges */}
                  <div className="flex items-center gap-2 pt-2">
                    <Badge variant="secondary">{creator.platform}</Badge>
                    <Badge variant="outline">{creator.avg_engagement}% engagement</Badge>
                    {creator.category && (
                      <Badge variant="outline">{creator.category}</Badge>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs: Feed / Grid / Analytics */}
        <Tabs defaultValue="feed" className="space-y-4">
          <TabsList>
            <TabsTrigger value="feed">Feed</TabsTrigger>
            <TabsTrigger value="grid">Grid</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          {/* Tab 1: Feed */}
          <TabsContent value="feed" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {creatorPosts.length > 0 ? (
                creatorPosts.map((post) => (
                  <Card 
                    key={post.id} 
                    className="overflow-hidden cursor-pointer hover:border-primary transition-colors"
                  >
                    <div className="relative">
                      <img
                        src={post.media_url}
                        alt={post.caption}
                        className="w-full h-64 object-cover"
                      />
                      <div className="absolute top-2 right-2 flex gap-2">
                        <Badge variant="secondary" className="bg-black/50 text-white">
                          {post.platform || creator.platform}
                        </Badge>
                      </div>
                    </div>
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <img
                          src={creator.profile_picture || `https://api.dicebear.com/7.x/avataaars/svg?seed=${creator.handle}`}
                          alt={creator.handle}
                          className="w-6 h-6 rounded-full flex-shrink-0"
                        />
                        <span className="text-sm font-medium">{creator.handle}</span>
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
                ))
              ) : (
                <div className="col-span-full text-center py-12 text-muted-foreground">
                  No posts found
                </div>
              )}
            </div>
          </TabsContent>

          {/* Tab 2: Grid */}
          <TabsContent value="grid" className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {creatorPosts.map((post) => (
                <Card key={post.id} className="overflow-hidden cursor-pointer hover:border-primary transition-colors">
                  <div className="relative">
                    <img
                      src={post.media_url}
                      alt={post.caption}
                      className="w-full aspect-square object-cover"
                    />
                    <div className="absolute inset-0 bg-black/40 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center gap-4 text-white">
                      <div className="flex items-center gap-2">
                        <Heart className="h-5 w-5" />
                        <span className="font-semibold">{post.like_count.toLocaleString()}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <MessageCircle className="h-5 w-5" />
                        <span className="font-semibold">{post.comment_count.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                  <CardContent className="p-3">
                    <p className="text-xs text-muted-foreground line-clamp-2">{post.caption}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Tab 3: Analytics */}
          <TabsContent value="analytics" className="space-y-4">
            {/* Quick Stats */}
            <div className="grid gap-4 md:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Posts</CardTitle>
                  <Grid3x3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{creatorPosts.length}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Avg Engagement</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{creator.avg_engagement || 0}%</div>
                  <p className="text-xs text-success flex items-center gap-1 mt-1">
                    <TrendingUp className="h-3 w-3" />
                    vs average
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Likes</CardTitle>
                  <Heart className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {creatorPosts.reduce((sum, p) => sum + (p.like_count || 0), 0).toLocaleString()}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Comments</CardTitle>
                  <MessageCircle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {creatorPosts.reduce((sum, p) => sum + (p.comment_count || 0), 0).toLocaleString()}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Charts */}
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Engagement Trends</CardTitle>
                  <CardDescription>Daily engagement rate over time</CardDescription>
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

              <Card>
                <CardHeader>
                  <CardTitle>Post Performance</CardTitle>
                  <CardDescription>Top posts by engagement</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={creatorPosts.slice(0, 5).map(p => ({
                      date: p.posted_at ? new Date(p.posted_at).toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' }) : 'N/A',
                      engagement: ((p.like_count || 0) + (p.comment_count || 0)) / (creator.followers || 1) * 100,
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-gray-700" />
                      <XAxis dataKey="date" className="text-gray-400" />
                      <YAxis className="text-gray-400" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '6px',
                        }}
                      />
                      <Bar dataKey="engagement" fill="hsl(var(--accent))" name="Engagement (%)" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

