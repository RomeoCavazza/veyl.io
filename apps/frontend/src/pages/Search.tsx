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

  // Charger posts depuis PostgreSQL - cherche dans tous les projets qui matchent la query
  const loadPostsFromDatabase = async (query: string): Promise<PostHit[]> => {
    try {
      const projects = await getProjects();
      
      // Chercher un projet qui contient la query dans son nom ou ses hashtags
      const matchingProject = projects.find((p: any) => {
        const nameMatch = p.name.toLowerCase().includes(query.toLowerCase());
        const hashtagMatch = p.hashtags?.some((h: any) => 
          h.name?.toLowerCase().includes(query.toLowerCase())
        );
        return nameMatch || hashtagMatch;
      });
      
      if (matchingProject) {
        console.log(`💾 [DB] Found matching project: ${matchingProject.name}`);
        const dbPosts = await getProjectPosts(matchingProject.id);
        
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
          like_count: post.like_count || 0,
          comment_count: post.comment_count || 0,
          score_trend: post.score_trend || 0,
        }));
      }
      
      console.log('💾 [DB] No matching project found');
      return [];
    } catch (error) {
      console.error('💾 [DB] Error:', error);
      return [];
    }
  };

  // 🔥 STRATÉGIE: 1. Meta API → 2. DB Fallback
  const handleSearch = async (query: string) => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    setHasSearched(true);
    setSearchQuery(query);

    try {
      console.log(`🔍 [SEARCH] Searching for: ${query}`);
      
      // 1️⃣ ESSAYER META API D'ABORD
      console.log('📡 [SEARCH] Step 1: Trying Meta API...');
      try {
        const metaResponse = await fetchMetaIGPublic(query, 20);
        
        if (metaResponse.status === 'success' && metaResponse.data && metaResponse.data.length > 0) {
          console.log(`✅ [SEARCH] Meta API success: ${metaResponse.data.length} posts`);
          const metaPosts: PostHit[] = metaResponse.data.map((item: any) => ({
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
          toast({
            title: `Found ${metaPosts.length} posts`,
            description: '✨ Live data from Meta API',
          });
          setIsLoading(false);
          return;
        }
        
        console.log('⚠️ [SEARCH] Meta API returned 0 results, trying DB fallback...');
      } catch (metaError: any) {
        console.log(`⚠️ [SEARCH] Meta API failed: ${metaError.message}, trying DB fallback...`);
      }
      
      // 2️⃣ FALLBACK: CHARGER DEPUIS DB
      console.log('💾 [SEARCH] Step 2: Loading from database...');
      const dbPosts = await loadPostsFromDatabase(query);
      
      if (dbPosts.length > 0) {
        console.log(`✅ [SEARCH] DB success: ${dbPosts.length} posts`);
        setPosts(dbPosts);
        toast({
          title: `Found ${dbPosts.length} posts`,
          description: '💾 Loaded from database (Meta API unavailable)',
        });
      } else {
        console.log('❌ [SEARCH] No posts in DB either');
        setPosts([]);
        toast({
          title: 'No results found',
          description: 'Neither Meta API nor database returned results.',
          variant: 'destructive',
        });
      }
      
    } catch (error: any) {
      console.error('❌ [SEARCH] Fatal error:', error);
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
