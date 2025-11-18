import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Heart, MessageCircle, TrendingUp, ExternalLink, Code2 } from 'lucide-react';
import { formatNumber } from '@/lib/utils';
import type { ProjectPost } from '@/types/project';

interface ProjectPostsListProps {
  posts: ProjectPost[];
  creators: Array<{ handle: string }>;
  selectedPlatformFilter: string | 'all';
  onPostClick: (post: ProjectPost) => void;
  onEmbedClick: (post: ProjectPost) => void;
}

export function ProjectPostsList({
  posts,
  creators,
  selectedPlatformFilter,
  onPostClick,
  onEmbedClick,
}: ProjectPostsListProps) {
  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {posts.length > 0 ? (
          posts.map((post) => {
            const creator = creators.find(c => c.handle === post.author || c.handle === post.username);
            const isImage = post.media_url ? /\.(jpg|jpeg|png|gif|webp)$/i.test(post.media_url.split('?')[0]) : false;
            const embedUrl = post.permalink ? `${post.permalink.replace(/\/$/, '')}/embed` : undefined;
            return (
              <Card 
                key={post.id} 
                className="overflow-hidden hover:shadow-lg transition-shadow"
                onClick={() => onPostClick(post)}
              >
                <div className="aspect-square relative overflow-hidden bg-muted">
                  {post.platform === 'tiktok' ? (
                    post.media_url ? (
                      <img
                        src={post.media_url}
                        alt={post.caption || post.author || 'TikTok video'}
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
                      alt={post.caption || post.author}
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
                    <div className={`tiktok-placeholder w-full h-full bg-gradient-to-br from-pink-500 via-red-500 to-blue-500 flex flex-col items-center justify-center text-white ${post.media_url ? 'hidden' : ''}`}>
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
                  <Badge className="absolute top-2 right-2 bg-accent">
                    {post.platform?.toUpperCase() || 'INSTAGRAM'}
                  </Badge>
                </div>
                
                <CardContent className="p-4 space-y-3">
                  <div className="flex items-center gap-2">
                    <img
                      src={`https://unavatar.io/instagram/${post.username || post.author || 'instagram'}`}
                      alt={post.username || post.author || 'creator'}
                      className="w-8 h-8 rounded-full object-cover bg-muted"
                      onError={(event) => {
                        const username = post.username || post.author || 'IG';
                        (event.target as HTMLImageElement).src = `https://api.dicebear.com/7.x/initials/svg?seed=${username}`;
                      }}
                    />
                    <div className="flex-1 min-w-0">
                      {(post.username || post.author) ? (
                        <>
                          <p className="font-semibold text-sm truncate">{post.username || post.author}</p>
                          <p className="text-xs text-muted-foreground truncate">
                            @{post.username || post.author}
                          </p>
                        </>
                      ) : (
                        <p className="text-xs text-muted-foreground truncate">Unknown creator</p>
                      )}
                    </div>
                  </div>

                  <p className="text-sm line-clamp-2">{post.caption}</p>

                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    {post.like_count !== null && post.like_count !== undefined && (
                      <div className="flex items-center gap-1">
                        <Heart className="h-4 w-4" />
                        <span>{formatNumber(post.like_count)}</span>
                      </div>
                    )}
                    {post.comment_count !== null && post.comment_count !== undefined && (
                      <div className="flex items-center gap-1">
                        <MessageCircle className="h-4 w-4" />
                        <span>{formatNumber(post.comment_count)}</span>
                      </div>
                    )}
                    {post.score_trend !== undefined && (
                      <div className="flex items-center gap-1 text-success">
                        <TrendingUp className="h-4 w-4" />
                        <span>{post.score_trend}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-2 pt-2">
                    {post.platform === 'instagram' && post.permalink && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 px-2"
                        onClick={(e) => {
                          e.stopPropagation();
                          onEmbedClick(post);
                        }}
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
                </CardContent>
              </Card>
            );
          })
        ) : (
          <Card className="col-span-full">
            <CardContent className="p-10 text-center text-muted-foreground">
              {selectedPlatformFilter !== 'all' 
                ? `No ${selectedPlatformFilter === 'meta' ? 'Meta' : 'TikTok'} posts yet. Add ${selectedPlatformFilter === 'meta' ? 'Instagram/Facebook' : 'TikTok'} creators or hashtags to start tracking content.`
                : 'No posts yet. Add creators or hashtags to start tracking content.'}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

