import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Search as SearchIcon, TrendingUp, Heart, MessageCircle, ExternalLink, Code2, Copy, CheckCircle2 } from 'lucide-react';
import { generateMockPosts, type InstagramPost } from '@/lib/mockData';
import { searchPosts, type PostHit, type SearchParams } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { AISearchBar } from '@/components/AISearchBar';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { useAuth } from '@/contexts/AuthContext';

export default function Search() {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [posts, setPosts] = useState<PostHit[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [embedDialogOpen, setEmbedDialogOpen] = useState(false);
  const [selectedPost, setSelectedPost] = useState<PostHit | null>(null);
  const [embedCopied, setEmbedCopied] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const { toast } = useToast();

  const handleSearch = async (query: string, platforms: string[] = []) => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    setHasSearched(true);
    setSearchQuery(query);
    setSelectedPlatforms(platforms);
    
    try {
      const params: SearchParams = {
        q: query,
        platform: platforms.includes('instagram') ? 'instagram' : 'instagram', // Default to Instagram
        limit: 12,
        sort: 'score_trend:desc'
      };
      
      const response = await searchPosts(params);
      setPosts(response.hits);
    } catch (error) {
      console.error('Search error:', error);
      // Fallback to mock data if API fails
      setPosts(generateMockPosts(query, 12) as any);
    } finally {
      setIsLoading(false);
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
    navigator.clipboard.writeText(getEmbedCode(selectedPost));
    setEmbedCopied(true);
    toast({
      title: "Embed code copied!",
      description: "Instagram post embed code copied to clipboard",
    });
    setTimeout(() => setEmbedCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="container py-8 md:py-12">
        <div className="flex flex-col items-center text-center space-y-6 max-w-4xl mx-auto">
          <div className="space-y-6">
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-gradient">
              Search. Discover. Analyze.
            </h1>
            
            <p className="text-base md:text-lg text-muted-foreground max-w-3xl mx-auto">
              Search trending hashtags, analyze creator performance, and discover what's trending across social platforms
            </p>
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
                onClick={() => handleSearch(tag, ['instagram'])}
              >
                #{tag}
              </Badge>
            ))}
          </div>
        </div>
      </section>

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
                  Results for #{searchQuery}
                </h2>
                <Badge variant="outline" className="text-sm">
                  {posts.length} posts found
                </Badge>
              </div>

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

                    <div className="pt-2 border-t flex gap-2">
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
                    <code>{getEmbedCode(selectedPost)}</code>
                  </pre>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="absolute top-2 right-2"
                    onClick={handleCopyEmbed}
                  >
                    {embedCopied ? (
                      <>
                        <CheckCircle2 className="h-4 w-4 mr-1 text-success" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4 mr-1" />
                        Copy
                      </>
                    )}
                  </Button>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-accent/50 text-sm">
                <p className="font-medium mb-1">Meta oEmbed Read Permission</p>
                <p className="text-muted-foreground">
                  This feature allows you to get embed HTML and metadata for public Instagram posts
                  to provide front-end views in your application.
                </p>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Footer />
    </div>
  );
}
