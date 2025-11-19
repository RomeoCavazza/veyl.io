import { useState } from 'react';
import Layout from '@/components/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { BarChart3, TrendingUp, Users, Eye } from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { fetchMetaInsights, fetchPagePublicPosts, fetchInstagramBusinessProfile, fetchInstagramProfile, fetchTikTokProfile, fetchTikTokStats } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

export default function Analytics() {
  const { toast } = useToast();
  const [platform, setPlatform] = useState<'instagram' | 'facebook'>('instagram');
  const [resourceId, setResourceId] = useState('');
  const [metrics, setMetrics] = useState('impressions,reach,profile_views');
  const [insightsResponse, setInsightsResponse] = useState<any>(null);
  const [isFetchingInsights, setIsFetchingInsights] = useState(false);
  
  // Pour Page Posts
  const [pageId, setPageId] = useState('');
  const [pagePostsResponse, setPagePostsResponse] = useState<any>(null);
  const [isFetchingPagePosts, setIsFetchingPagePosts] = useState(false);
  // Pour IG Business Profile
  const [igBusinessProfileResponse, setIgBusinessProfileResponse] = useState<any>(null);
  const [isFetchingIgBusinessProfile, setIsFetchingIgBusinessProfile] = useState(false);
  // Pour IG Profile
  const [igProfileUserId, setIgProfileUserId] = useState('');
  const [igProfileResponse, setIgProfileResponse] = useState<any>(null);
  const [isFetchingIgProfile, setIsFetchingIgProfile] = useState(false);
  // Pour TikTok Profile
  const [tiktokProfileUserId, setTiktokProfileUserId] = useState('');
  const [tiktokProfileResponse, setTiktokProfileResponse] = useState<any>(null);
  const [isFetchingTikTokProfile, setIsFetchingTikTokProfile] = useState(false);
  // Pour TikTok Stats
  const [tiktokStatsUserId, setTiktokStatsUserId] = useState('');
  const [tiktokStatsResponse, setTiktokStatsResponse] = useState<any>(null);
  const [isFetchingTikTokStats, setIsFetchingTikTokStats] = useState(false);

  // Note: Ces données sont vides car elles doivent être calculées depuis les vraies données Meta API
  // Pour Meta App Review, on affiche uniquement les données réelles récupérées via les endpoints
  const pieData: Array<{ name: string; value: number; color: string }> = [];
  const reachData: Array<{ date: string; organic: number; paid: number }> = [];
  const engagementTrendData: Array<{ date: string; engagement: number; reach: number; impressions: number }> = [];
  const topPerformingCreators: Array<{ username: string; posts: number; avg_engagement: number; total_reach: number }> = [];

  const handleFetchInsights = async () => {
    // Si resourceId est vide, utiliser "me" pour le compte connecté
    const actualResourceId = resourceId.trim() || 'me';
    
    setIsFetchingInsights(true);
    try {
      const data = await fetchMetaInsights(actualResourceId, metrics.trim());
      setInsightsResponse(data);
      toast({
        title: 'Insights fetched',
        description: 'Live insights retrieved from Meta Graph API.',
      });
    } catch (error: any) {
      console.error('Fetch insights error:', error);
      const errorMessage = error?.detail?.message || error?.message || 'Unable to fetch insights from Meta.';
      toast({
        title: 'Fetch failed',
        description: errorMessage,
        variant: 'destructive',
      });
      setInsightsResponse(null);
    } finally {
      setIsFetchingInsights(false);
    }
  };

  const handleFetchPagePosts = async () => {
    if (!pageId.trim()) {
      toast({
        title: 'Page ID required',
        description: 'Provide a Facebook Page ID before fetching posts.',
        variant: 'destructive',
      });
      return;
    }
    
    setIsFetchingPagePosts(true);
    try {
      const data = await fetchPagePublicPosts(pageId.trim(), 10);
      setPagePostsResponse(data);
      toast({
        title: 'Page posts fetched',
        description: `Retrieved ${data.total || 0} posts from Facebook Page.`,
      });
    } catch (error: any) {
      console.error('Fetch page posts error:', error);
      const errorMessage = error?.detail?.message || error?.message || 'Unable to fetch page posts from Meta.';
      toast({
        title: 'Fetch failed',
        description: errorMessage,
        variant: 'destructive',
      });
      setPagePostsResponse(null);
    } finally {
      setIsFetchingPagePosts(false);
    }
  };

  const handleFetchIgBusinessProfile = async () => {
    setIsFetchingIgBusinessProfile(true);
    try {
      const data = await fetchInstagramBusinessProfile('me');
      setIgBusinessProfileResponse(data);
      toast({
        title: 'IG Business Profile fetched',
        description: 'Profile retrieved from Meta Graph API.',
      });
    } catch (error: any) {
      console.error('Fetch IG Business Profile error:', error);
      const errorMessage = error?.detail?.message || error?.message || 'Unable to fetch IG Business Profile from Meta.';
      toast({
        title: 'Fetch failed',
        description: errorMessage,
        variant: 'destructive',
      });
      setIgBusinessProfileResponse(null);
    } finally {
      setIsFetchingIgBusinessProfile(false);
    }
  };

  const handleFetchIgProfile = async () => {
    if (!igProfileUserId.trim()) {
      toast({
        title: 'User ID required',
        description: 'Provide an Instagram user ID before fetching profile.',
        variant: 'destructive',
      });
      return;
    }
    
    setIsFetchingIgProfile(true);
    try {
      const data = await fetchInstagramProfile(igProfileUserId.trim());
      setIgProfileResponse(data);
      toast({
        title: 'IG Profile fetched',
        description: 'Profile retrieved from Meta Graph API.',
      });
    } catch (error: any) {
      console.error('Fetch IG Profile error:', error);
      const errorMessage = error?.detail?.message || error?.message || 'Unable to fetch IG Profile from Meta.';
      toast({
        title: 'Fetch failed',
        description: errorMessage,
        variant: 'destructive',
      });
      setIgProfileResponse(null);
    } finally {
      setIsFetchingIgProfile(false);
    }
  };

  const handleFetchTikTokProfile = async () => {
    setIsFetchingTikTokProfile(true);
    try {
      const userId = tiktokProfileUserId.trim() || undefined;
      const data = await fetchTikTokProfile(userId);
      setTiktokProfileResponse(data);
      toast({
        title: 'TikTok Profile fetched',
        description: 'Profile retrieved from TikTok API.',
      });
    } catch (error: any) {
      console.error('Fetch TikTok Profile error:', error);
      const errorMessage = error?.detail?.message || error?.message || 'Unable to fetch TikTok Profile.';
      toast({
        title: 'Fetch failed',
        description: errorMessage,
        variant: 'destructive',
      });
      setTiktokProfileResponse(null);
    } finally {
      setIsFetchingTikTokProfile(false);
    }
  };

  const handleFetchTikTokStats = async () => {
    setIsFetchingTikTokStats(true);
    try {
      const userId = tiktokStatsUserId.trim() || undefined;
      const data = await fetchTikTokStats(userId);
      setTiktokStatsResponse(data);
      toast({
        title: 'TikTok Stats fetched',
        description: 'Stats retrieved from TikTok API.',
      });
    } catch (error: any) {
      console.error('Fetch TikTok Stats error:', error);
      const errorMessage = error?.detail?.message || error?.message || 'Unable to fetch TikTok Stats.';
      toast({
        title: 'Fetch failed',
        description: errorMessage,
        variant: 'destructive',
      });
      setTiktokStatsResponse(null);
    } finally {
      setIsFetchingTikTokStats(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold tracking-tight">Analytics</h1>
            <p className="text-muted-foreground mt-2">
              Deep dive into engagement metrics and performance insights.
            </p>
          </div>
          <Badge variant="outline" className="text-sm">
            Last 7 Days
          </Badge>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Live Insights Fetch (Meta Graph API)</CardTitle>
            <CardDescription>
              Provide a connected Instagram Business ID or Facebook Page ID, choose metrics, then fetch live insights.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="resourceId">Resource ID</Label>
                <Input
                  id="resourceId"
                  placeholder="Leave empty for 'me' (your connected account)"
                  value={resourceId}
                  onChange={(event) => setResourceId(event.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  Leave empty to use your connected Instagram Business account, or enter a specific IG Business ID or Page ID
                </p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="platform">Platform</Label>
                <Select value={platform} onValueChange={(value: 'instagram' | 'facebook') => setPlatform(value)}>
                  <SelectTrigger id="platform">
                    <SelectValue placeholder="Select platform" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="instagram">Instagram Business</SelectItem>
                    <SelectItem value="facebook">Facebook Page</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="metrics">Metrics (comma-separated)</Label>
                <Input
                  id="metrics"
                  placeholder="impressions,reach,profile_views"
                  value={metrics}
                  onChange={(event) => setMetrics(event.target.value)}
                />
              </div>
            </div>
            <div className="flex justify-end">
              <Button onClick={handleFetchInsights} disabled={isFetchingInsights}>
                {isFetchingInsights ? 'Fetching…' : 'Fetch Insights'}
              </Button>
            </div>
            <div className="rounded-lg border bg-muted/40 p-4 text-sm">
              <p className="font-medium mb-2">Meta API Response</p>
              {insightsResponse ? (
                <div className="space-y-4">
                  {/* Afficher les métriques de manière lisible */}
                  {insightsResponse.metrics && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {Object.entries(insightsResponse.metrics).map(([key, value]) => (
                        <div key={key} className="p-3 rounded-md bg-background border">
                          <p className="text-xs text-muted-foreground mb-1">{key.replace(/_/g, ' ')}</p>
                          <p className="text-lg font-bold">{typeof value === 'number' ? value.toLocaleString() : String(value)}</p>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {/* Raw JSON pour debug */}
                  <details className="mt-4">
                    <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">
                      View raw JSON response
                    </summary>
                    <pre className="max-h-64 overflow-auto text-xs bg-background p-3 rounded-md border mt-2">
                      {JSON.stringify(insightsResponse, null, 2)}
                    </pre>
                  </details>
                </div>
              ) : (
                <p className="text-muted-foreground">
                  No insights fetched yet. Use the form above and click "Fetch Insights" to trigger a live Meta Graph API call.
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Facebook Page Posts Card */}
        <Card>
          <CardHeader>
            <CardTitle>Facebook Page Posts (pages_read_user_content)</CardTitle>
            <CardDescription>
              Fetch public posts from a Facebook Page using pages_read_user_content permission.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="pageId">Facebook Page ID</Label>
              <Input
                id="pageId"
                placeholder="e.g. 123456789012345 (Facebook Page ID)"
                value={pageId}
                onChange={(event) => setPageId(event.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Enter a Facebook Page ID to fetch public posts from that page
              </p>
            </div>
            <div className="flex justify-end">
              <Button onClick={handleFetchPagePosts} disabled={isFetchingPagePosts}>
                {isFetchingPagePosts ? 'Fetching…' : 'Fetch Page Posts'}
              </Button>
            </div>
            <div className="rounded-lg border bg-muted/40 p-4 text-sm">
              <p className="font-medium mb-2">Page Posts Response</p>
              {pagePostsResponse ? (
                <div className="space-y-4">
                  {/* Afficher les posts de manière lisible */}
                  {pagePostsResponse.data && pagePostsResponse.data.length > 0 ? (
                    <div className="space-y-3">
                      <p className="text-xs text-muted-foreground">
                        Found {pagePostsResponse.total} post(s) from page {pagePostsResponse.page_id}
                      </p>
                      <div className="space-y-2 max-h-64 overflow-y-auto">
                        {pagePostsResponse.data.map((post: any, index: number) => (
                          <div key={post.id || index} className="p-3 rounded-md bg-background border">
                            <div className="flex items-start justify-between gap-2 mb-2">
                              <p className="text-xs text-muted-foreground">
                                {post.created_time ? new Date(post.created_time).toLocaleString() : 'N/A'}
                              </p>
                              <div className="flex gap-3 text-xs text-muted-foreground">
                                {post.like_count !== undefined && (
                                  <span>❤️ {post.like_count}</span>
                                )}
                                {post.comment_count !== undefined && (
                                  <span>💬 {post.comment_count}</span>
                                )}
                              </div>
                            </div>
                            {post.message && (
                              <p className="text-sm line-clamp-3">{post.message}</p>
                            )}
                            {post.permalink_url && (
                              <a
                                href={post.permalink_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-primary hover:underline mt-2 inline-block"
                              >
                                View on Facebook →
                              </a>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <p className="text-muted-foreground">No posts found</p>
                  )}
                  
                  {/* Raw JSON pour debug */}
                  <details className="mt-4">
                    <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">
                      View raw JSON response
                    </summary>
                    <pre className="max-h-64 overflow-auto text-xs bg-background p-3 rounded-md border mt-2">
                      {JSON.stringify(pagePostsResponse, null, 2)}
                    </pre>
                  </details>
                </div>
              ) : (
                <p className="text-muted-foreground">
                  No page posts fetched yet. Enter a Facebook Page ID and click "Fetch Page Posts" to retrieve posts.
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Instagram Business Profile Card */}
        <Card>
          <CardHeader>
            <CardTitle>Instagram Business Profile (instagram_business_basic)</CardTitle>
            <CardDescription>
              Fetch Instagram Business profile using instagram_business_basic permission.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-end">
              <Button onClick={handleFetchIgBusinessProfile} disabled={isFetchingIgBusinessProfile}>
                {isFetchingIgBusinessProfile ? 'Fetching…' : 'Fetch IG Business Profile'}
              </Button>
            </div>
            <div className="rounded-lg border bg-muted/40 p-4 text-sm">
              <p className="font-medium mb-2">IG Business Profile Response</p>
              {igBusinessProfileResponse ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {igBusinessProfileResponse.username && (
                      <div className="p-3 rounded-md bg-background border">
                        <p className="text-xs text-muted-foreground mb-1">Username</p>
                        <p className="text-lg font-bold">@{igBusinessProfileResponse.username}</p>
                      </div>
                    )}
                    {igBusinessProfileResponse.followers_count !== undefined && (
                      <div className="p-3 rounded-md bg-background border">
                        <p className="text-xs text-muted-foreground mb-1">Followers</p>
                        <p className="text-lg font-bold">{igBusinessProfileResponse.followers_count.toLocaleString()}</p>
                      </div>
                    )}
                    {igBusinessProfileResponse.media_count !== undefined && (
                      <div className="p-3 rounded-md bg-background border">
                        <p className="text-xs text-muted-foreground mb-1">Media Count</p>
                        <p className="text-lg font-bold">{igBusinessProfileResponse.media_count.toLocaleString()}</p>
                      </div>
                    )}
                  </div>
                  {igBusinessProfileResponse.biography && (
                    <div className="p-3 rounded-md bg-background border">
                      <p className="text-xs text-muted-foreground mb-1">Bio</p>
                      <p className="text-sm">{igBusinessProfileResponse.biography}</p>
                    </div>
                  )}
                  <details className="mt-4">
                    <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">
                      View raw JSON response
                    </summary>
                    <pre className="max-h-64 overflow-auto text-xs bg-background p-3 rounded-md border mt-2">
                      {JSON.stringify(igBusinessProfileResponse, null, 2)}
                    </pre>
                  </details>
                </div>
              ) : (
                <p className="text-muted-foreground">
                  No profile fetched yet. Click "Fetch IG Business Profile" to retrieve your Instagram Business profile.
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Instagram Profile Card (instagram_basic) */}
        <Card>
          <CardHeader>
            <CardTitle>Instagram Profile (instagram_basic)</CardTitle>
            <CardDescription>
              Fetch Instagram profile using instagram_basic permission.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="igProfileUserId">Instagram User ID</Label>
              <Input
                id="igProfileUserId"
                placeholder="e.g. 17841411416084584 (Instagram user ID)"
                value={igProfileUserId}
                onChange={(event) => setIgProfileUserId(event.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Enter an Instagram user ID to fetch profile information
              </p>
            </div>
            <div className="flex justify-end">
              <Button onClick={handleFetchIgProfile} disabled={isFetchingIgProfile}>
                {isFetchingIgProfile ? 'Fetching…' : 'Fetch IG Profile'}
              </Button>
            </div>
            <div className="rounded-lg border bg-muted/40 p-4 text-sm">
              <p className="font-medium mb-2">IG Profile Response</p>
              {igProfileResponse ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {igProfileResponse.username && (
                      <div className="p-3 rounded-md bg-background border">
                        <p className="text-xs text-muted-foreground mb-1">Username</p>
                        <p className="text-lg font-bold">@{igProfileResponse.username}</p>
                      </div>
                    )}
                    {igProfileResponse.profile_picture_url && (
                      <div className="p-3 rounded-md bg-background border">
                        <p className="text-xs text-muted-foreground mb-1">Profile Picture</p>
                        <img src={igProfileResponse.profile_picture_url} alt="Profile" className="w-16 h-16 rounded-full" />
                      </div>
                    )}
                  </div>
                  {igProfileResponse.biography && (
                    <div className="p-3 rounded-md bg-background border">
                      <p className="text-xs text-muted-foreground mb-1">Bio</p>
                      <p className="text-sm">{igProfileResponse.biography}</p>
                    </div>
                  )}
                  <details className="mt-4">
                    <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">
                      View raw JSON response
                    </summary>
                    <pre className="max-h-64 overflow-auto text-xs bg-background p-3 rounded-md border mt-2">
                      {JSON.stringify(igProfileResponse, null, 2)}
                    </pre>
                  </details>
                </div>
              ) : (
                <p className="text-muted-foreground">
                  No profile fetched yet. Enter a user ID and click "Fetch IG Profile" to retrieve profile information.
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* TikTok Profile Card (user.info.basic, user.info.profile) */}
        <Card>
          <CardHeader>
            <CardTitle>TikTok Profile (user.info.basic, user.info.profile)</CardTitle>
            <CardDescription>
              Fetch TikTok profile using user.info.basic and user.info.profile permissions.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="tiktokProfileUserId">TikTok User ID (optional)</Label>
              <Input
                id="tiktokProfileUserId"
                placeholder="Leave empty for 'me' (your connected account)"
                value={tiktokProfileUserId}
                onChange={(event) => setTiktokProfileUserId(event.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Leave empty to use your connected TikTok account, or enter a specific user ID
              </p>
            </div>
            <div className="flex justify-end">
              <Button onClick={handleFetchTikTokProfile} disabled={isFetchingTikTokProfile}>
                {isFetchingTikTokProfile ? 'Fetching…' : 'Fetch TikTok Profile'}
              </Button>
            </div>
            <div className="rounded-lg border bg-muted/40 p-4 text-sm">
              <p className="font-medium mb-2">TikTok Profile Response</p>
              {tiktokProfileResponse?.data ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {tiktokProfileResponse.data.display_name && (
                      <div className="p-3 rounded-md bg-background border">
                        <p className="text-xs text-muted-foreground mb-1">Display Name</p>
                        <p className="text-lg font-bold">{tiktokProfileResponse.data.display_name}</p>
                      </div>
                    )}
                    {tiktokProfileResponse.data.avatar_url && (
                      <div className="p-3 rounded-md bg-background border">
                        <p className="text-xs text-muted-foreground mb-1">Avatar</p>
                        <img src={tiktokProfileResponse.data.avatar_url} alt="Avatar" className="w-16 h-16 rounded-full" />
                      </div>
                    )}
                    {tiktokProfileResponse.data.is_verified !== undefined && (
                      <div className="p-3 rounded-md bg-background border">
                        <p className="text-xs text-muted-foreground mb-1">Verified</p>
                        <p className="text-lg font-bold">{tiktokProfileResponse.data.is_verified ? 'Yes' : 'No'}</p>
                      </div>
                    )}
                  </div>
                  {tiktokProfileResponse.data.bio_description && (
                    <div className="p-3 rounded-md bg-background border">
                      <p className="text-xs text-muted-foreground mb-1">Bio</p>
                      <p className="text-sm">{tiktokProfileResponse.data.bio_description}</p>
                    </div>
                  )}
                  <details className="mt-4">
                    <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">
                      View raw JSON response
                    </summary>
                    <pre className="max-h-64 overflow-auto text-xs bg-background p-3 rounded-md border mt-2">
                      {JSON.stringify(tiktokProfileResponse, null, 2)}
                    </pre>
                  </details>
                </div>
              ) : (
                <p className="text-muted-foreground">
                  No profile fetched yet. Click "Fetch TikTok Profile" to retrieve your TikTok profile.
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* TikTok Stats Card (user.info.stats) */}
        <Card>
          <CardHeader>
            <CardTitle>TikTok Stats (user.info.stats)</CardTitle>
            <CardDescription>
              Fetch TikTok user statistics using user.info.stats permission.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="tiktokStatsUserId">TikTok User ID (optional)</Label>
              <Input
                id="tiktokStatsUserId"
                placeholder="Leave empty for 'me' (your connected account)"
                value={tiktokStatsUserId}
                onChange={(event) => setTiktokStatsUserId(event.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                Leave empty to use your connected TikTok account, or enter a specific user ID
              </p>
            </div>
            <div className="flex justify-end">
              <Button onClick={handleFetchTikTokStats} disabled={isFetchingTikTokStats}>
                {isFetchingTikTokStats ? 'Fetching…' : 'Fetch TikTok Stats'}
              </Button>
            </div>
            <div className="rounded-lg border bg-muted/40 p-4 text-sm">
              <p className="font-medium mb-2">TikTok Stats Response</p>
              {tiktokStatsResponse?.data ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {tiktokStatsResponse.data.follower_count !== undefined && (
                      <div className="p-3 rounded-md bg-background border">
                        <p className="text-xs text-muted-foreground mb-1">Followers</p>
                        <p className="text-lg font-bold">{tiktokStatsResponse.data.follower_count.toLocaleString()}</p>
                      </div>
                    )}
                    {tiktokStatsResponse.data.following_count !== undefined && (
                      <div className="p-3 rounded-md bg-background border">
                        <p className="text-xs text-muted-foreground mb-1">Following</p>
                        <p className="text-lg font-bold">{tiktokStatsResponse.data.following_count.toLocaleString()}</p>
                      </div>
                    )}
                    {tiktokStatsResponse.data.likes_count !== undefined && (
                      <div className="p-3 rounded-md bg-background border">
                        <p className="text-xs text-muted-foreground mb-1">Total Likes</p>
                        <p className="text-lg font-bold">{tiktokStatsResponse.data.likes_count.toLocaleString()}</p>
                      </div>
                    )}
                    {tiktokStatsResponse.data.video_count !== undefined && (
                      <div className="p-3 rounded-md bg-background border">
                        <p className="text-xs text-muted-foreground mb-1">Videos</p>
                        <p className="text-lg font-bold">{tiktokStatsResponse.data.video_count.toLocaleString()}</p>
                      </div>
                    )}
                  </div>
                  <details className="mt-4">
                    <summary className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">
                      View raw JSON response
                    </summary>
                    <pre className="max-h-64 overflow-auto text-xs bg-background p-3 rounded-md border mt-2">
                      {JSON.stringify(tiktokStatsResponse, null, 2)}
                    </pre>
                  </details>
                </div>
              ) : (
                <p className="text-muted-foreground">
                  No stats fetched yet. Click "Fetch TikTok Stats" to retrieve your TikTok statistics.
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Quick Stats - Afficher les métriques depuis insightsResponse si disponible */}
        {insightsResponse?.metrics && (
          <div className="grid gap-4 md:grid-cols-4">
            {insightsResponse.metrics.reach !== undefined && (
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Reach</CardTitle>
                  <Eye className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{insightsResponse.metrics.reach.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground mt-1">From Meta Insights API</p>
                </CardContent>
              </Card>
            )}

            {insightsResponse.metrics.impressions !== undefined && (
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Impressions</CardTitle>
                  <Eye className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{insightsResponse.metrics.impressions.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground mt-1">From Meta Insights API</p>
                </CardContent>
              </Card>
            )}

            {insightsResponse.metrics.profile_views !== undefined && (
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Profile Views</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{insightsResponse.metrics.profile_views.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground mt-1">From Meta Insights API</p>
                </CardContent>
              </Card>
            )}

            {insightsResponse.metrics.website_clicks !== undefined && (
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Website Clicks</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{insightsResponse.metrics.website_clicks.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground mt-1">From Meta Insights API</p>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Tabs */}
        <Tabs defaultValue="engagement" className="space-y-4">
          <TabsList>
            <TabsTrigger value="engagement">Engagement</TabsTrigger>
            <TabsTrigger value="reach">Reach & Impressions</TabsTrigger>
            <TabsTrigger value="content">Content Performance</TabsTrigger>
            <TabsTrigger value="instagram">Instagram Insights</TabsTrigger>
            <TabsTrigger value="pages">Page Metadata</TabsTrigger>
          </TabsList>

          <TabsContent value="engagement" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Engagement Trends</CardTitle>
                <CardDescription>Daily engagement rate over time</CardDescription>
              </CardHeader>
              <CardContent>
                {engagementTrendData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={engagementTrendData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="date"
                        tickFormatter={(value) =>
                          new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
                        }
                      />
                      <YAxis />
                      <Tooltip />
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
                ) : (
                  <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                    <p className="text-sm">No engagement data available. Fetch insights to see trends.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reach" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Reach & Impressions</CardTitle>
                <CardDescription>Organic vs Paid reach over time</CardDescription>
              </CardHeader>
              <CardContent>
                {reachData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={400}>
                    <AreaChart data={reachData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="date"
                        tickFormatter={(value) =>
                          new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
                        }
                      />
                      <YAxis />
                      <Tooltip />
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
                ) : (
                  <div className="flex items-center justify-center h-[400px] text-muted-foreground">
                    <p className="text-sm">No reach data available. Fetch insights to see trends.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="content" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Content Type Distribution</CardTitle>
                  <CardDescription>Breakdown by media type</CardDescription>
                </CardHeader>
                <CardContent>
                  {pieData.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={pieData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                          outerRadius={100}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {pieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                      <p className="text-sm">No content data available. Fetch insights to see distribution.</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Best Performing Posts</CardTitle>
                  <CardDescription>Top 5 by engagement rate</CardDescription>
                </CardHeader>
                <CardContent>
                  {topPerformingCreators.length > 0 ? (
                    <div className="space-y-4">
                      {topPerformingCreators.map((creator, index) => (
                        <div key={index} className="flex items-center justify-between p-3 rounded-lg border">
                          <div className="space-y-1">
                            <p className="text-sm font-medium">@{creator.username}</p>
                            <p className="text-xs text-muted-foreground">{creator.posts} posts</p>
                          </div>
                          <Badge variant="secondary">{creator.avg_engagement.toFixed(1)}%</Badge>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                      <p className="text-sm">No creator data available. Fetch insights to see top performers.</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Instagram Insights Tab - instagram_business_manage_insights */}
          <TabsContent value="instagram" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Instagram Professional Account Insights</CardTitle>
                <CardDescription>
                  Detailed insights from Instagram Business account (instagram_business_manage_insights permission)
                </CardDescription>
              </CardHeader>
              <CardContent>
                {insightsResponse?.metrics ? (
                  <div className="grid gap-4 md:grid-cols-3">
                    {insightsResponse.metrics.impressions !== undefined && (
                      <div className="p-4 rounded-lg border">
                        <p className="text-sm text-muted-foreground">Impressions</p>
                        <p className="text-2xl font-bold mt-1">{insightsResponse.metrics.impressions.toLocaleString()}</p>
                        <p className="text-xs text-muted-foreground mt-1">From Meta Insights API</p>
                      </div>
                    )}
                    {insightsResponse.metrics.reach !== undefined && (
                      <div className="p-4 rounded-lg border">
                        <p className="text-sm text-muted-foreground">Reach</p>
                        <p className="text-2xl font-bold mt-1">{insightsResponse.metrics.reach.toLocaleString()}</p>
                        <p className="text-xs text-muted-foreground mt-1">From Meta Insights API</p>
                      </div>
                    )}
                    {insightsResponse.metrics.profile_views !== undefined && (
                      <div className="p-4 rounded-lg border">
                        <p className="text-sm text-muted-foreground">Profile Views</p>
                        <p className="text-2xl font-bold mt-1">{insightsResponse.metrics.profile_views.toLocaleString()}</p>
                        <p className="text-xs text-muted-foreground mt-1">From Meta Insights API</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <p className="text-sm">No Instagram insights data available.</p>
                    <p className="text-xs mt-2">Use the "Live Insights Fetch" section above to fetch insights from Meta API.</p>
                  </div>
                )}

                <div className="mt-4 text-center py-4 text-muted-foreground">
                  <p className="text-sm">Demographics and location data require additional Meta API calls.</p>
                  <p className="text-xs mt-2">These metrics are available via the Meta Insights API with appropriate permissions.</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Page Metadata Tab - Page Public Metadata Access */}
          <TabsContent value="pages" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Page Public Metadata</CardTitle>
                <CardDescription>
                  Aggregate public information from Facebook Pages (Page Public Metadata Access feature)
                </CardDescription>
              </CardHeader>
              <CardContent>
                {pagePostsResponse?.data && pagePostsResponse.data.length > 0 ? (
                  <div className="space-y-4">
                    <div className="p-4 rounded-lg border">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <p className="font-semibold">Page ID: {pagePostsResponse.page_id}</p>
                          <p className="text-sm text-muted-foreground">Facebook Page</p>
                        </div>
                        <Badge variant="secondary">Public Data</Badge>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                          <p className="text-lg font-bold">{pagePostsResponse.total}</p>
                          <p className="text-xs text-muted-foreground">Posts Retrieved</p>
                        </div>
                        <div>
                          <p className="text-lg font-bold">
                            {pagePostsResponse.data.reduce((sum: number, p: any) => sum + (p.like_count || 0), 0).toLocaleString()}
                          </p>
                          <p className="text-xs text-muted-foreground">Total Likes</p>
                        </div>
                        <div>
                          <p className="text-lg font-bold">
                            {pagePostsResponse.data.reduce((sum: number, p: any) => sum + (p.comment_count || 0), 0).toLocaleString()}
                          </p>
                          <p className="text-xs text-muted-foreground">Total Comments</p>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <p className="text-sm">No page data available.</p>
                    <p className="text-xs mt-2">Use the "Facebook Page Posts" section above to fetch posts from a Facebook Page.</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Public Engagement Analytics</CardTitle>
                <CardDescription>
                  Aggregated insights from fetched Facebook Page posts
                </CardDescription>
              </CardHeader>
              <CardContent>
                {pagePostsResponse?.data && pagePostsResponse.data.length > 0 ? (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 rounded-lg border">
                      <span className="text-sm">Total Posts Retrieved</span>
                      <span className="text-sm font-semibold">{pagePostsResponse.total}</span>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg border">
                      <span className="text-sm">Average Likes per Post</span>
                      <span className="text-sm font-semibold">
                        {Math.round(pagePostsResponse.data.reduce((sum: number, p: any) => sum + (p.like_count || 0), 0) / pagePostsResponse.data.length).toLocaleString()}
                      </span>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg border">
                      <span className="text-sm">Average Comments per Post</span>
                      <span className="text-sm font-semibold">
                        {Math.round(pagePostsResponse.data.reduce((sum: number, p: any) => sum + (p.comment_count || 0), 0) / pagePostsResponse.data.length).toLocaleString()}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <p className="text-sm">No engagement data available.</p>
                    <p className="text-xs mt-2">Fetch page posts to see engagement analytics.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
}
