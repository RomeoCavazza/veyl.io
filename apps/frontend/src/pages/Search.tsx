import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Heart, MessageCircle, ExternalLink, RefreshCcw, Sparkles } from 'lucide-react';
import { fetchMetaIGPublic, getProjects, getProjectPosts, type PostHit } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { AISearchBar } from '@/components/AISearchBar';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';

export default function Search() {
  const [searchQuery, setSearchQuery] = useState('');
  const [posts, setPosts] = useState<PostHit[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [isTestingMetaAPI, setIsTestingMetaAPI] = useState(false);
  const { toast } = useToast();

  // Charger posts depuis PostgreSQL (fashion project)
  const loadPostsFromDatabase = async (): Promise<PostHit[]> => {
    try {
      const projects = await getProjects();
      const fashionProject = projects.find((p: any) => p.name.toLowerCase() === 'fashion');
      
      if (fashionProject) {
        const dbPosts = await getProjectPosts(fashionProject.id);
        // Convertir ProjectPost[] en PostHit[]
        return dbPosts.map((post: any) => ({
          id: post.id || post.external_id,
          platform: post.platform || 'instagram',
          username: post.author || 'unknown',
          caption: post.caption,
          media_type: post.media_type || 'image',
          media_url: post.media_url,
          permalink: post.permalink,
          posted_at: post.posted_at,
          like_count: post.metrics?.like_count || 0,
          comment_count: post.metrics?.comment_count || 0,
          score_trend: post.score_trend || 0,
        }));
      }
      return [];
    } catch (error) {
      console.error('[DB] Error:', error);
      return [];
    }
  };

  // Recherche simplifiée: charge depuis DB pour "fashion"
  const handleSearch = async (query: string) => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    setHasSearched(true);
    setSearchQuery(query);

    try {
      if (query.toLowerCase() === 'fashion') {
        const dbPosts = await loadPostsFromDatabase();
        
        if (dbPosts.length > 0) {
          setPosts(dbPosts);
          toast({
            title: `Found ${dbPosts.length} posts`,
            description: 'Loaded from your fashion project.',
          });
        } else {
          setPosts([]);
          toast({
            title: 'No stored posts',
            description: 'Run the link script first, or use "Test Live Meta API"',
          });
        }
      } else {
        setPosts([]);
        toast({
          title: 'Search "fashion"',
          description: 'Only "fashion" hashtag is populated for the demo.',
        });
      }
    } catch (error: any) {
      console.error('[SEARCH] Error:', error);
      setPosts([]);
      toast({
        title: 'Search failed',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Tester Meta API en live (pour App Review)
  const testMetaAPI = async () => {
    if (!searchQuery) {
      toast({
        title: 'Enter a search query first',
        variant: 'destructive',
      });
      return;
    }

    setIsTestingMetaAPI(true);
    try {
      console.log('[META API] Testing:', searchQuery);
      const response = await fetchMetaIGPublic(searchQuery, 10);
      console.log('[META API] Response:', response);

      toast({
        title: 'Meta API call completed',
        description: `Status: ${response.status}, Check Network tab for details.`,
      });

      if (response.status === 'success' && response.data?.length > 0) {
        const metaPosts: PostHit[] = response.data.map((item: any) => ({
          id: item.id,
          platform: 'instagram',
          username: item.username || 'unknown',
          caption: item.caption,
          media_type: item.media_type,
          media_url: item.media_url,
          permalink: item.permalink,
          posted_at: item.timestamp,
          like_count: item.like_count,
          comment_count: item.comments_count,
          score_trend: item.like_count ?? 0,
        }));
        setPosts(metaPosts);
      }
    } catch (error: any) {
      console.error('[META API] Error:', error);
      toast({
        title: 'Meta API error',
        description: 'Check Network tab - should show HTTP call attempt',
        variant: 'destructive',
      });
    } finally {
      setIsTestingMetaAPI(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero */}
      <section className="container py-8 md:py-12">
        <div className="flex flex-col items-center text-center space-y-6 max-w-4xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-gradient">
            Search
          </h1>

          <div className="w-full">
            <AISearchBar onSearch={handleSearch} />
          </div>

          {/* Popular Tags */}
          <div className="flex flex-wrap gap-2 justify-center">
            <span className="text-sm text-muted-foreground">Popular:</span>
            {['fashion', 'makeup', 'fitness'].map((tag) => (
              <Badge
                key={tag}
                variant="secondary"
                className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-colors"
                onClick={() => handleSearch(tag)}
              >
                #{tag}
              </Badge>
            ))}
          </div>

          {/* Test Meta API Button */}
          {hasSearched && posts.length > 0 && (
            <div className="flex gap-3 items-center">
              <Button
                onClick={testMetaAPI}
                disabled={isTestingMetaAPI}
                variant="outline"
                size="sm"
                className="gap-2"
              >
                {isTestingMetaAPI ? (
                  <>
                    <RefreshCcw className="h-4 w-4 animate-spin" />
                    Testing...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    Test Live Meta API
                  </>
                )}
              </Button>
              <span className="text-xs text-muted-foreground">
                (For App Review demo - check Network tab)
              </span>
            </div>
          )}
        </div>
      </section>

      {/* Results */}
      {isLoading ? (
        <section className="container py-8">
          <div className="text-center">Loading...</div>
        </section>
      ) : hasSearched ? (
        <section className="container py-8">
          {posts.length > 0 ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {posts.map((post) => (
                <Card key={post.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                  <CardContent className="p-0">
                    {/* Instagram Embed */}
                    {post.permalink && (
                      <div className="aspect-square bg-muted relative">
                        <iframe
                          src={`https://www.instagram.com/p/${post.permalink.split('/p/')[1]?.replace('/', '')}/embed`}
                          className="w-full h-full border-0"
                          scrolling="no"
                          allowTransparency
                        />
                      </div>
                    )}

                    {/* Content */}
                    <div className="p-4 space-y-3">
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">
                          {post.platform || 'instagram'}
                        </Badge>
                        {post.username && (
                          <span className="text-sm font-medium">@{post.username}</span>
                        )}
                      </div>

                      {post.caption && (
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {post.caption}
                        </p>
                      )}

                      <div className="flex items-center justify-between text-sm">
                        <div className="flex gap-4">
                          {post.like_count !== undefined && (
                            <span className="flex items-center gap-1">
                              <Heart className="h-4 w-4" />
                              {post.like_count}
                            </span>
                          )}
                          {post.comment_count !== undefined && (
                            <span className="flex items-center gap-1">
                              <MessageCircle className="h-4 w-4" />
                              {post.comment_count}
                            </span>
                          )}
                        </div>

                        {post.permalink && (
                          <a
                            href={post.permalink}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:underline"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No results found</p>
              <p className="text-sm text-muted-foreground mt-2">
                Try searching for "fashion" or run the link script
              </p>
            </div>
          )}
        </section>
      ) : null}

      <Footer />
    </div>
  );
}
