import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { RefreshCcw, Users, Image, TrendingUp, Eye } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { getApiBase } from '@/lib/api';

interface InstagramInsightsProps {
  projectId: string;
}

export function InstagramInsights({ projectId }: InstagramInsightsProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [insights, setInsights] = useState<any>(null);
  const { toast } = useToast();

  const fetchInsights = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem('token');
      const apiBase = getApiBase();
      
      // Appel à l'endpoint Meta insights
      const response = await fetch(`${apiBase}/api/v1/meta/insights?platform=instagram&resource_id=me&metrics=followers_count,media_count,impressions,reach`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setInsights(data);
      
      toast({
        title: 'Insights loaded',
        description: 'Instagram insights fetched successfully.',
      });
    } catch (error: any) {
      console.error('[INSIGHTS] Error:', error);
      toast({
        title: 'Failed to load insights',
        description: error.message || 'Check that you have connected your Instagram account.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="bg-card border-border shadow-lg">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-white flex items-center gap-2">
              <Image className="h-5 w-5" />
              Instagram Insights
            </CardTitle>
            <CardDescription className="text-gray-400">
              Account metrics and performance data
            </CardDescription>
          </div>
          <Button
            onClick={fetchInsights}
            disabled={isLoading}
            variant="outline"
            size="sm"
            className="gap-2"
          >
            {isLoading ? (
              <>
                <RefreshCcw className="h-4 w-4 animate-spin" />
                Loading...
              </>
            ) : (
              <>
                <RefreshCcw className="h-4 w-4" />
                Fetch Insights
              </>
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {!insights ? (
          <div className="text-center py-8 text-muted-foreground">
            <p>Click "Fetch Insights" to load your Instagram account metrics.</p>
            <p className="text-xs mt-2">
              (Requires Instagram Business account connected via OAuth)
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* Followers */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Users className="h-4 w-4" />
                <span className="text-sm">Followers</span>
              </div>
              <p className="text-2xl font-bold">
                {insights.followers_count?.toLocaleString() || 'N/A'}
              </p>
            </div>

            {/* Media Count */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Image className="h-4 w-4" />
                <span className="text-sm">Posts</span>
              </div>
              <p className="text-2xl font-bold">
                {insights.media_count?.toLocaleString() || 'N/A'}
              </p>
            </div>

            {/* Impressions */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Eye className="h-4 w-4" />
                <span className="text-sm">Impressions</span>
              </div>
              <p className="text-2xl font-bold">
                {insights.impressions?.toLocaleString() || 'N/A'}
              </p>
            </div>

            {/* Reach */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-muted-foreground">
                <TrendingUp className="h-4 w-4" />
                <span className="text-sm">Reach</span>
              </div>
              <p className="text-2xl font-bold">
                {insights.reach?.toLocaleString() || 'N/A'}
              </p>
            </div>
          </div>
        )}

        {insights && (
          <div className="mt-4 pt-4 border-t border-border">
            <Badge variant="secondary" className="text-xs">
              Last updated: {new Date().toLocaleString()}
            </Badge>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

