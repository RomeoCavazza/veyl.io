import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Heart, MessageCircle, ExternalLink, RefreshCcw, Sparkles, Code2 } from 'lucide-react';
import { fetchMetaIGPublic, fetchTikTokVideos, getProjects, getProjectPosts, type PostHit } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { AISearchBar, type SearchMode } from '@/components/AISearchBar';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { EmbedDialog } from '@/components/EmbedDialog';

export default function Search() {
  const [searchQuery, setSearchQuery] = useState('');
  const [posts, setPosts] = useState<PostHit[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [isTestingAPI, setIsTestingAPI] = useState(false);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [embedDialogOpen, setEmbedDialogOpen] = useState(false);
  const [selectedPostForEmbed, setSelectedPostForEmbed] = useState<PostHit | null>(null);
  const { toast } = useToast();

  // Charger posts depuis PostgreSQL - cherche dans tous les projets qui matchent la query
  // Filtre par plateforme si spécifiée
  const loadPostsFromDatabase = async (query: string, platforms?: string[]): Promise<PostHit[]> => {
    if (typeof window === 'undefined') return [];
    const token = localStorage.getItem('token');
    if (!token) {
      if (import.meta.env.DEV) {
        console.log('💾 [DB] Skipping DB fallback - no auth token');
      }
      return [];
    }

    try {
      const projects = await getProjects();
      
      // Chercher un projet qui contient la query dans son nom ou ses hashtags
      const matchingProject = projects.find((p) => {
        const nameMatch = p.name.toLowerCase().includes(query.toLowerCase());
        const hashtagMatch = p.hashtags?.some((h) => 
          h.name?.toLowerCase().includes(query.toLowerCase())
        );
        return nameMatch || hashtagMatch;
      });
      
      if (matchingProject) {
        if (import.meta.env.DEV) {
          console.log(`💾 [DB] Found matching project: ${matchingProject.name}`);
        }
        const dbPosts = await getProjectPosts(matchingProject.id);
        
        // Convertir ProjectPost[] en PostHit[] et filtrer par plateforme
        let filteredPosts = dbPosts.map((post) => {
          // Extraire username depuis permalink si author/username manquant
          let username = post.username || post.author;
          if (!username && post.permalink) {
            const permalinkMatch = post.permalink.match(/instagram\.com\/([^/]+)/);
            if (permalinkMatch && !['p', 'reel', 'tv', 'stories'].includes(permalinkMatch[1])) {
              username = permalinkMatch[1];
            }
          }
          
          return {
            id: post.id || post.external_id,
            platform: post.platform || 'instagram',
            username: username || undefined, // undefined plutôt que 'unknown'
            author: username || undefined, // Alias pour compatibilité
            caption: post.caption,
            media_type: post.media_type || 'image',
            media_url: post.media_url,
            permalink: post.permalink,
            posted_at: post.posted_at,
            like_count: post.like_count ?? null,
            comment_count: post.comment_count ?? null,
            score_trend: post.score_trend || 0,
          };
        });
        
        // Filtrer par plateforme si spécifiée
        if (platforms && platforms.length > 0) {
          filteredPosts = filteredPosts.filter((post) => {
            // Mapper les noms de plateformes
            const platformMap: Record<string, string[]> = {
              'instagram': ['instagram'],
              'facebook': ['facebook'],
              'tiktok': ['tiktok'],
            };
            
            // Vérifier si la plateforme du post correspond à une des plateformes demandées
            return platforms.some((reqPlatform) => {
              const mappedPlatforms = platformMap[reqPlatform] || [reqPlatform];
              return mappedPlatforms.includes(post.platform);
            });
          });
          if (import.meta.env.DEV) {
            console.log(`💾 [DB] Filtered by platforms [${platforms.join(', ')}]: ${filteredPosts.length} posts`);
          }
        }
        
        return filteredPosts;
      }
      
      if (import.meta.env.DEV) {
        console.log('💾 [DB] No matching project found');
      }
      return [];
    } catch (error) {
      if (import.meta.env.DEV) {
        console.error('💾 [DB] Error:', error);
      }
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
      if (import.meta.env.DEV) {
        console.log(`🔍 [SEARCH] Searching for: ${query} on platforms: ${activePlatforms.join(', ') || 'all'}`);
      }
      
      const allPosts: PostHit[] = [];
      
      let apiSuccess = false;
      
      // 1️⃣ ESSAYER META API (Instagram) SI DEMANDÉ - PRIORITAIRE
      if (useInstagram) {
        if (import.meta.env.DEV) {
          console.log('📡 [SEARCH] Step 1: Trying Meta API (Instagram) - PRIORITY...');
        }
        try {
          const metaResponse = await fetchMetaIGPublic(query, 20);
          
          // L'endpoint renvoie {"data": [...], "source": "meta_api" | "database_fallback"}
          if (metaResponse && metaResponse.data && Array.isArray(metaResponse.data) && metaResponse.data.length > 0) {
            const source = metaResponse.source || 'unknown';
            if (import.meta.env.DEV) {
              console.log(`✅ [SEARCH] Meta API SUCCESS: ${metaResponse.data.length} posts from ${source}`);
            }
            apiSuccess = true;
            const metaPosts: PostHit[] = metaResponse.data.map((item: any) => ({
              id: item.id,
              platform: 'instagram',
              username: item.username || item.author || undefined,
              author: item.username || item.author || undefined,
              caption: item.caption,
              media_type: item.media_type,
              media_url: item.media_url,
              permalink: item.permalink,
              posted_at: item.timestamp || item.posted_at,
              like_count: item.like_count ?? null,
              comment_count: item.comments_count || item.comment_count ?? null,
              score_trend: item.like_count ?? 0,
            }));
            allPosts.push(...metaPosts);
          } else {
            if (import.meta.env.DEV) {
              console.log(`⚠️ [SEARCH] Meta API returned 0 results (source: ${metaResponse?.source || 'unknown'})`);
            }
          }
        } catch (metaError: unknown) {
          if (import.meta.env.DEV) {
            const errorMessage = metaError instanceof Error ? metaError.message : String(metaError);
            console.error(`❌ [SEARCH] Meta API FAILED: ${errorMessage} - Will fallback to DB`);
          }
        }
      }
      
      // 2️⃣ ESSAYER TIKTOK API SI DEMANDÉ - PRIORITAIRE
      if (useTikTok) {
        if (import.meta.env.DEV) {
          console.log('📡 [SEARCH] Step 2: Trying TikTok API - PRIORITY...');
        }
        try {
          const tiktokResponse = await fetchTikTokVideos(query, 20);
          
          if (tiktokResponse.status === 'success' && tiktokResponse.data && tiktokResponse.data.length > 0) {
            const source = tiktokResponse.meta?.source || 'unknown';
            if (source === 'tiktok_video_list_api') {
              if (import.meta.env.DEV) {
                console.log(`✅ [SEARCH] TikTok API SUCCESS: ${tiktokResponse.data.length} videos from API`);
              }
              apiSuccess = true;
            } else {
              if (import.meta.env.DEV) {
                console.log(`⚠️ [SEARCH] TikTok returned ${tiktokResponse.data.length} videos from DB (source: ${source})`);
              }
            }
            
            const tiktokPosts: PostHit[] = tiktokResponse.data.map((item) => ({
              id: item.id,
              platform: 'tiktok',
              username: item.creator_username || item.creator_display_name || undefined,
              author: item.creator_username || item.creator_display_name || undefined,
              caption: item.title || item.video_description,
              media_type: 'video',
              media_url: item.cover_image_url || item.thumbnail_url,
              thumbnail_url: item.thumbnail_url,
              permalink: item.share_url || `https://www.tiktok.com/@${item.creator_username || 'user'}/video/${item.id}`,
              posted_at: item.create_time,
              like_count: item.like_count ?? null,
              comment_count: item.comment_count ?? null,
              view_count: item.view_count || 0,
              score_trend: item.like_count ?? 0,
            }));
            allPosts.push(...tiktokPosts);
          } else {
            if (import.meta.env.DEV) {
              console.log(`⚠️ [SEARCH] TikTok API returned 0 results (status: ${tiktokResponse.status})`);
            }
          }
        } catch (tiktokError: unknown) {
          if (import.meta.env.DEV) {
            const errorMessage = tiktokError instanceof Error ? tiktokError.message : String(tiktokError);
            console.error(`❌ [SEARCH] TikTok API FAILED: ${errorMessage} - Will fallback to DB`);
          }
        }
      }
      
      // 3️⃣ FALLBACK: CHARGER DEPUIS DB SI API ÉCHOUÉ OU AUCUN RÉSULTAT
      if (!apiSuccess || allPosts.length === 0) {
        if (import.meta.env.DEV) {
          console.log(`💾 [SEARCH] Step 3: Loading from database (fallback) - API success: ${apiSuccess}, Posts: ${allPosts.length}...`);
        }
        const dbPosts = await loadPostsFromDatabase(query, activePlatforms);
        
        if (dbPosts.length > 0) {
          if (import.meta.env.DEV) {
            console.log(`✅ [SEARCH] DB fallback success: ${dbPosts.length} posts`);
          }
          // Éviter les doublons
          const existingIds = new Set(allPosts.map(p => p.id));
          const newDbPosts = dbPosts.filter(p => !existingIds.has(p.id));
          allPosts.push(...newDbPosts);
        } else {
          if (import.meta.env.DEV) {
            console.log(`⚠️ [SEARCH] No posts found in DB either`);
          }
        }
      }
      
      // Trier par date (plus récent en premier)
      allPosts.sort((a, b) => {
        const dateA = a.posted_at ? new Date(a.posted_at).getTime() : 0;
        const dateB = b.posted_at ? new Date(b.posted_at).getTime() : 0;
        return dateB - dateA;
      });
      
      if (allPosts.length > 0) {
        if (import.meta.env.DEV) {
          console.log(`✅ [SEARCH] Total results: ${allPosts.length} posts`);
        }
        setPosts(allPosts);
        const sources = [];
        if (useInstagram) sources.push('Instagram');
        if (useTikTok) sources.push('TikTok');
        toast({
          title: `Found ${allPosts.length} posts`,
          description: apiSuccess && allPosts.length > 0
            ? `✨ Live data from ${sources.join(' + ')} API`
            : `💾 Loaded from database`,
        });
      } else {
        if (import.meta.env.DEV) {
          console.log('❌ [SEARCH] No posts found');
        }
        setPosts([]);
        toast({
          title: 'No results found',
          description: 'Neither API nor database returned results.',
          variant: 'destructive',
        });
      }
      
    } catch (error: unknown) {
      if (import.meta.env.DEV) {
        console.error('❌ [SEARCH] Fatal error:', error);
      }
      setPosts([]);
      const errorMessage = error instanceof Error ? error.message : String(error);
      toast({
        title: 'Search failed',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Tester API en live - adaptatif selon les plateformes sélectionnées
  const testAPI = async () => {
    if (!searchQuery) {
      toast({
        title: 'Enter a search query first',
        variant: 'destructive',
      });
      return;
    }

    setIsTestingAPI(true);
    
    // Déterminer quelles plateformes tester
    const platformsToTest = selectedPlatforms.length > 0 ? selectedPlatforms : ['instagram', 'facebook', 'tiktok', 'x'];
    const useInstagram = platformsToTest.includes('instagram');
    const useFacebook = platformsToTest.includes('facebook');
    const useTikTok = platformsToTest.includes('tiktok');
    const useX = platformsToTest.includes('x');
    
    const allPosts: PostHit[] = [];
    const results: { platform: string; success: boolean; count: number; error?: string }[] = [];
    
    try {
      // Tester Instagram API
      if (useInstagram) {
        try {
          if (import.meta.env.DEV) {
            console.log('📡 [TEST API] Testing Instagram API for:', searchQuery);
          }
          const response = await fetchMetaIGPublic(searchQuery, 10);
          const source = response?.source || 'unknown';
          
          // L'endpoint renvoie {"data": [...], "source": "meta_api" | "database_fallback"}
          if (response && response.data && Array.isArray(response.data) && response.data.length > 0) {
            if (import.meta.env.DEV) {
              console.log(`✅ [TEST API] Instagram SUCCESS: ${response.data.length} posts (source: ${source})`);
            }
            const metaPosts: PostHit[] = response.data.map((item: any) => ({
              id: item.id,
              platform: 'instagram',
              username: item.username || item.author || 'unknown',
              caption: item.caption,
              media_type: item.media_type,
              media_url: item.media_url,
              permalink: item.permalink,
              posted_at: item.timestamp || item.posted_at,
              like_count: item.like_count || 0,
              comment_count: item.comments_count || item.comment_count || 0,
              score_trend: item.like_count ?? 0,
            }));
            allPosts.push(...metaPosts);
            results.push({ platform: 'Instagram', success: true, count: response.data.length });
          } else {
            const errorMsg = response?.data?.length === 0 ? 'No results found' : 'Invalid response format';
            if (import.meta.env.DEV) {
              console.log(`⚠️ [TEST API] Instagram returned 0 results (source: ${source})`);
            }
            results.push({ platform: 'Instagram', success: false, count: 0, error: errorMsg });
          }
        } catch (error: unknown) {
          if (import.meta.env.DEV) {
            console.error('❌ [TEST API] Instagram FAILED:', error);
          }
          const errorMessage = error instanceof Error ? error.message : String(error);
          results.push({ platform: 'Instagram', success: false, count: 0, error: errorMessage });
        }
      }
      
      // Tester Facebook API (utilise la même API Meta)
      if (useFacebook) {
        try {
          if (import.meta.env.DEV) {
            console.log('📡 [TEST API] Testing Facebook API for:', searchQuery);
          }
          // Facebook utilise la même API Meta mais avec page_id
          // Pour l'instant, on log juste
          results.push({ platform: 'Facebook', success: false, count: 0, error: 'Not implemented yet' });
        } catch (error: unknown) {
          if (import.meta.env.DEV) {
            console.error('❌ [TEST API] Facebook FAILED:', error);
          }
          const errorMessage = error instanceof Error ? error.message : String(error);
          results.push({ platform: 'Facebook', success: false, count: 0, error: errorMessage });
        }
      }
      
      // Tester TikTok API
      if (useTikTok) {
        try {
          if (import.meta.env.DEV) {
            console.log('📡 [TEST API] Testing TikTok API for:', searchQuery);
          }
          const response = await fetchTikTokVideos(searchQuery, 10);
          const source = response.meta?.source || 'unknown';
          const success = response.status === 'success' && response.data?.length > 0;
          
          if (success) {
            if (import.meta.env.DEV) {
              console.log(`✅ [TEST API] TikTok SUCCESS: ${response.data.length} videos (source: ${source})`);
            }
            const tiktokPosts: PostHit[] = response.data.map((item) => ({
              id: item.id,
              platform: 'tiktok',
              username: item.creator_username || item.creator_display_name || 'unknown',
              caption: item.title || item.video_description,
              media_type: 'video',
              media_url: item.cover_image_url || item.thumbnail_url,
              permalink: item.share_url || `https://www.tiktok.com/@${item.creator_username || 'user'}/video/${item.id}`,
              posted_at: item.create_time,
              like_count: item.like_count ?? null,
              comment_count: item.comment_count ?? null,
              view_count: item.view_count || 0,
              score_trend: item.like_count ?? 0,
            }));
            allPosts.push(...tiktokPosts);
            results.push({ platform: 'TikTok', success: true, count: response.data.length });
          } else {
            results.push({ platform: 'TikTok', success: false, count: 0, error: `Status: ${response.status}` });
          }
        } catch (error: unknown) {
          if (import.meta.env.DEV) {
            console.error('❌ [TEST API] TikTok FAILED:', error);
          }
          const errorMessage = error instanceof Error ? error.message : String(error);
          results.push({ platform: 'TikTok', success: false, count: 0, error: errorMessage });
        }
      }
      
      // Tester X API (pas encore implémenté)
      if (useX) {
        results.push({ platform: 'X', success: false, count: 0, error: 'Not implemented yet' });
      }
      
      // Afficher les résultats
      if (allPosts.length > 0) {
        setPosts(allPosts);
      }
      
      const successCount = results.filter(r => r.success).length;
      const totalCount = results.reduce((sum, r) => sum + r.count, 0);
      
      toast({
        title: `API Test completed`,
        description: `${successCount}/${results.length} platforms succeeded, ${totalCount} total posts`,
      });
      
    } catch (error: unknown) {
      if (import.meta.env.DEV) {
        console.error('❌ [TEST API] Fatal error:', error);
      }
      const errorMessage = error instanceof Error ? error.message : String(error);
      toast({
        title: 'API Test error',
        description: errorMessage || 'Check Network tab for details',
        variant: 'destructive',
      });
    } finally {
      setIsTestingAPI(false);
    }
  };
  
  // Déterminer le texte du bouton selon les plateformes sélectionnées
  const getTestButtonText = () => {
    if (selectedPlatforms.length === 0) {
      return 'Test All';
    } else if (selectedPlatforms.length === 1) {
      const platform = selectedPlatforms[0];
      const labels: Record<string, string> = {
        'instagram': 'Instagram',
        'facebook': 'Facebook',
        'tiktok': 'TikTok',
        'x': 'X',
      };
      return `Test ${labels[platform] || platform}`;
    } else {
      return 'Test All';
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

          {/* Test API Button - adaptatif selon les plateformes sélectionnées */}
          {hasSearched && (
            <div className="flex gap-2 items-center flex-wrap justify-center">
              <Button
                onClick={testAPI}
                disabled={isTestingAPI}
                variant="outline"
                size="sm"
                className="gap-1.5 h-8 text-xs"
              >
                {isTestingAPI ? (
                  <>
                    <RefreshCcw className="h-3 w-3 animate-spin" />
                    Testing...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-3 w-3" />
                    {getTestButtonText()}
                  </>
                )}
              </Button>
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
              {posts.map((post) => {
                // Extraire username pour l'affichage
                let username = post.username || post.author;
                if (!username && post.permalink) {
                  const permalinkMatch = post.permalink.match(/instagram\.com\/([^/]+)/);
                  if (permalinkMatch && !['p', 'reel', 'tv', 'stories'].includes(permalinkMatch[1])) {
                    username = permalinkMatch[1];
                  }
                }
                
                // Déterminer si c'est une image
                const isImage = post.media_url ? /\.(jpg|jpeg|png|gif|webp)$/i.test(post.media_url.split('?')[0]) : false;
                const embedUrl = post.permalink ? `${post.permalink.replace(/\/$/, '')}/embed` : undefined;
                
                return (
                <Card key={post.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                  <CardContent className="p-0">
                    {/* Media Display - Aligné avec ProjectPostsList */}
                    <div className="aspect-square relative overflow-hidden bg-muted">
                      {post.platform === 'tiktok' ? (
                        post.media_url || post.thumbnail_url ? (
                          <img
                            src={post.thumbnail_url || post.media_url}
                            alt={post.caption || username || 'TikTok video'}
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              const img = e.target as HTMLImageElement;
                              img.style.display = 'none';
                              const placeholder = img.parentElement?.querySelector('.tiktok-placeholder') as HTMLElement;
                              if (placeholder) placeholder.style.display = 'flex';
                            }}
                          />
                        ) : null
                      ) : post.media_url && isImage ? (
                        <img
                          src={post.media_url}
                          alt={post.caption || username || 'Instagram post'}
                          className="object-cover w-full h-full"
                        />
                      ) : embedUrl ? (
                        <iframe
                          src={embedUrl}
                          title={post.id}
                          className="w-full h-full"
                          allow="autoplay; clipboard-write; encrypted-media; picture-in-picture"
                        />
                      ) : null}
                      {post.platform === 'tiktok' && (
                        <div className={`tiktok-placeholder w-full h-full bg-gradient-to-br from-pink-500 via-red-500 to-blue-500 flex flex-col items-center justify-center text-white ${post.media_url || post.thumbnail_url ? 'hidden' : ''}`}>
                          <svg className="w-16 h-16 mb-2" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"/>
                          </svg>
                          <span className="text-sm font-medium">TikTok Video</span>
                        </div>
                      )}
                      {!post.media_url && !embedUrl && post.platform !== 'tiktok' && (
                        <div className="w-full h-full flex items-center justify-center bg-muted/50">
                          <span className="text-muted-foreground text-sm">No media</span>
                        </div>
                      )}
                    </div>
                  
                    {/* Content */}
                    <div className="p-4 space-y-3">
                    <div className="flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">
                          {post.platform || 'instagram'}
                        </Badge>
                        {(() => {
                          // Extraire username depuis permalink si manquant
                          let displayUsername = post.username || post.author;
                          if (!displayUsername && post.permalink) {
                            const permalinkMatch = post.permalink.match(/instagram\.com\/([^/]+)/);
                            if (permalinkMatch && !['p', 'reel', 'tv', 'stories'].includes(permalinkMatch[1])) {
                              displayUsername = permalinkMatch[1];
                            }
                          }
                          return displayUsername ? (
                            <span className="text-sm font-medium">@{displayUsername}</span>
                          ) : null;
                        })()}
                    </div>

                      {post.caption && (
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {post.caption}
                        </p>
                      )}

                      <div className="flex items-center justify-between text-sm">
                        <div className="flex gap-4">
                          <span className="flex items-center gap-1">
                            <Heart className="h-4 w-4" />
                            {(post.like_count !== null && post.like_count !== undefined) 
                              ? post.like_count.toLocaleString() 
                              : '0'}
                          </span>
                          <span className="flex items-center gap-1">
                            <MessageCircle className="h-4 w-4" />
                            {(post.comment_count !== null && post.comment_count !== undefined) 
                              ? post.comment_count.toLocaleString() 
                              : '0'}
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
                          {post.platform === 'instagram' && post.permalink && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedPostForEmbed(post);
                                setEmbedDialogOpen(true);
                              }}
                              className="h-8 px-2"
                            >
                              <Code2 className="h-4 w-4" />
                            </Button>
                          )}
                          {post.permalink && (
                            <a
                              href={post.permalink}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-primary hover:underline"
                              onClick={(e) => e.stopPropagation()}
                            >
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                );
              })}
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

      <EmbedDialog
        post={selectedPostForEmbed}
        open={embedDialogOpen}
        onOpenChange={setEmbedDialogOpen}
      />

      <Footer />
    </div>
  );
}
