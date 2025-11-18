// EmbedDialog.tsx - Dialog to display Instagram post embed using Meta oEmbed API
import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Copy, Check, ExternalLink } from 'lucide-react';
import { fetchMetaOEmbed } from '@/lib/api';
import type { ProjectPost } from '@/types/project';
import type { PostHit } from '@/lib/api';

// Type compatible pour les posts (ProjectPost ou PostHit)
type PostForEmbed = ProjectPost | PostHit;

interface EmbedDialogProps {
  post: PostForEmbed | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function EmbedDialog({ post, open, onOpenChange }: EmbedDialogProps) {
  const [oembedData, setOembedData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (open && post && post.permalink && post.platform === 'instagram') {
      fetchOEmbed();
    } else if (open && (!post || !post.permalink || post.platform !== 'instagram')) {
      setError('Embed is only available for Instagram posts with a permalink.');
    }
  }, [open, post]);

  const fetchOEmbed = async () => {
    if (!post?.permalink) return;

    setLoading(true);
    setError(null);
    setOembedData(null);

    try {
      const data = await fetchMetaOEmbed(post.permalink);
      setOembedData(data);
    } catch (err: unknown) {
      let errorMessage = 'Failed to fetch embed data';
      
      if (err instanceof Error) {
        errorMessage = err.message;
        // Si c'est une erreur HTTP, essayer d'extraire plus d'infos
        if (errorMessage.includes('HTTP_')) {
          const statusCode = errorMessage.replace('HTTP_', '');
          if (statusCode === '502') {
            errorMessage = 'Bad Gateway: The server could not reach Meta API. Please try again later or check if Meta API is available.';
          } else if (statusCode === '401') {
            errorMessage = 'Unauthorized: Please connect your Instagram/Facebook account via OAuth.';
          } else if (statusCode === '400') {
            errorMessage = 'Bad Request: Invalid Instagram URL or Meta API error.';
          } else if (statusCode === '403') {
            errorMessage = 'Forbidden: Meta API access denied. The oEmbed permission may not be approved yet.';
          }
        }
      }
      
      setError(errorMessage);
      
      if (import.meta.env.DEV) {
        console.error('oEmbed fetch error:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCopyHTML = async () => {
    if (!oembedData?.html) return;

    try {
      await navigator.clipboard.writeText(oembedData.html);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  if (!post) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Embed Instagram Post</DialogTitle>
          <DialogDescription>
            Embed this Instagram post using Meta oEmbed API. Copy the HTML code to use in your website or dashboard.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {loading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
              <span className="ml-2 text-sm text-muted-foreground">Fetching embed data...</span>
            </div>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {oembedData && (
            <>
              {/* Preview */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-sm">Preview</h3>
                  {post.permalink && (
                    <a
                      href={post.permalink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-primary hover:underline inline-flex items-center gap-1"
                    >
                      View on Instagram
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
                <div className="border rounded-lg p-4 bg-muted/50 flex items-center justify-center min-h-[400px]">
                  <div
                    className="w-full"
                    dangerouslySetInnerHTML={{ __html: oembedData.html }}
                  />
                </div>
              </div>

              {/* HTML Code */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-sm">Embed Code</h3>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCopyHTML}
                    className="gap-2"
                  >
                    {copied ? (
                      <>
                        <Check className="h-4 w-4" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4" />
                        Copy HTML
                      </>
                    )}
                  </Button>
                </div>
                <pre className="bg-muted p-4 rounded-lg overflow-auto text-xs max-h-60">
                  <code>{oembedData.html}</code>
                </pre>
              </div>

              {/* Metadata */}
              {oembedData.thumbnail_url && (
                <div className="space-y-2">
                  <h3 className="font-semibold text-sm">Thumbnail</h3>
                  <img
                    src={oembedData.thumbnail_url}
                    alt="Post thumbnail"
                    className="max-w-xs rounded-lg border"
                  />
                </div>
              )}
            </>
          )}

          {!loading && !error && !oembedData && post.platform !== 'instagram' && (
            <Alert>
              <AlertDescription>
                Embed is only available for Instagram posts. This post is from {post.platform}.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

