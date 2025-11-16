import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Heart, MessageCircle, ExternalLink, RefreshCcw, Sparkles } from 'lucide-react';
import { fetchMetaIGPublic, fetchTikTokVideos, getProjects, getProjectPosts, type PostHit } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { AISearchBar, type SearchMode } from '@/components/AISearchBar';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';

export default function Search() {
  const [searchQuery, setSearchQuery] = useState('');
  const [posts, setPosts] = useState<PostHit[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [isTestingMetaAPI, setIsTestingMetaAPI] = useState(false);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const { toast } = useToast();

  // Charger posts depuis PostgreSQL - cherche dans tous les projets qui matchent la query
  const loadPostsFromDatabase = async (query: string): Promise<PostHit[]> => {
    if (typeof window === 'undefined') return [];
    const token = localStorage.getItem('token');
    if (!token) {
      console.log('💾 [DB] Skipping DB fallback - no auth token');
      return [];
    }

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

  // 🔥 STRATÉGIE: 1. API (Meta/TikTok selon platforms) → 2. DB Fallback
  const handleSearch = async (
    query: string, 
    platforms?: string[], 
    modes?: SearchMode[]
  ) => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    setHasSearched(true);
    setSearchQuery(query);
    
    // Si platforms est fourni, l'utiliser, sinon utiliser selectedPlatforms, sinon vide (toutes)
    const activePlatforms = platforms || selectedPlatforms;
    setSelectedPlatforms(activePlatforms);
    
    // Déterminer quelles plateformes utiliser
    const useInstagram = activePlatforms.length === 0 || activePlatforms.includes('instagram');
    const useTikTok = activePlatforms.includes('tiktok');

    try {
      console.log(`🔍 [SEARCH] Searching for: ${query} on platforms: ${activePlatforms.join(', ') || 'all'}`);
      
      const allPosts: PostHit[] = [];
      
      // 1️⃣ ESSAYER META API (Instagram) SI DEMANDÉ
      if (useInstagram) {
        console.log('📡 [SEARCH] Step 1: Trying Meta API (Instagram)...');
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
            allPosts.push(...metaPosts);
          } else {
            console.log('⚠️ [SEARCH] Meta API returned 0 results');
          }
        } catch (metaError: any) {
          console.log(`⚠️ [SEARCH] Meta API failed: ${metaError.message}`);
        }
      }
      
      // 2️⃣ ESSAYER TIKTOK API SI DEMANDÉ
      if (useTikTok) {
        console.log('📡 [SEARCH] Step 2: Trying TikTok API...');
        try {
          const tiktokResponse = await fetchTikTokVideos(query, 20);
          
          if (tiktokResponse.status === 'success' && tiktokResponse.data && tiktokResponse.data.length > 0) {
            console.log(`✅ [SEARCH] TikTok API success: ${tiktokResponse.data.length} videos`);
            const tiktokPosts: PostHit[] = tiktokResponse.data.map((item: any) => ({
              id: item.id,
              platform: 'tiktok',
              username: item.creator_username || item.creator_display_name || 'unknown',
              caption: item.title || item.video_description,
              media_type: 'video',
              media_url: item.cover_image_url || item.thumbnail_url,
              permalink: item.share_url || `https://www.tiktok.com/@${item.creator_username || 'user'}/video/${item.id}`,
              posted_at: item.create_time,
              like_count: item.like_count || 0,
              comment_count: item.comment_count || 0,
              view_count: item.view_count || 0,
              score_trend: item.like_count ?? 0,
            }));
            allPosts.push(...tiktokPosts);
          } else {
            console.log('⚠️ [SEARCH] TikTok API returned 0 results');
          }
        } catch (tiktokError: any) {
          console.log(`⚠️ [SEARCH] TikTok API failed: ${tiktokError.message}`);
        }
      }
      
      // 3️⃣ FALLBACK: CHARGER DEPUIS DB SI AUCUN RÉSULTAT API
      if (allPosts.length === 0) {
        console.log('💾 [SEARCH] Step 3: Loading from database (fallback)...');
        const dbPosts = await loadPostsFromDatabase(query);
        
        if (dbPosts.length > 0) {
          console.log(`✅ [SEARCH] DB success: ${dbPosts.length} posts`);
          allPosts.push(...dbPosts);
        }
      }
      
      // Trier par date (plus récent en premier)
      allPosts.sort((a, b) => {
        const dateA = a.posted_at ? new Date(a.posted_at).getTime() : 0;
        const dateB = b.posted_at ? new Date(b.posted_at).getTime() : 0;
        return dateB - dateA;
      });
      
      if (allPosts.length > 0) {
        console.log(`✅ [SEARCH] Total results: ${allPosts.length} posts`);
        setPosts(allPosts);
        const sources = [];
        if (useInstagram) sources.push('Instagram');
        if (useTikTok) sources.push('TikTok');
        toast({
          title: `Found ${allPosts.length} posts`,
          description: allPosts.length > 0 && allPosts[0].platform === 'instagram' && useInstagram
            ? '✨ Live data from Meta API'
            : allPosts.length > 0 && allPosts[0].platform === 'tiktok' && useTikTok
            ? '✨ Live data from TikTok API'
            : `💾 Loaded from ${sources.join(' + ')} (${allPosts.length > 0 ? 'API + ' : ''}database)`,
        });
      } else {
        console.log('❌ [SEARCH] No posts found');
        setPosts([]);
        toast({
          title: 'No results found',
          description: 'Neither API nor database returned results.',
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
            <AISearchBar onSearch={(query, platforms, modes) => handleSearch(query, platforms, modes)} />
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

          {/* Test Meta API Button - Only show if Instagram is selected or no platform selected */}
          {hasSearched && posts.length > 0 && (selectedPlatforms.length === 0 || selectedPlatforms.includes('instagram')) && (
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
                    {/* Media Display - Instagram Embed or TikTok Thumbnail */}
                    {post.platform === 'instagram' && post.permalink && (
                      <div className="aspect-square bg-muted relative">
                        <iframe
                          src={`https://www.instagram.com/p/${post.permalink.split('/p/')[1]?.replace('/', '')}/embed`}
                          className="w-full h-full border-0"
                          scrolling="no"
                          allowTransparency
                        />
                      </div>
                    )}
                    {post.platform === 'tiktok' && post.media_url && (
                      <div className="aspect-square bg-muted relative overflow-hidden">
                        <img
                          src={post.media_url}
                          alt={post.caption || 'TikTok video'}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400x400?text=TikTok';
                          }}
                        />
                        <div className="absolute inset-0 flex items-center justify-center bg-black/20">
                          <Badge variant="secondary" className="absolute top-2 right-2">
                            TikTok
                          </Badge>
                        </div>
                      </div>
                    )}
                    {!post.permalink && !post.media_url && (
                      <div className="aspect-square bg-muted flex items-center justify-center">
                        <span className="text-muted-foreground text-sm">No media</span>
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
