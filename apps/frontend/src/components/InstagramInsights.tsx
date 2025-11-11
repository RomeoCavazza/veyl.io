import { useState, useEffect } from 'react';
import { Users, Image, TrendingUp, Eye } from 'lucide-react';

interface InstagramInsightsProps {
  projectId: string;
  triggerRefresh?: number; // Pour déclencher un refresh depuis le parent
}

export function InstagramInsights({ projectId, triggerRefresh }: InstagramInsightsProps) {
  const [insights, setInsights] = useState<any>(null);

  useEffect(() => {
    fetchInsights();
  }, [triggerRefresh]); // Recharge quand triggerRefresh change

  const fetchInsights = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/v1/meta/insights?platform=instagram&resource_id=me&metrics=followers_count,media_count,impressions,reach`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setInsights(data);
      }
    } catch (error) {
      console.error('[INSIGHTS] Error:', error);
    }
  };

  if (!insights) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {/* Followers */}
      <div className="space-y-2 p-4 rounded-lg bg-card border border-border">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Users className="h-4 w-4" />
          <span className="text-sm">Followers</span>
        </div>
        <p className="text-2xl font-bold">
          {insights.followers_count?.toLocaleString() || '0'}
        </p>
      </div>

      {/* Media Count */}
      <div className="space-y-2 p-4 rounded-lg bg-card border border-border">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Image className="h-4 w-4" />
          <span className="text-sm">Posts</span>
        </div>
        <p className="text-2xl font-bold">
          {insights.media_count?.toLocaleString() || '0'}
        </p>
      </div>

      {/* Impressions */}
      <div className="space-y-2 p-4 rounded-lg bg-card border border-border">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Eye className="h-4 w-4" />
          <span className="text-sm">Impressions</span>
        </div>
        <p className="text-2xl font-bold">
          {insights.impressions?.toLocaleString() || '0'}
        </p>
      </div>

      {/* Reach */}
      <div className="space-y-2 p-4 rounded-lg bg-card border border-border">
        <div className="flex items-center gap-2 text-muted-foreground">
          <TrendingUp className="h-4 w-4" />
          <span className="text-sm">Reach</span>
        </div>
        <p className="text-2xl font-bold">
          {insights.reach?.toLocaleString() || '0'}
        </p>
      </div>
    </div>
  );
}
