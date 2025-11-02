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
import { Settings, Edit, Copy, Trash2 } from 'lucide-react';
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
          {/* Informations de la DB */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Créateurs</p>
              <p className="text-2xl font-bold text-primary">{project.creators_count || 0}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Posts</p>
              <p className="text-2xl font-bold text-primary">{project.posts_count || 0}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Signals</p>
              <p className="text-2xl font-bold text-primary">{project.signals_count || 0}</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Platforms</p>
              <div className="flex gap-1 flex-wrap">
                {(project.platforms || []).map((p: string) => (
                  <Badge key={p} variant="outline" className="text-xs">{p}</Badge>
                ))}
              </div>
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

