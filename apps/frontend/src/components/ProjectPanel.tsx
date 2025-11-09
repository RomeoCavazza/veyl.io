import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Settings, Edit, Copy, Trash2, TrendingUp, TrendingDown, Minus, Instagram, Video, Music } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { getApiBase } from '@/lib/api';

interface ProjectPanelProps {
  project: any;
  creators: any[];
  onEdit: () => void;
  onDelete: () => void;
}

export function ProjectPanel({ project, creators, onEdit, onDelete }: ProjectPanelProps) {
  const navigate = useNavigate();
  const { toast } = useToast();

  // Fonction pour obtenir l'icône de la plateforme
  const getPlatformIcon = (platform: string) => {
    const platformLower = platform.toLowerCase();
    if (platformLower.includes('instagram')) return Instagram;
    if (platformLower.includes('tiktok')) return Video;
    if (platformLower.includes('youtube')) return Video;
    return Video; // Par défaut
  };

  // TODO: Remplacer par vraies données historiques depuis la DB
  const getTrend = (current: number, metric: string, projectId: number) => {
    // Hash simple pour générer une variation stable basée sur metric + projectId
    const hash = (metric + projectId.toString()).split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const seed = (hash % 100) / 100; // 0 à 1
    
    // Générer une variation stable (-15% à +25%)
    const variation = (seed * 40 - 15) / 100;
    const previous = current > 0 ? Math.round(current / (1 + variation)) : 0;
    const change = current - previous;
    const percent = previous > 0 ? ((change / previous) * 100).toFixed(1) : '0.0';
    
    if (change > 0) {
      return { type: 'up', percent: `+${percent}%`, value: change, icon: TrendingUp, color: 'text-green-500' };
    } else if (change < 0) {
      return { type: 'down', percent: `${percent}%`, value: change, icon: TrendingDown, color: 'text-red-500' };
    } else {
      return { type: 'stable', percent: '0%', value: 0, icon: Minus, color: 'text-gray-500' };
    }
  };

  const handleDuplicate = async () => {
    try {
      const token = localStorage.getItem('token');
      const apiBase = getApiBase();
      const url = apiBase ? `${apiBase}/api/v1/projects` : `/api/v1/projects`;
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token || ''}`,
        },
        body: JSON.stringify({
          name: `${project.name} (copie)`,
          description: project.description,
          platforms: project.platforms || [],
          scope_type: project.scope_type,
          scope_query: project.scope_query,
          hashtag_names: project.hashtag_names || [],
          creator_usernames: project.creator_usernames || [],
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to duplicate project');
      }

      const duplicatedProject = await response.json();
      toast({
        title: 'Succès',
        description: 'Projet dupliqué avec succès',
      });
      navigate(`/projects/${duplicatedProject.id}`);
    } catch (error: any) {
      toast({
        title: 'Erreur',
        description: error.message || 'Erreur lors de la duplication',
        variant: 'destructive',
      });
    }
  };

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle>{project.name}</CardTitle>
            <CardDescription>
              {project.description || 'vide'}
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={project.status === 'active' ? 'default' : 'secondary'}>
              {project.status}
            </Badge>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon">
                  <Settings className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={onEdit}>
                  <Edit className="h-4 w-4 mr-2" />
                  Modifier le projet
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleDuplicate}>
                  <Copy className="h-4 w-4 mr-2" />
                  Dupliquer le projet
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  onClick={onDelete}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Supprimer le projet
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Platforms avec logos */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">Platforms</p>
            <div className="flex gap-2 flex-wrap">
              {(project.platforms || []).map((p: string) => {
                const Icon = getPlatformIcon(p);
                return (
                  <Badge 
                    key={p} 
                    variant="outline" 
                    className="flex items-center gap-2 px-3 py-1.5"
                  >
                    <Icon className="h-4 w-4" />
                    <span className="capitalize">{p}</span>
                  </Badge>
                );
              })}
            </div>
          </div>

          {/* Métriques avec tendances style crypto */}
          <div className="grid grid-cols-3 gap-4 pt-2">
            <div className="space-y-2 p-3 rounded-lg bg-muted/30 border border-border">
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Créateurs</p>
                {(() => {
                  const trend = getTrend(project.creators_count || 0, 'creators', project.id || 0);
                  const TrendIcon = trend.icon;
                  return (
                    <div className={`flex items-center gap-1 ${trend.color}`}>
                      <TrendIcon className="h-3 w-3" />
                      <span className="text-xs font-semibold">{trend.percent}</span>
                    </div>
                  );
                })()}
              </div>
              <p className="text-2xl font-bold text-primary">{project.creators_count || 0}</p>
            </div>
            <div className="space-y-2 p-3 rounded-lg bg-muted/30 border border-border">
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Posts</p>
                {(() => {
                  const trend = getTrend(project.posts_count || 0, 'posts', project.id || 0);
                  const TrendIcon = trend.icon;
                  return (
                    <div className={`flex items-center gap-1 ${trend.color}`}>
                      <TrendIcon className="h-3 w-3" />
                      <span className="text-xs font-semibold">{trend.percent}</span>
                    </div>
                  );
                })()}
              </div>
              <p className="text-2xl font-bold text-primary">{project.posts_count || 0}</p>
            </div>
            <div className="space-y-2 p-3 rounded-lg bg-muted/30 border border-border">
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Signals</p>
                {(() => {
                  const trend = getTrend(project.signals_count || 0, 'signals', project.id || 0);
                  const TrendIcon = trend.icon;
                  return (
                    <div className={`flex items-center gap-1 ${trend.color}`}>
                      <TrendIcon className="h-3 w-3" />
                      <span className="text-xs font-semibold">{trend.percent}</span>
                    </div>
                  );
                })()}
              </div>
              <p className="text-2xl font-bold text-primary">{project.signals_count || 0}</p>
            </div>
          </div>
          {/* Dates importantes */}
          {(project.last_run_at || project.last_signal_at) && (
            <div className="pt-4 border-t space-y-2">
              {project.last_run_at && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Dernière exécution:</span>
                  <span>{new Date(project.last_run_at).toLocaleDateString('fr-FR')}</span>
                </div>
              )}
              {project.last_signal_at && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Dernier signal:</span>
                  <span>{new Date(project.last_signal_at).toLocaleDateString('fr-FR')}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

