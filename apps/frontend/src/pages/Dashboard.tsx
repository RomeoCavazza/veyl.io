import { Navbar } from '@/components/Navbar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, ArrowUp, Hash, Users, BarChart3 } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function Dashboard() {
  const dashboardMetrics: Array<{ label: string; value: number; change: number; trend: 'up' | 'down' }> = [];
  const engagementTrendData: Array<{ date: string; engagement: number }> = [];
  const topPerformingCreators: Array<{ username: string; avg_engagement: number }> = [];
  const trendingHashtags: Array<{ name: string; post_count: number; recent_growth: number; avg_engagement: number }> = [];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container py-8">
        <div className="space-y-8">
          {/* Header */}
          <div>
            <h1 className="text-4xl font-bold tracking-tight">Overview</h1>
            <p className="text-muted-foreground mt-2">
              Quick overview of your Instagram account performance and key metrics
            </p>
          </div>

        {/* KPI Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {dashboardMetrics.map((metric, index) => (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {metric.label}
                </CardTitle>
                {metric.trend === 'up' ? (
                  <TrendingUp className="h-4 w-4 text-success" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-destructive" />
                )}
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metric.value.toLocaleString()}
                </div>
                <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                  <ArrowUp className="h-3 w-3 text-success" />
                  <span className="text-success">+{metric.change}%</span>
                  <span>vs last month</span>
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid gap-4 md:grid-cols-2">
          {/* Engagement Trend Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Engagement Trends</CardTitle>
              <CardDescription>
                Last 7 days performance metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={engagementTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="engagement" 
                    stroke="hsl(var(--primary))" 
                    strokeWidth={2}
                    name="Engagement Rate (%)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Top Performing Creators */}
          <Card>
            <CardHeader>
              <CardTitle>Top Performing Creators</CardTitle>
              <CardDescription>
                By average engagement rate
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={topPerformingCreators}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="username" />
                  <YAxis />
                  <Tooltip />
                  <Bar 
                    dataKey="avg_engagement" 
                    fill="hsl(var(--accent))"
                    name="Avg Engagement (%)"
                  />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Trending Hashtags */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Hash className="h-5 w-5 text-primary" />
              Trending Hashtags
            </CardTitle>
            <CardDescription>
              Most popular hashtags with growth indicators
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {trendingHashtags.slice(0, 6).map((hashtag) => (
                <div
                  key={hashtag.name}
                  className="flex items-center justify-between p-4 rounded-lg border hover:border-primary transition-colors"
                >
                  <div className="space-y-1">
                    <div className="font-semibold">#{hashtag.name}</div>
                    <div className="text-sm text-muted-foreground">
                      {(hashtag.post_count / 1000).toFixed(1)}K posts
                    </div>
                  </div>
                  <div className="text-right space-y-1">
                    <div className="flex items-center gap-1 text-success text-sm font-medium">
                      <TrendingUp className="h-3 w-3" />
                      +{hashtag.recent_growth}%
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {hashtag.avg_engagement}% engagement
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card className="hover:border-primary transition-colors cursor-pointer">
            <CardHeader>
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-2">
                <Hash className="h-6 w-6 text-primary" />
              </div>
              <CardTitle className="text-lg">Search Hashtags</CardTitle>
              <CardDescription>
                Discover trending content and analyze hashtag performance
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="hover:border-primary transition-colors cursor-pointer">
            <CardHeader>
              <div className="h-12 w-12 rounded-lg bg-accent/10 flex items-center justify-center mb-2">
                <BarChart3 className="h-6 w-6 text-accent" />
              </div>
              <CardTitle className="text-lg">View Analytics</CardTitle>
              <CardDescription>
                Deep dive into engagement metrics and performance insights
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="hover:border-primary transition-colors cursor-pointer">
            <CardHeader>
              <div className="h-12 w-12 rounded-lg bg-success/10 flex items-center justify-center mb-2">
                <Users className="h-6 w-6 text-success" />
              </div>
              <CardTitle className="text-lg">Manage Pages</CardTitle>
              <CardDescription>
                Connect and manage your Instagram Business accounts
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
        </div>
      </div>
    </div>
  );
}
