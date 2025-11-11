import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
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
import { formatDistanceToNow } from 'date-fns';

interface ProjectPanelProps {
  project: any;
  onEdit: () => void;
  onDelete: () => void;
}

export function ProjectPanel({ project, onEdit, onDelete }: ProjectPanelProps) {
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
          name: `${project.name} copy`,
          description: project.description,
          platforms: project.platforms || [],
          scope_type: project.scope_type,
          scope_query: project.scope_query,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to duplicate project');
      }

      const duplicatedProject = await response.json();
      toast({
        title: 'Project duplicated',
        description: 'You can now customise the copy.',
      });
      navigate(`/projects/${duplicatedProject.id}`);
    } catch (error: any) {
      toast({
        title: 'Duplication failed',
        description: error.message || 'We were unable to duplicate the project.',
        variant: 'destructive',
      });
    }
  };

  const updatedLabel = project.updated_at
    ? formatDistanceToNow(new Date(project.updated_at), { addSuffix: true })
    : 'just now';

  const lastFetchLabel = project.last_run_at
    ? formatDistanceToNow(new Date(project.last_run_at), { addSuffix: true })
    : null;

  const scopeTokens = (project.scope_query || '')
    .split(',')
    .map((token: string) => token.trim())
    .filter(Boolean);

  return (
    <Card className="bg-card border-border">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle>{project.name}</CardTitle>
            <CardDescription>{project.description || 'No description yet.'}</CardDescription>
            <p className="text-xs text-muted-foreground mt-2">Updated {updatedLabel}</p>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <Settings className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={onEdit}>
                <Edit className="h-4 w-4 mr-2" />
                Edit project
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleDuplicate}>
                <Copy className="h-4 w-4 mr-2" />
                Duplicate
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={onDelete}
                className="text-destructive focus:text-destructive"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-lg border border-border bg-muted/20 p-4">
              <p className="text-xs uppercase tracking-wide text-muted-foreground mb-1">Creators tracked</p>
              <p className="text-2xl font-semibold">{project.creators_count ?? 0}</p>
            </div>
            <div className="rounded-lg border border-border bg-muted/20 p-4">
              <p className="text-xs uppercase tracking-wide text-muted-foreground mb-1">Posts stored</p>
              <p className="text-2xl font-semibold">{project.posts_count ?? 0}</p>
            </div>
          </div>

          {scopeTokens.length > 0 && (
            <div>
              <p className="text-xs uppercase tracking-wide text-muted-foreground mb-2">Scope</p>
              <div className="flex flex-wrap gap-2">
                {scopeTokens.map((token: string) => (
                  <span
                    key={token}
                    className="text-xs px-2 py-1 rounded-full bg-muted text-muted-foreground"
                  >
                    {token}
                  </span>
                ))}
              </div>
            </div>
          )}

          {lastFetchLabel && (
            <p className="text-xs text-muted-foreground">Last fetch {lastFetchLabel}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

