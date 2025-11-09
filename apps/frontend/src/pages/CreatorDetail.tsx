import { useState, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { ArrowLeft, Heart, MessageCircle, Eye, Grid3x3, BarChart3, TrendingUp, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function CreatorDetail() {
  const engagementTrendData: Array<{ date: string; engagement: number }> = [];
  const topPerformingCreators: Array<{ username: string; avg_engagement: number }> = [];
  const { id, username } = useParams<{ id: string; username: string }>();
  const navigate = useNavigate();
  const [sortColumn, setSortColumn] = useState<string>('posted_at');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [selectedPost, setSelectedPost] = useState<any>(null);
  const [postDialogOpen, setPostDialogOpen] = useState(false);
  const [creator, setCreator] = useState<any>(null);
  const [creatorPosts, setCreatorPosts] = useState<any[]>([]);

  // Function to sort posts
  const sortedPosts = useMemo(() => {
    const sorted = [...creatorPosts];
    sorted.sort((a: any, b: any) => {
      let aVal: any = a[sortColumn];
      let bVal: any = b[sortColumn];

      // Handle null/undefined values
      if (aVal === null || aVal === undefined) aVal = '';
      if (bVal === null || bVal === undefined) bVal = '';

      // Sort by date
      if (sortColumn === 'posted_at' || sortColumn === 'fetched_at') {
        const aDate = aVal ? new Date(aVal).getTime() : 0;
        const bDate = bVal ? new Date(bVal).getTime() : 0;
        return sortDirection === 'asc' ? aDate - bDate : bDate - aDate;
      }

      // Numeric sort
      if (sortColumn === 'like_count' || sortColumn === 'comment_count' || sortColumn === 'view_count' || sortColumn === 'score') {
        const aNum = Number(aVal) || 0;
        const bNum = Number(bVal) || 0;
        return sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
      }

      // Text sort
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        const cmp = aVal.localeCompare(bVal);
        return sortDirection === 'asc' ? cmp : -cmp;
      }

      return 0;
    });
    return sorted;
  }, [creatorPosts, sortColumn, sortDirection]);

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
                      <p className="text-sm text-muted-foreground mt-2 mb-4">{creator.bio}</p>
                    )}

                    {/* Stats regroupées sous la description - 6 chiffres max */}
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
                      <div>
                        <p className="text-2xl font-bold text-primary">{creator.avg_engagement || 0}%</p>
                        <p className="text-xs text-muted-foreground">Avg Engagement</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-primary">
                          {creatorPosts.reduce((sum, p) => sum + (p.like_count || 0), 0).toLocaleString()}
                        </p>
                        <p className="text-xs text-muted-foreground">Total Likes</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-primary">
                          {creatorPosts.reduce((sum, p) => sum + (p.comment_count || 0), 0).toLocaleString()}
                        </p>
                        <p className="text-xs text-muted-foreground">Total Comments</p>
                      </div>
                    </div>

                    {/* Badges */}
                    <div className="flex items-center gap-2 pt-4">
                      <Badge variant="secondary">{creator.platform}</Badge>
                      {creator.category && (
                        <Badge variant="outline">{creator.category}</Badge>
                      )}
                    </div>
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

          {/* Tab 2: Grid - Tableau */}
          <TabsContent value="grid" className="space-y-4">
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
                        sortedPosts.map((post: any) => (
                          <TableRow
                            key={post.id}
                            className="cursor-pointer hover:bg-muted/50"
                          >
                            <TableCell>
                              <img
                                src={post.media_url}
                                alt={post.caption}
                                className="w-12 h-12 rounded object-cover"
                              />
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
                              <Badge variant="outline">{post.platform || creator.platform || 'instagram'}</Badge>
                            </TableCell>
                          </TableRow>
                        ))
                      ) : (
                        <TableRow>
                          <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
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

          {/* Tab 3: Analytics */}
          <TabsContent value="analytics" className="space-y-4">
            {/* Charts - 4 graphiques en 2x2 */}
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

              <Card>
                <CardHeader>
                  <CardTitle>Likes Over Time</CardTitle>
                  <CardDescription>Daily likes trend</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={creatorPosts.slice(0, 7).map(p => ({
                      date: p.posted_at ? new Date(p.posted_at).toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' }) : 'N/A',
                      likes: p.like_count || 0,
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
                      <Area
                        type="monotone"
                        dataKey="likes"
                        stroke="#ef4444"
                        fill="#ef4444"
                        fillOpacity={0.2}
                        name="Likes"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Comments Over Time</CardTitle>
                  <CardDescription>Daily comments trend</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={creatorPosts.slice(0, 7).map(p => ({
                      date: p.posted_at ? new Date(p.posted_at).toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' }) : 'N/A',
                      comments: p.comment_count || 0,
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
                      <Area
                        type="monotone"
                        dataKey="comments"
                        stroke="#3b82f6"
                        fill="#3b82f6"
                        fillOpacity={0.2}
                        name="Comments"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>

        {/* Post Detail Dialog - Style Instagram */}
        <Dialog open={postDialogOpen} onOpenChange={setPostDialogOpen}>
          {selectedPost && (() => {
            const profilePic = creator?.profile_picture || `https://api.dicebear.com/7.x/avataaars/svg?seed=${creator?.handle}`;
            const postedDate = selectedPost.posted_at ? new Date(selectedPost.posted_at) : new Date();
            const relativeTime = formatDistanceToNow(postedDate, { addSuffix: true, locale: fr });
            const caption = selectedPost.caption || '';

            return (
              <DialogContent className="max-w-5xl max-h-[90vh] p-0 gap-0 overflow-hidden">
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
                          alt={creator?.handle}
                          className="w-10 h-10 rounded-full cursor-pointer hover:opacity-80"
                        />
                        <div>
                          <div className="font-semibold text-sm">
                            {creator?.handle}
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
                        <span className="font-semibold mr-2">{creator?.handle}</span>
                        {(() => {
                          // Format caption with hashtags and mentions as normal but styled text
                          const parts: (string | JSX.Element)[] = [];
                          let lastIndex = 0;
                          
                          // Regex to find hashtags and mentions
                          const regex = /(#\w+|@\w+)/g;
                          let match;
                          
                          while ((match = regex.exec(caption)) !== null) {
                            // Add text before the match
                            if (match.index > lastIndex) {
                              parts.push(caption.substring(lastIndex, match.index));
                            }
                            
                            // Add styled hashtag or mention
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
                          
                          // Add remaining text
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
              </DialogContent>
            );
          })()}
        </Dialog>
      </div>
    </div>
  );
}

