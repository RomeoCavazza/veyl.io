import { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { useWatchlist, WatchItem } from '@/contexts/WatchlistContext';
import { Eye, Trash2, FileText, Hash, User, Tag, Search, TrendingUp, Edit, Instagram, Facebook } from 'lucide-react';
import { toast } from 'sonner';
import { EmptyState } from '@/components/EmptyState';
import { format, subDays } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { Link } from 'react-router-dom';
import { TikTokIcon } from '@/components/icons/TikTokIcon';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from 'recharts';

interface ScrapedAccount {
  id: string;
  username: string;
  platform: 'instagram' | 'tiktok' | 'facebook';
  status: 'active' | 'pending' | 'error';
  lastScraped: string;
  postsCount: number;
  followers?: number;
}

export default function Watch() {
  const { items, removeItem } = useWatchlist();
  const [activeTab, setActiveTab] = useState('daily');
  const [showDemo, setShowDemo] = useState(false);

  // Performance data for charts
  const generatePerformanceData = (days: number) => {
    const data = [];
    for (let i = days - 1; i >= 0; i--) {
      const date = subDays(new Date(), i);
      data.push({
        date: format(date, 'MMM dd', { locale: enUS }),
        comptes: Math.floor(Math.random() * 500 + 200),
        hashtags: Math.floor(Math.random() * 800 + 400),
        posts: Math.floor(Math.random() * 1200 + 800),
      });
    }
    return data;
  };

  const performanceData = useMemo(() => {
    const daysMap: Record<string, number> = {
      daily: 7,
      weekly: 30,
      monthly: 90,
      yearly: 365,
    };
    return generatePerformanceData(daysMap[activeTab] || 7);
  }, [activeTab]);
  
  // Demo data for scraped accounts
  const [scrapedAccounts] = useState<ScrapedAccount[]>([
    {
      id: '1',
      username: 'makeupro',
      platform: 'instagram',
      status: 'active',
      lastScraped: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      postsCount: 1247,
      followers: 45000
    },
    {
      id: '2',
      username: 'fashionista',
      platform: 'tiktok',
      status: 'active',
      lastScraped: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
      postsCount: 892,
      followers: 125000
    },
    {
      id: '3',
      username: 'trendsetter366',
      platform: 'facebook',
      status: 'pending',
      lastScraped: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      postsCount: 345,
      followers: 23000
    },
  ]);

  // Demo items pour montrer le rendu
  const demoItems = [
    { kind: 'hashtag' as const, value: 'fashion', created_at: new Date().toISOString() },
    { kind: 'user' as const, value: 'makeupro', created_at: new Date().toISOString() },
  ];

  const displayItems = showDemo ? [...items, ...demoItems] : items;

  const getIcon = (kind: string) => {
    switch (kind) {
      case 'hashtag':
        return Hash;
      case 'user':
        return User;
      default:
        return Tag;
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'instagram':
        return <Instagram className="h-4 w-4" style={{ color: '#ac2bac' }} />;
      case 'facebook':
        return <Facebook className="h-4 w-4" style={{ color: '#3b5998' }} />;
      case 'tiktok':
        return <TikTokIcon className="h-4 w-4" />;
      default:
        return <User className="h-4 w-4" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge variant="default" className="bg-green-500">Active</Badge>;
      case 'pending':
        return <Badge variant="secondary">Pending</Badge>;
      case 'error':
        return <Badge variant="destructive">Error</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <main className="flex-1 container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">My Watchlist</h1>
          <p className="text-muted-foreground">
            Track your favorite hashtags, creators, and niches.
          </p>
        </div>

        {items.length === 0 && !showDemo ? (
          <div className="space-y-6">
            <Card className="p-8 text-center border-dashed">
              <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No items being watched</h3>
              <p className="text-muted-foreground mb-4">
                Add a #hashtag, @account, or niche from the search.
              </p>
              <div className="flex gap-2 justify-center">
                <Button asChild className="gap-2">
                  <Link to="/search">
                    <Search className="h-4 w-4" />
                    Go to search
                  </Link>
                </Button>
                <Button variant="outline" onClick={() => setShowDemo(!showDemo)}>
                  {showDemo ? 'Hide demo' : 'View demo'}
                </Button>
              </div>
            </Card>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Demo toggle */}
            {items.length > 0 && (
              <div className="flex justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowDemo(!showDemo)}
                >
                  {showDemo ? 'Hide demo' : 'Show with demo'}
                </Button>
              </div>
            )}

            {/* Scraped Accounts - Table */}
            <section>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <div>
                    <CardTitle className="text-xl font-semibold flex items-center gap-2">
                      <User className="h-5 w-5" />
                      Scraped Accounts
                    </CardTitle>
                    <p className="text-sm text-muted-foreground mt-1">
                      {scrapedAccounts.length} account{scrapedAccounts.length > 1 ? 's' : ''} being watched
                    </p>
                  </div>
                  <Button onClick={() => toast.info('Account addition in development')}>
                    Add account
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-[200px]">Account</TableHead>
                          <TableHead>Platform</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead className="hidden md:table-cell">Last updated</TableHead>
                          <TableHead className="text-right">Posts</TableHead>
                          <TableHead className="text-right">Followers</TableHead>
                          <TableHead className="text-right w-[100px]">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {scrapedAccounts.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                              No scraped accounts yet
                            </TableCell>
                          </TableRow>
                        ) : (
                          scrapedAccounts.map((account) => (
                            <TableRow key={account.id}>
                              <TableCell>
                                <div className="flex items-center gap-3">
                                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                                    {getPlatformIcon(account.platform)}
                                  </div>
                                  <div>
                                    <p className="font-medium">@{account.username}</p>
                                  </div>
                                </div>
                              </TableCell>
                              <TableCell>
                                <Badge variant="outline" className="capitalize">
                                  {account.platform}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                {getStatusBadge(account.status)}
                              </TableCell>
                              <TableCell className="hidden md:table-cell">
                                <span className="text-sm text-muted-foreground">
                                  {format(new Date(account.lastScraped), 'MMM dd, yyyy HH:mm', { locale: enUS })}
                                </span>
                              </TableCell>
                              <TableCell className="text-right">
                                <span className="font-medium">{account.postsCount.toLocaleString()}</span>
                              </TableCell>
                              <TableCell className="text-right">
                                {account.followers ? (
                                  <span className="font-medium">{account.followers.toLocaleString()}</span>
                                ) : (
                                  <span className="text-muted-foreground">—</span>
                                )}
                              </TableCell>
                              <TableCell className="text-right">
                                <div className="flex justify-end gap-1">
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-8 w-8"
                                    onClick={() => toast.info('Editing in development')}
                                  >
                                    <Edit className="h-4 w-4" />
                                  </Button>
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-8 w-8 text-destructive hover:text-destructive"
                                    onClick={() => {
                                      if (confirm(`Do you want to remove @${account.username}?`)) {
                                        toast.success(`@${account.username} removed`);
                                      }
                                    }}
                                  >
                                    <Trash2 className="h-4 w-4" />
                                  </Button>
                                </div>
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>
            </section>

            {/* Watchlist */}
            <section>
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Watched Items ({displayItems.length})
              </h2>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {displayItems.map((item, i) => {
                  const Icon = getIcon(item.kind);
                  const isDemo = i >= items.length;
                  return (
                    <Card key={i} className="p-4 relative">
                      {isDemo && (
                        <Badge className="absolute top-2 right-2 text-xs" variant="secondary">
                          Demo
                        </Badge>
                      )}
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Icon className="h-4 w-4 text-primary" />
                          <span className="font-semibold">
                            {item.kind === 'hashtag' && '#'}
                            {item.kind === 'user' && '@'}
                            {item.value}
                          </span>
                        </div>
                        {!isDemo && (
                          <Button
                            size="icon"
                            variant="ghost"
                            onClick={() => removeItem(i)}
                            aria-label="Remove"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {item.kind}
                      </Badge>
                      <p className="text-xs text-muted-foreground mt-2">
                        Added on{' '}
                        {format(new Date(item.created_at), 'MMM dd, yyyy', {
                          locale: enUS,
                        })}
                      </p>
                    </Card>
                  );
                })}
              </div>
            </section>

            {/* Analytics Performance */}
            <section>
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Performance & Trends
              </h2>
              <Card className="p-6">
                <Tabs value={activeTab} onValueChange={setActiveTab}>
                  <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="daily">7 days</TabsTrigger>
                    <TabsTrigger value="weekly">30 days</TabsTrigger>
                    <TabsTrigger value="monthly">90 days</TabsTrigger>
                    <TabsTrigger value="yearly">1 year</TabsTrigger>
                  </TabsList>
                  <TabsContent value={activeTab} className="mt-6">
                    <div className="space-y-6">
                      {/* Account Performance Chart */}
                      <div>
                        <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                          <User className="h-4 w-4" />
                          Account performance
                        </h3>
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={performanceData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                              <defs>
                                <linearGradient id="colorComptes" x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                                  <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                                </linearGradient>
                              </defs>
                              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                              <XAxis 
                                dataKey="date" 
                                className="text-xs text-muted-foreground"
                                tick={{ fill: 'currentColor' }}
                              />
                              <YAxis 
                                className="text-xs text-muted-foreground"
                                tick={{ fill: 'currentColor' }}
                              />
                              <Tooltip 
                                contentStyle={{ 
                                  backgroundColor: 'hsl(var(--card))',
                                  border: '1px solid hsl(var(--border))',
                                  borderRadius: '6px'
                                }}
                              />
                              <Legend />
                              <Area 
                                type="monotone" 
                                dataKey="comptes" 
                                name="Active accounts"
                                stroke="#8884d8" 
                                fillOpacity={1} 
                                fill="url(#colorComptes)" 
                              />
                            </AreaChart>
                          </ResponsiveContainer>
                        </div>
                      </div>

                      {/* Hashtag Performance Chart */}
                      <div>
                        <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                          <Hash className="h-4 w-4" />
                          Hashtag performance
                        </h3>
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={performanceData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                              <defs>
                                <linearGradient id="colorHashtags" x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8}/>
                                  <stop offset="95%" stopColor="#82ca9d" stopOpacity={0}/>
                                </linearGradient>
                              </defs>
                              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                              <XAxis 
                                dataKey="date" 
                                className="text-xs text-muted-foreground"
                                tick={{ fill: 'currentColor' }}
                              />
                              <YAxis 
                                className="text-xs text-muted-foreground"
                                tick={{ fill: 'currentColor' }}
                              />
                              <Tooltip 
                                contentStyle={{ 
                                  backgroundColor: 'hsl(var(--card))',
                                  border: '1px solid hsl(var(--border))',
                                  borderRadius: '6px'
                                }}
                              />
                              <Legend />
                              <Area 
                                type="monotone" 
                                dataKey="hashtags" 
                                name="Tracked hashtags"
                                stroke="#82ca9d" 
                                fillOpacity={1} 
                                fill="url(#colorHashtags)" 
                              />
                            </AreaChart>
                          </ResponsiveContainer>
                        </div>
                      </div>

                      {/* Post Performance Chart */}
                      <div>
                        <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                          <FileText className="h-4 w-4" />
                          Post performance
                        </h3>
                        <div className="h-64">
                          <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={performanceData} margin={{ top: 5, right: 10, left: 0, bottom: 0 }}>
                              <defs>
                                <linearGradient id="colorPosts" x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="5%" stopColor="#ffc658" stopOpacity={0.8}/>
                                  <stop offset="95%" stopColor="#ffc658" stopOpacity={0}/>
                                </linearGradient>
                              </defs>
                              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                              <XAxis 
                                dataKey="date" 
                                className="text-xs text-muted-foreground"
                                tick={{ fill: 'currentColor' }}
                              />
                              <YAxis 
                                className="text-xs text-muted-foreground"
                                tick={{ fill: 'currentColor' }}
                              />
                              <Tooltip 
                                contentStyle={{ 
                                  backgroundColor: 'hsl(var(--card))',
                                  border: '1px solid hsl(var(--border))',
                                  borderRadius: '6px'
                                }}
                              />
                              <Legend />
                              <Area 
                                type="monotone" 
                                dataKey="posts" 
                                name="Scraped posts"
                                stroke="#ffc658" 
                                fillOpacity={1} 
                                fill="url(#colorPosts)" 
                              />
                            </AreaChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </Card>
            </section>

            {/* Slides generation */}
            <section>
              <Card className="p-6 border-primary/20 bg-gradient-to-br from-primary/5 to-accent/5">
                <div className="flex items-start gap-4">
                  <div className="rounded-lg bg-primary/10 p-3">
                    <FileText className="h-6 w-6 text-primary" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold">Slide Generation</h3>
                      <Badge variant="secondary" className="text-xs">Coming soon</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-4">
                      Automatically create professional presentations from your watchlist data. Export to PowerPoint, Google Slides, or PDF.
                    </p>
                    <Button disabled title="Feature in development">
                      <FileText className="h-4 w-4 mr-2" />
                      Generate slides
                    </Button>
                  </div>
                </div>
              </Card>
            </section>
          </div>
        )}
      </main>
  );
}
