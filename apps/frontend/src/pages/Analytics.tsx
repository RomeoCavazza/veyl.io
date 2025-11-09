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
import { fetchMetaInsights } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

export default function Analytics() {
  const { toast } = useToast();
  const [platform, setPlatform] = useState<'instagram' | 'facebook'>('instagram');
  const [resourceId, setResourceId] = useState('');
  const [metrics, setMetrics] = useState('impressions,reach,profile_views');
  const [insightsResponse, setInsightsResponse] = useState<any>(null);
  const [isFetchingInsights, setIsFetchingInsights] = useState(false);

  const pieData: Array<{ name: string; value: number; color: string }> = [];
  const reachData: Array<{ date: string; organic: number; paid: number }> = [];
  const engagementTrendData: Array<{ date: string; engagement: number; reach: number; impressions: number }> = [];
  const topPerformingCreators: Array<{ username: string; posts: number; avg_engagement: number; total_reach: number }> = [];

  const handleFetchInsights = async () => {
    if (!resourceId.trim()) {
      toast({
        title: 'Resource ID required',
        description: 'Provide an Instagram Business ID or Facebook Page ID before fetching insights.',
        variant: 'destructive',
      });
      return;
    }
    setIsFetchingInsights(true);
    try {
      const data = await fetchMetaInsights(resourceId.trim(), platform, metrics.trim());
      setInsightsResponse(data);
      toast({
        title: 'Insights fetched',
        description: 'Live insights retrieved from Meta Graph API.',
      });
    } catch (error) {
      console.error('Fetch insights error:', error);
      toast({
        title: 'Fetch failed',
        description: 'Unable to fetch insights from Meta. Check logs and credentials.',
        variant: 'destructive',
      });
      setInsightsResponse(null);
    } finally {
      setIsFetchingInsights(false);
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
                  placeholder="e.g. 1784140xxxxxx (IG Business ID)"
                  value={resourceId}
                  onChange={(event) => setResourceId(event.target.value)}
                />
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
                <pre className="max-h-64 overflow-auto text-xs bg-background p-3 rounded-md border">
                  {JSON.stringify(insightsResponse, null, 2)}
                </pre>
              ) : (
                <p className="text-muted-foreground">
                  No insights fetched yet. Use the form above and click “Fetch Insights” to trigger a live Meta Graph API call.
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Quick Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Reach</CardTitle>
              <Eye className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">892.4K</div>
              <p className="text-xs text-success flex items-center gap-1 mt-1">
                <TrendingUp className="h-3 w-3" />
                +24.3% vs last week
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Engagement Rate</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">4.2%</div>
              <p className="text-xs text-success flex items-center gap-1 mt-1">
                <TrendingUp className="h-3 w-3" />
                +0.8% vs last week
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Impressions</CardTitle>
              <Eye className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1.2M</div>
              <p className="text-xs text-success flex items-center gap-1 mt-1">
                <TrendingUp className="h-3 w-3" />
                +18.7% vs last week
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Followers Growth</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">+2,847</div>
              <p className="text-xs text-success flex items-center gap-1 mt-1">
                <TrendingUp className="h-3 w-3" />
                +34.2% vs last week
              </p>
            </CardContent>
          </Card>
        </div>

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
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Engagement Trends</CardTitle>
                  <CardDescription>Daily engagement rate over time</CardDescription>
                </CardHeader>
                <CardContent>
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
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Top Performing Creators</CardTitle>
                  <CardDescription>By average engagement rate</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={topPerformingCreators} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="username" type="category" width={100} />
                      <Tooltip />
                      <Bar dataKey="avg_engagement" fill="hsl(var(--accent))" name="Avg Engagement (%)" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="reach" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Reach & Impressions</CardTitle>
                <CardDescription>Organic vs Paid reach over time</CardDescription>
              </CardHeader>
              <CardContent>
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
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Best Performing Posts</CardTitle>
                  <CardDescription>Top 5 by engagement rate</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {[
                      { title: 'Summer collection launch', engagement: 8.2, reach: 245000 },
                      { title: 'Behind the scenes shoot', engagement: 7.9, reach: 198000 },
                      { title: 'Product reveal teaser', engagement: 7.5, reach: 234000 },
                      { title: 'Customer testimonial', engagement: 6.8, reach: 187000 },
                      { title: 'Influencer collaboration', engagement: 6.5, reach: 215000 },
                    ].map((post, index) => (
                      <div key={index} className="flex items-center justify-between p-3 rounded-lg border">
                        <div className="space-y-1">
                          <p className="text-sm font-medium">{post.title}</p>
                          <p className="text-xs text-muted-foreground">{post.reach.toLocaleString()} reach</p>
                        </div>
                        <Badge variant="secondary">{post.engagement}%</Badge>
                      </div>
                    ))}
                  </div>
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
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="p-4 rounded-lg border">
                    <p className="text-sm text-muted-foreground">Story Views</p>
                    <p className="text-2xl font-bold mt-1">24.5K</p>
                    <p className="text-xs text-success mt-1">+18.2% vs last week</p>
                  </div>
                  <div className="p-4 rounded-lg border">
                    <p className="text-sm text-muted-foreground">Saves</p>
                    <p className="text-2xl font-bold mt-1">3.2K</p>
                    <p className="text-xs text-success mt-1">+24.7% vs last week</p>
                  </div>
                  <div className="p-4 rounded-lg border">
                    <p className="text-sm text-muted-foreground">Shares</p>
                    <p className="text-2xl font-bold mt-1">1.8K</p>
                    <p className="text-xs text-success mt-1">+31.4% vs last week</p>
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2 mt-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Audience Demographics</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm">18-24 years</span>
                        <span className="text-sm font-semibold">34%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">25-34 years</span>
                        <span className="text-sm font-semibold">42%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">35-44 years</span>
                        <span className="text-sm font-semibold">18%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">45+ years</span>
                        <span className="text-sm font-semibold">6%</span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Top Locations</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm">United States</span>
                        <span className="text-sm font-semibold">45%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">United Kingdom</span>
                        <span className="text-sm font-semibold">22%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">France</span>
                        <span className="text-sm font-semibold">15%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Germany</span>
                        <span className="text-sm font-semibold">12%</span>
                      </div>
                    </CardContent>
                  </Card>
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
                <div className="grid gap-4">
                  {[
                    { name: 'Insider Trends Official', category: 'Analytics', likes: 45200, followers: 48900, posts: 1247 },
                    { name: 'Fashion Insights Hub', category: 'Fashion', likes: 128500, followers: 132000, posts: 2894 },
                    { name: 'Trend Analytics Pro', category: 'Business', likes: 67800, followers: 72100, posts: 1567 },
                  ].map((page, index) => (
                    <div key={index} className="p-4 rounded-lg border">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <p className="font-semibold">{page.name}</p>
                          <p className="text-sm text-muted-foreground">{page.category}</p>
                        </div>
                        <Badge variant="secondary">Public Data</Badge>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                          <p className="text-lg font-bold">{(page.likes / 1000).toFixed(1)}K</p>
                          <p className="text-xs text-muted-foreground">Likes</p>
                        </div>
                        <div>
                          <p className="text-lg font-bold">{(page.followers / 1000).toFixed(1)}K</p>
                          <p className="text-xs text-muted-foreground">Followers</p>
                        </div>
                        <div>
                          <p className="text-lg font-bold">{page.posts.toLocaleString()}</p>
                          <p className="text-xs text-muted-foreground">Posts</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Public Engagement Analytics</CardTitle>
                <CardDescription>
                  Aggregated and anonymized insights from public Pages
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 rounded-lg border">
                    <span className="text-sm">Average Post Engagement</span>
                    <span className="text-sm font-semibold">4.2%</span>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg border">
                    <span className="text-sm">Total Public Reach</span>
                    <span className="text-sm font-semibold">2.4M</span>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg border">
                    <span className="text-sm">Community Growth Rate</span>
                    <span className="text-sm font-semibold">+18.7%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
}
