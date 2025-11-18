// OEmbedDemo.tsx - Public demo page for Meta App Review
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, ExternalLink, Code2 } from 'lucide-react';

export default function OEmbedDemo() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [oembedData, setOembedData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Example Instagram post URL for testing
  const exampleUrl = 'https://www.instagram.com/p/EXAMPLE/';

  const handleFetch = async () => {
    if (!url.trim()) {
      setError('Please enter an Instagram post URL');
      return;
    }

    setLoading(true);
    setError(null);
    setOembedData(null);

    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || '';
      const endpoint = apiBase 
        ? `${apiBase}/api/v1/meta/oembed/public?url=${encodeURIComponent(url)}`
        : `/api/v1/meta/oembed/public?url=${encodeURIComponent(url)}`;
      
      const response = await fetch(endpoint);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();
      setOembedData(data);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch oEmbed data';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Meta oEmbed Demo</h1>
          <p className="text-muted-foreground">
            This page demonstrates the Meta oEmbed API integration for App Review.
            Enter an Instagram post URL to see the oEmbed data.
          </p>
        </div>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Test oEmbed API</CardTitle>
            <CardDescription>
              Enter an Instagram post URL to fetch oEmbed data using Meta Graph API
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input
                type="url"
                placeholder={exampleUrl}
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleFetch()}
                className="flex-1"
              />
              <Button onClick={handleFetch} disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Fetching...
                  </>
                ) : (
                  <>
                    <Code2 className="mr-2 h-4 w-4" />
                    Fetch oEmbed
                  </>
                )}
              </Button>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {oembedData && (
              <div className="space-y-4">
                <Alert>
                  <AlertDescription>
                    ✅ Successfully fetched oEmbed data from Meta Graph API
                  </AlertDescription>
                </Alert>

                <div className="space-y-2">
                  <h3 className="font-semibold">oEmbed Response:</h3>
                  <pre className="bg-muted p-4 rounded-lg overflow-auto text-sm">
                    {JSON.stringify(oembedData, null, 2)}
                  </pre>
                </div>

                {oembedData.html && (
                  <div className="space-y-2">
                    <h3 className="font-semibold">Embedded Content Preview:</h3>
                    <div 
                      className="border rounded-lg p-4 bg-muted/50"
                      dangerouslySetInnerHTML={{ __html: oembedData.html }}
                    />
                  </div>
                )}

                {oembedData.thumbnail_url && (
                  <div className="space-y-2">
                    <h3 className="font-semibold">Thumbnail:</h3>
                    <img 
                      src={oembedData.thumbnail_url} 
                      alt="oEmbed thumbnail"
                      className="max-w-md rounded-lg border"
                    />
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Use Case Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2">1. App Feature:</h3>
              <p className="text-muted-foreground">
                Social media monitoring and analytics platform that allows users to embed Instagram posts 
                in their projects and dashboards for content analysis.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-2">2. How oEmbed Permission Enables This Feature:</h3>
              <p className="text-muted-foreground">
                The <code className="bg-muted px-1 rounded">Meta oEmbed Read</code> permission allows veyl.io 
                to fetch oEmbed data from Instagram posts, enabling rich previews with thumbnails, 
                captions, and embedded content directly in the user's dashboard.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-2">3. End-User Benefit:</h3>
              <p className="text-muted-foreground">
                Users can preview and analyze Instagram content directly within veyl.io without leaving 
                the platform, improving workflow efficiency and providing a seamless content monitoring experience.
              </p>
            </div>

            <div className="pt-4 border-t">
              <a 
                href="https://developers.facebook.com/docs/instagram-api/reference/ig-media/oembed"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline inline-flex items-center gap-1"
              >
                Meta oEmbed API Documentation
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

