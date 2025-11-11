import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Search as SearchIcon, TrendingUp, Heart, MessageCircle, ExternalLink, Code2, Copy, CheckCircle2, RefreshCcw } from 'lucide-react';
import { searchPosts, fetchMetaOEmbed, getProjects, getProjectPosts, type PostHit } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { AISearchBar, type SearchMode } from '@/components/AISearchBar';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { useAuth } from '@/contexts/AuthContext';

export default function Search() {
  const defaultModes: SearchMode[] = ['hashtag'];
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [selectedModes, setSelectedModes] = useState<SearchMode[]>(defaultModes);
  const [posts, setPosts] = useState<PostHit[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [embedDialogOpen, setEmbedDialogOpen] = useState(false);
  const [selectedPost, setSelectedPost] = useState<PostHit | null>(null);
  const [embedCopied, setEmbedCopied] = useState(false);
  const [embedHtml, setEmbedHtml] = useState<string | null>(null);
  const [isFetchingEmbed, setIsFetchingEmbed] = useState(false);
  const [fetchingPostId, setFetchingPostId] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [fallbackNotice, setFallbackNotice] = useState<string | null>(null);
  const { toast } = useToast();

  const handleSearch = async (
    query: string,
    platforms: string[] = [],
    modes: SearchMode[] = defaultModes
  ) => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    setFallbackNotice(null);
    setHasSearched(true);
    setSearchQuery(query);
    setSelectedPlatforms(platforms);
    const normalizedModes = modes.length > 0 ? modes : defaultModes;
    setSelectedModes(normalizedModes);
    const normalizedPlatforms = platforms;
    const shouldFetchHashtag =
      normalizedModes.includes('hashtag') &&
      (normalizedPlatforms.length === 0 || normalizedPlatforms.includes('instagram'));
    const wantsCreator = normalizedModes.includes('creator');

    if (!shouldFetchHashtag && !wantsCreator) {
      setIsLoading(false);
      setPosts([]);
      toast({
        title: 'Select a search mode',
        description: 'Choose hashtag or creator to run a search.',
        variant: 'destructive',
      });
      return;
    }
    
    if (wantsCreator) {
      toast({
        title: 'Creator search coming soon',
        description: 'Creator lookup will be enabled once Meta permissions are confirmed. For now, try hashtag search.',
      });
    }
    
    try {
      const aggregatedPosts: PostHit[] = [];

      if (shouldFetchHashtag) {
        const response = await searchPosts({
          q: query,
          limit: 12,
        });
        const data = response.data || [];
        data.forEach((item: any) => {
          aggregatedPosts.push({
            id: item.id,
            platform: 'instagram',
            username: item.owner?.username,
            caption: item.caption,
            media_type: item.media_type,
            media_url: item.media_url,
            permalink: item.permalink,
            posted_at: item.timestamp,
            like_count: item.like_count,
            comment_count: item.comments_count,
            score_trend: item.like_count ?? 0,
          });
        });
      }

      setPosts(aggregatedPosts);
    } catch (error) {
      console.error('Search error:', error);
      await loadFallbackResults(query, normalizedModes);
    } finally {
      setIsLoading(false);
    }
  };

  const loadFallbackResults = async (query: string, modes: SearchMode[]) => {
    try {
      const projects = await getProjects();
      const aggregated: PostHit[] = [];

      for (const project of projects) {
        const projectPosts = await getProjectPosts(project.id);
        projectPosts.forEach((post) => {
          aggregated.push({
            id: post.id,
            platform: post.platform || 'instagram',
            username: post.author,
            caption: post.caption,
            media_type: post.media_url ? 'IMAGE' : undefined,
            media_url: post.media_url,
            permalink: post.permalink || (post.media_url?.startsWith('http') ? post.media_url : undefined),
            posted_at: post.posted_at,
            like_count: post.like_count,
            comment_count: post.comment_count,
            score_trend: post.score_trend,
          });
        });
      }

      const normalizedQuery = query.trim().toLowerCase();
      const filtered = aggregated.filter((item) => {
        const caption = (item.caption || '').toLowerCase();
        const username = (item.username || '').toLowerCase();
        const matchesHashtag = modes.includes('hashtag')
          ? caption.includes(`#${normalizedQuery}`) || caption.includes(normalizedQuery)
          : false;
        const matchesCreator = modes.includes('creator')
          ? username.includes(normalizedQuery.replace('@', ''))
          : false;
        return matchesHashtag || matchesCreator;
      });

      if (filtered.length === 0) {
        setPosts([]);
        toast({
          title: 'No results',
          description: 'No stored posts match your search query.',
        });
      } else {
        setFallbackNotice('Showing stored results (Meta API currently unavailable).');
        setPosts(filtered);
      }
    } catch (fallbackError) {
      console.error('Fallback search error:', fallbackError);
      setPosts([]);
      toast({
        title: 'Search failed',
        description: 'Unable to fetch posts. Please verify the search query and try again.',
        variant: 'destructive',
      });
    }
  };

  const fetchLivePost = async (post: PostHit) => {
    if (post.platform !== 'instagram' || !post.permalink) return;

    try {
      setFetchingPostId(post.id);
      await fetchMetaOEmbed(post.permalink);
      toast({
        title: 'Live fetch successful',
        description: 'Meta oEmbed response stored.',
      });
    } catch (error) {
      console.error('Fetch live error:', error);
      toast({
        title: 'Live fetch failed',
        description: 'Check console/logs for details.',
        variant: 'destructive',
      });
    } finally {
      setFetchingPostId(null);
    }
  };


  // Meta oEmbed Read functionality
  const getEmbedCode = (post: PostHit) => {
    return `<iframe
  src="${post.permalink}/embed"
  width="400"
  height="480"
  frameborder="0"
  scrolling="no"
  allowtransparency="true"
></iframe>`;
  };

  const handleCopyEmbed = () => {
    if (!selectedPost) return;
    const code = embedHtml || getEmbedCode(selectedPost);
    navigator.clipboard.writeText(code);
    setEmbedCopied(true);
    toast({
      title: "Embed code copied!",
      description: "Instagram post embed code copied to clipboard",
    });
    setTimeout(() => setEmbedCopied(false), 2000);
  };

  useEffect(() => {
    const loadEmbed = async () => {
      if (
        !embedDialogOpen ||
        !selectedPost?.permalink ||
        selectedPost.platform !== 'instagram'
      ) {
        setEmbedHtml(null);
        return;
      }
      setIsFetchingEmbed(true);
      try {
        const data = await fetchMetaOEmbed(selectedPost.permalink);
        const html = typeof data === 'string' ? data : data.html ?? '';
        setEmbedHtml(html);
      } catch (error) {
        console.error('Embed fetch error:', error);
        toast({
          title: 'Embed fetch failed',
          description: 'Unable to load oEmbed HTML from Meta.',
          variant: 'destructive',
        });
        setEmbedHtml(null);
      } finally {
        setIsFetchingEmbed(false);
      }
    };

    loadEmbed();
  }, [embedDialogOpen, selectedPost]);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="container py-8 md:py-12">
        <div className="flex flex-col items-center text-center space-y-6 max-w-4xl mx-auto">
          <div className="space-y-6">
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-gradient">
              Search
            </h1>
          </div>

          <div className="w-full">
            <AISearchBar onSearch={handleSearch} />
          </div>

          {/* Popular Tags */}
          <div className="flex flex-wrap gap-2 justify-center">
            <span className="text-sm text-muted-foreground">Popular:</span>
            {['fashion', 'makeup', 'fitness', 'travel', 'food'].map((tag) => (
              <Badge
                key={tag}
                variant="secondary"
                className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                onClick={() => handleSearch(tag, ['instagram'], selectedModes)}
              >
                #{tag}
              </Badge>
            ))}
          </div>

          <p className="text-xs text-muted-foreground">
            Mode tips: select <span className="font-semibold">Instagram</span> + <span className="font-semibold">Hashtag</span> to fetch public IG media,
            <span className="font-semibold"> Facebook</span> + <span className="font-semibold">Public Page</span> to fetch posts from a Facebook Page you do not manage,
            or select both to demonstrate both permissions in one search.
          </p>

        </div>
      </section>

      {/* Subtle Post Silhouettes - Background decoration when no search */}
      {!hasSearched && (
        <section className="container py-16 pb-32">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 opacity-[0.03]">
            {Array.from({ length: 12 }).map((_, i) => (
              <div key={i} className="space-y-3">
                {/* Image placeholder silhouette */}
                <div className="aspect-square rounded-lg border border-border/20 bg-muted/10" />
                {/* Content placeholder silhouettes */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full border border-border/20 bg-muted/10" />
                    <div className="flex-1 space-y-1">
                      <div className="h-3 w-20 rounded border border-border/20 bg-muted/10" />
                      <div className="h-2 w-16 rounded border border-border/20 bg-muted/10" />
                    </div>
                  </div>
                  <div className="h-2 w-full rounded border border-border/20 bg-muted/10" />
                  <div className="h-2 w-3/4 rounded border border-border/20 bg-muted/10" />
                  <div className="flex gap-4 mt-2">
                    <div className="h-2 w-12 rounded border border-border/20 bg-muted/10" />
                    <div className="h-2 w-12 rounded border border-border/20 bg-muted/10" />
                    <div className="h-2 w-12 rounded border border-border/20 bg-muted/10" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Search Results Section */}
      {hasSearched && (
        <section className="container py-4">
          {isLoading ? (
            <div className="text-center py-12">
              <div className="inline-flex h-16 w-16 items-center justify-center rounded-full bg-muted animate-pulse">
                <SearchIcon className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="font-semibold text-lg mt-4">Searching...</h3>
              <p className="text-muted-foreground">Finding trending content for you</p>
            </div>
          ) : posts.length > 0 ? (
            <div className="space-y-8">
              <div className="flex items-center justify-between">
                <h2 className="text-3xl font-bold">
                  Results for {searchQuery.startsWith('#') ? searchQuery : `#${searchQuery}`}
                </h2>
                <Badge variant="outline" className="text-sm">
                  {posts.length} posts found
                </Badge>
              </div>
              {fallbackNotice && (
                <p className="text-xs text-muted-foreground">{fallbackNotice}</p>
              )}
              {selectedModes.includes('creator') && !fallbackNotice && (
                <p className="text-xs text-muted-foreground">
                  Creator search will soon pull live posts from specific profiles. For now, use hashtag mode to explore trending content.
                </p>
              )}

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {posts.map((post) => (
                <Card key={post.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                  <div className="aspect-square relative overflow-hidden bg-muted">
                    {post.media_url ? (
                      <img
                        src={post.media_url}
                        alt={post.caption}
                        className="object-cover w-full h-full"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          target.src = `https://picsum.photos/800/800?random=${post.id}`;
                        }}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-muted/50">
                        <span className="text-muted-foreground text-sm">No image</span>
                      </div>
                    )}
                    <Badge className="absolute top-2 right-2 bg-accent">
                      {post.media_type || 'IMAGE'}
                    </Badge>
                  </div>
                  
                  <CardContent className="p-4 space-y-3">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-xs font-bold">
                        {post.username?.charAt(0).toUpperCase() || 'U'}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-sm truncate">{post.username || 'Unknown User'}</p>
                        <p className="text-xs text-muted-foreground truncate">@{post.username || 'unknown'}</p>
                      </div>
                    </div>

                    <p className="text-sm line-clamp-2">{post.caption}</p>

                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Heart className="h-4 w-4" />
                        <span>{(post.like_count / 1000).toFixed(1)}K</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MessageCircle className="h-4 w-4" />
                        <span>{((post.comment_count || 0) / 1000).toFixed(1)}K</span>
                      </div>
                      <div className="flex items-center gap-1 text-success">
                        <TrendingUp className="h-4 w-4" />
                        <span>{post.score_trend || 0}</span>
                      </div>
                    </div>

                    <div className="pt-2 border-t flex flex-wrap gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        asChild
                      >
                        <a href={post.permalink} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="h-3 w-3 mr-1" />
                          View on Instagram
                        </a>
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        onClick={() => fetchLivePost(post)}
                        disabled={fetchingPostId === post.id}
                      >
                        {fetchingPostId === post.id ? (
                          <span className="flex items-center gap-2"><RefreshCcw className="h-3 w-3 animate-spin" /> Fetching…</span>
                        ) : (
                          'Fetch Live'
                        )}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        onClick={() => {
                          setSelectedPost(post);
                          setEmbedDialogOpen(true);
                        }}
                      >
                        <Code2 className="h-3 w-3 mr-1" />
                        Embed
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
          ) : (
            <div className="text-center py-12">
              <div className="inline-flex h-16 w-16 items-center justify-center rounded-full bg-muted">
                <SearchIcon className="h-8 w-8 text-muted-foreground" />
              </div>
              <div className="mt-4">
                <h3 className="font-semibold text-lg">No results found</h3>
                <p className="text-muted-foreground">
                  Try searching for a different hashtag or check your spelling
                </p>
              </div>
            </div>
          )}
        </section>
      )}

      {/* Meta oEmbed Read Dialog */}
      <Dialog open={embedDialogOpen} onOpenChange={setEmbedDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Embed Instagram Post</DialogTitle>
            <DialogDescription>
              Meta oEmbed Read feature - Get embed HTML code for public Instagram posts
            </DialogDescription>
          </DialogHeader>

          {selectedPost && (
            <div className="space-y-4">
              <div className="flex gap-4">
                <img
                  src={selectedPost.media_url}
                  alt="Preview"
                  className="w-32 h-32 object-cover rounded-lg"
                />
                <div className="flex-1">
                  <p className="font-semibold">{selectedPost.username}</p>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {selectedPost.caption}
                  </p>
                  <div className="flex items-center gap-3 mt-2 text-sm">
                    <span>{((selectedPost.like_count || 0) / 1000).toFixed(1)}K likes</span>
                    <span>{((selectedPost.comment_count || 0) / 1000).toFixed(1)}K comments</span>
                  </div>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Embed Code:</label>
                <div className="relative">
                  <pre className="p-4 rounded-lg bg-muted text-xs overflow-x-auto">
                    <code>
                      {isFetchingEmbed
                        ? 'Loading oEmbed response...'
                        : embedHtml || getEmbedCode(selectedPost)}
                    </code>
                  </pre>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="absolute top-2 right-2"
                    onClick={handleCopyEmbed}
                    disabled={isFetchingEmbed}
                  >
                    {embedCopied ? (
                      <>
                        <CheckCircle2 className="h-4 w-4 mr-1 text-success" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4 mr-1" />
                        {isFetchingEmbed ? 'Wait' : 'Copy'}
                      </>
                    )}
                  </Button>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-accent/50 text-sm space-y-3">
                <div>
                <p className="font-medium mb-1">Meta oEmbed Read Permission</p>
                <p className="text-muted-foreground">
                  This feature allows you to get embed HTML and metadata for public Instagram posts
                  to provide front-end views in your application.
                </p>
                </div>
                {embedHtml && (
                  <div>
                    <p className="text-xs font-semibold mb-2">Live Preview (rendered from Meta response):</p>
                    <div
                      className="border rounded-lg overflow-hidden bg-background"
                      dangerouslySetInnerHTML={{ __html: embedHtml }}
                    />
                  </div>
                )}
                {!embedHtml && isFetchingEmbed && (
                  <p className="text-xs text-muted-foreground">Fetching live oEmbed data from Meta...</p>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Footer />
    </div>
  );
}
