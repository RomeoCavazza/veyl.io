import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, Calendar, Plus, RefreshCcw } from 'lucide-react';
import { format } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { useToast } from '@/hooks/use-toast';

import { getProjects as fetchProjectsApi } from '@/lib/api';

interface Project {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  status: 'active' | 'archived' | 'draft';
  creators?: Array<{ id: number; creator_username: string; platform_id?: number; platform?: string; added_at?: string }>;
  creatorsCount?: number;
  platforms?: string[];
  scope_query?: string;
}

export default function Projects() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchProjects();
    
    // Recharger quand on revient sur cette page
    const handleFocus = () => {
      fetchProjects();
    };
    
    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, []);

  const fetchProjects = async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      
      const data = await fetchProjectsApi();
      setProjects(data.map((p) => ({
        id: String(p.id),
        name: p.name,
        description: p.description,
        createdAt: p.created_at,
        updatedAt: p.updated_at,
        status: (p.status === 'active' || p.status === 'archived' || p.status === 'draft' ? p.status : 'draft') as 'active' | 'archived' | 'draft',
        creators: p.creators || [],
        creatorsCount: typeof p.creators_count === 'number' ? p.creators_count : undefined,
        platforms: p.platforms || [],
        scope_query: p.scope_query || '',
      })));
    } catch (error: unknown) {
      if (import.meta.env.DEV) {
        console.error('Error fetching projects:', error);
      }
      const errorMessage = error instanceof Error ? error.message : String(error);
      if (errorMessage.includes('401') || errorMessage.includes('403')) {
        navigate('/auth');
      }
    } finally {
      setLoading(false);
    }
  };

  // Refresh complet : recharge projets + met à jour stats via /posts endpoint
  const handleRefreshAll = async () => {
    setRefreshing(true);
    try {
      // 1. Recharger les projets
      await fetchProjects(true);

      // 2. Pour chaque projet, appeler /projects/{id}/posts pour mettre à jour les stats
      const { getProjectPosts } = await import('@/lib/api');
      const refreshPromises = projects.map(async (project) => {
        try {
          await getProjectPosts(project.id);
          console.log(`✅ Refreshed stats for project ${project.name}`);
        } catch (error) {
          console.error(`❌ Failed to refresh project ${project.name}:`, error);
        }
      });

      await Promise.all(refreshPromises);

      // 3. Recharger une dernière fois pour avoir les stats à jour
      await fetchProjects(true);

      toast({
        title: 'Projects refreshed',
        description: 'All project stats have been updated.',
      });
    } catch (error: any) {
      console.error('Refresh error:', error);
      toast({
        title: 'Refresh failed',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container py-8 px-4">
        <div className="mb-6 flex items-center justify-between">
          <CardTitle className="text-2xl">My Projects</CardTitle>
          {projects.length > 0 && (
            <Button onClick={() => navigate('/projects/new')}>
              <Plus className="h-4 w-4 mr-2" />
              New project
            </Button>
          )}
        </div>
        <div className="space-y-4">
            {loading ? (
              <div className="flex items-center justify-center py-16">
                <div className="text-muted-foreground">Loading...</div>
              </div>
            ) : projects.length === 0 ? (
              /* Empty State */
              <div className="flex flex-col items-center justify-center py-16 px-4">
                <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
                  <FileText className="h-8 w-8 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  No projects found
                </h3>
                <p className="text-sm text-muted-foreground text-center mb-6 max-w-md">
                  You haven't created any projects yet. Create your first project to get started!
                </p>
                <Button onClick={() => navigate('/projects/new')}>
                  <Plus className="h-4 w-4 mr-2" />
                  New project
                </Button>
              </div>
            ) : (
              /* Projects List - Pleine largeur */
              <div className="space-y-4">
                {projects.map((project) => {
                  // Obtenir tous les créateurs réels
                  const projectCreators = (project.creators || []);
                  const fallbackHandles = (project.scope_query || '')
                    .split(',')
                    .map((q: string) => q.trim())
                    .filter((entry: string) => entry.startsWith('@'))
                    .map((handle: string) => ({
                        id: 0,
                      creator_username: handle.replace('@', ''),
                        platform_id: 0,
                    }));
                  const allCreators = projectCreators.length > 0
                    ? projectCreators
                    : fallbackHandles;
                  
                  const totalCreatorsCount = project.creatorsCount ?? allCreators.length;
                  const displayedCreators = allCreators.slice(0, 3);
                  const recentPosts: Array<{ id: string; media_url?: string; caption?: string }> = [];
                  
                  return (
                    <Card 
                      key={project.id} 
                      className="hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => navigate(`/projects/${project.id}`)}
                    >
                      <div className="flex gap-4 p-4">
                        {/* Bloc gauche - Informations */}
                        <div className="flex-shrink-0 w-80 flex flex-col justify-between">
                          <div className="space-y-3">
                            {/* Header avec nom, date et status sur la même ligne */}
                            <div className="flex items-center gap-3 flex-wrap">
                              <CardTitle className="text-lg">{project.name}</CardTitle>
                              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                <Calendar className="h-3 w-3" />
                                <span>
                                  {format(new Date(project.updatedAt), 'MMM dd, yyyy', { locale: enUS })}
                                </span>
                              </div>
                              <Badge 
                                variant={
                                  project.status === 'active' ? 'default' : 
                                  project.status === 'archived' ? 'secondary' : 
                                  'outline'
                                }
                              >
                                {project.status === 'active' ? 'Active' : 
                                 project.status === 'archived' ? 'Archived' : 
                                 'Draft'}
                              </Badge>
                            </div>
                            
                            {/* Description */}
                            {project.description && (
                              <p className="text-sm text-muted-foreground line-clamp-2">
                                {project.description}
                              </p>
                            )}
                          </div>
                          
                          {/* Photos de profil des créateurs en cascade - 3 premiers seulement */}
                          {displayedCreators.length > 0 && (
                            <div className="flex items-center gap-2 mt-3">
                              <div className="flex -space-x-2">
                                {displayedCreators.map((creator, idx) => {
                                  const isHashtag = project.scope_query
                                    ?.split(',')
                                    .map((entry: string) => entry.trim())
                                    .filter(Boolean)
                                    .some((entry: string) =>
                                      entry.startsWith('#') &&
                                      entry.replace('#', '').toLowerCase() === creator.creator_username?.toLowerCase()
                                    );
                                  const label = creator.creator_username
                                    ? creator.creator_username.charAt(0).toUpperCase()
                                    : '?';
                                  return (
                                    <div
                                      key={creator.id || creator.creator_username || `fallback-${idx}`}
                                      className={`w-10 h-10 rounded-full border-2 border-background flex items-center justify-center text-sm font-medium uppercase ${
                                        isHashtag
                                          ? 'bg-secondary/50 text-secondary-foreground'
                                          : 'bg-muted text-muted-foreground'
                                      }`}
                                    style={{ zIndex: displayedCreators.length - idx }}
                                      title={creator.creator_username || label}
                                    >
                                      {label}
                                    </div>
                                  );
                                })}
                              </div>
                              <span className="text-xs text-muted-foreground">
                                {totalCreatorsCount} {totalCreatorsCount > 1 ? 'creators' : 'creator'}
                              </span>
                            </div>
                          )}
                        </div>
                        
                        {/* Bloc droit - Posts récents qui s'étalent jusqu'au bout */}
                        <div className="flex-1 flex gap-2 overflow-x-auto min-h-[80px]">
                          {recentPosts.map((post) => (
                            <div
                              key={post.id}
                              className="flex-shrink-0 h-20 w-20 rounded-lg overflow-hidden bg-muted"
                              onClick={(e) => {
                                e.stopPropagation();
                                navigate(`/projects/${project.id}`);
                              }}
                            >
                              <img
                                src={post.media_url}
                                alt={post.caption}
                                className="w-full h-full object-cover cursor-pointer hover:opacity-80 transition-opacity"
                              />
                            </div>
                          ))}
                        </div>
                      </div>
                    </Card>
                  );
                })}
              </div>
            )}
        </div>
      </div>
    </div>
  );
}

