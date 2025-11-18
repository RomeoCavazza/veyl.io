import { useState, useEffect } from 'react';
import { Users, Image, TrendingUp, Eye, AlertCircle, Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { getApiBase } from '@/lib/api';

interface InstagramInsightsProps {
  projectId: string;
  triggerRefresh?: number; // Pour déclencher un refresh depuis le parent
}

export function InstagramInsights({ projectId, triggerRefresh }: InstagramInsightsProps) {
  const [insights, setInsights] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchInsights();
  }, [triggerRefresh]); // Recharge quand triggerRefresh change

  const fetchInsights = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Authentication required. Please log in.');
        setLoading(false);
        return;
      }

      const apiBase = getApiBase();
      const url = apiBase 
        ? `${apiBase}/api/v1/meta/insights?resource_id=me&metrics=impressions,reach,profile_views,website_clicks`
        : `/api/v1/meta/insights?resource_id=me&metrics=impressions,reach,profile_views,website_clicks`;

      const response = await fetch(url, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        let errorData: any = null;
        try {
          errorData = await response.json();
        } catch {
          errorData = { detail: `HTTP ${response.status}` };
        }
        
        const errorMessage = errorData?.detail?.message || errorData?.detail || `Failed to fetch insights: ${response.status}`;
        setError(errorMessage);
        setInsights(null);
        setLoading(false);
        return;
      }

      const data = await response.json();
      
      // Le backend retourne: {resource_id, metrics: {...}, raw_data: [...]}
      // On utilise les metrics directement
      if (data.metrics) {
        setInsights(data.metrics);
      } else {
        // Fallback pour ancien format
        setInsights(data);
      }
      
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch insights';
      setError(errorMessage);
      console.error('[INSIGHTS] Error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-6 w-6 animate-spin text-primary mr-2" />
        <span className="text-sm text-muted-foreground">Loading Instagram insights...</span>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          {error.includes('Instagram Business Account not found') 
            ? 'Please connect your Instagram Business account via Facebook Page in Profile settings.'
            : error.includes('Authentication required')
            ? 'Please log in to view insights.'
            : error}
        </AlertDescription>
      </Alert>
    );
  }

  if (!insights) {
    return null;
  }

  // Extraire les valeurs des métriques
  const impressions = insights.impressions || 0;
  const reach = insights.reach || 0;
  const profileViews = insights.profile_views || 0;
  const websiteClicks = insights.website_clicks || 0;

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold mb-2">Instagram Business Insights</h3>
        <p className="text-sm text-muted-foreground">
          Performance metrics from your connected Instagram Business account
        </p>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Impressions */}
        <div className="space-y-2 p-4 rounded-lg bg-card border border-border">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Eye className="h-4 w-4" />
            <span className="text-sm">Impressions</span>
          </div>
          <p className="text-2xl font-bold">
            {impressions.toLocaleString()}
          </p>
        </div>

        {/* Reach */}
        <div className="space-y-2 p-4 rounded-lg bg-card border border-border">
          <div className="flex items-center gap-2 text-muted-foreground">
            <TrendingUp className="h-4 w-4" />
            <span className="text-sm">Reach</span>
          </div>
          <p className="text-2xl font-bold">
            {reach.toLocaleString()}
          </p>
        </div>

        {/* Profile Views */}
        <div className="space-y-2 p-4 rounded-lg bg-card border border-border">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Users className="h-4 w-4" />
            <span className="text-sm">Profile Views</span>
          </div>
          <p className="text-2xl font-bold">
            {profileViews.toLocaleString()}
          </p>
        </div>

        {/* Website Clicks */}
        <div className="space-y-2 p-4 rounded-lg bg-card border border-border">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Image className="h-4 w-4" />
            <span className="text-sm">Website Clicks</span>
          </div>
          <p className="text-2xl font-bold">
            {websiteClicks.toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );
}
