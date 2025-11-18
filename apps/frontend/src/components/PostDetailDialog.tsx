import { useNavigate } from 'react-router-dom';
import {
  Dialog,
  DialogContent,
} from '@/components/ui/dialog';
import { Heart, MessageCircle, Eye } from 'lucide-react';
import { formatNumber, formatRelativeTime } from '@/lib/utils';
import type { ProjectPost } from '@/types/project';

interface PostDetailDialogProps {
  post: ProjectPost | null;
  projectId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function PostDetailDialog({ post, projectId, open, onOpenChange }: PostDetailDialogProps) {
  const navigate = useNavigate();

  if (!post) return null;

  // Extraire username depuis permalink si manquant
  let handle = post.username || post.author;
  if (!handle && post.permalink) {
    const permalinkMatch = post.permalink.match(/instagram\.com\/([^/]+)/);
    if (permalinkMatch && !['p', 'reel', 'tv', 'stories'].includes(permalinkMatch[1])) {
      handle = permalinkMatch[1];
    }
  }
  
  // Fallback seulement si vraiment rien trouvé
  if (!handle) {
    handle = 'instagram';
  }
  
  const handleSlug = handle.replace('@', '');
  const profilePic = `https://unavatar.io/instagram/${handle}`;
  const relativeTime = formatRelativeTime(post.posted_at, 'fr');
  const caption = post.caption || '';

  const formatCaption = () => {
    const parts: (string | JSX.Element)[] = [];
    let lastIndex = 0;
    const regex = /(#\w+|@\w+)/g;
    let match;
    
    while ((match = regex.exec(caption)) !== null) {
      if (match.index > lastIndex) {
        parts.push(caption.substring(lastIndex, match.index));
      }
      parts.push(
        <span
          key={match.index}
          className="text-primary hover:underline cursor-pointer"
        >
          {match[0]}
        </span>
      );
      lastIndex = regex.lastIndex;
    }
    
    if (lastIndex < caption.length) {
      parts.push(caption.substring(lastIndex));
    }
    
    return parts.length > 0 ? parts : <span>{caption}</span>;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[90vh] p-0 gap-0 overflow-hidden">
        <div className="flex bg-background">
          <div className="flex-shrink-0 w-full md:w-[60%] bg-black flex items-center justify-center">
            <img
              src={post.media_url}
              alt={post.caption}
              className="max-h-[90vh] w-full object-contain"
            />
          </div>

          <div className="flex flex-col w-full md:w-[40%] max-h-[90vh] border-l border-border">
            <div className="flex items-center justify-between p-4 border-b border-border">
              <div className="flex items-center gap-3">
                <img
                  src={profilePic}
                  alt={post.username}
                  className="w-10 h-10 rounded-full cursor-pointer hover:opacity-80 object-cover bg-muted"
                  onError={(event) => {
                    (event.target as HTMLImageElement).src = `https://api.dicebear.com/7.x/initials/svg?seed=${handle}`;
                  }}
                  onClick={() => {
                    onOpenChange(false);
                    navigate(`/projects/${projectId}/creator/${handleSlug}`);
                  }}
                />
                <div>
                  <div 
                    className="font-semibold text-sm cursor-pointer hover:opacity-80"
                    onClick={() => {
                      onOpenChange(false);
                      navigate(`/projects/${projectId}/creator/${handleSlug}`);
                    }}
                  >
                    {handle}
                  </div>
                  {post.location && (
                    <div className="text-xs text-muted-foreground">{post.location}</div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <div className="text-sm whitespace-pre-wrap">
                <span className="font-semibold mr-2">{handle}</span>
                {formatCaption()}
              </div>

              <div className="pt-4 border-t border-border space-y-2">
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-1">
                    <Heart className="h-4 w-4 text-red-500" />
                    <span className="font-semibold">{formatNumber(post.like_count) || '0'}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <MessageCircle className="h-4 w-4" />
                    <span className="font-semibold">{formatNumber(post.comment_count) || '0'}</span>
                  </div>
                  {post.view_count && (
                    <div className="flex items-center gap-1">
                      <Eye className="h-4 w-4" />
                      <span className="font-semibold">{formatNumber(post.view_count)}</span>
                    </div>
                  )}
                </div>
                <div className="text-xs text-muted-foreground">{relativeTime}</div>
              </div>

              <div className="pt-4 border-t border-border space-y-3">
                <h4 className="font-semibold text-sm mb-3">Comments</h4>
                <div className="text-sm text-muted-foreground text-center py-4">
                  Comments are not available through the Meta API. 
                  <br />
                  <span className="text-xs">View comments directly on {post.platform === 'instagram' ? 'Instagram' : post.platform}.</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

