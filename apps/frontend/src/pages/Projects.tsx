import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, Calendar, Edit, Trash2, Plus } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { useToast } from '@/hooks/use-toast';
import { getFakeProjectPosts } from '@/lib/fakeData';

// Importer getApiBase depuis api.ts pour éviter la duplication
import { getApiBase } from '@/lib/api';

interface Project {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  status: 'active' | 'archived' | 'draft';
  creators?: Array<{ id: number; creator_username: string; platform_id: number }>;
  platforms?: string[];
  scope_query?: string;
}

export default function Projects() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProjects();
    
    // Recharger quand on revient sur cette page
    const handleFocus = () => {
      fetchProjects();
    };
    
    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, []);

  const fetchProjects = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/auth');
        return;
      }

      // Utiliser le proxy Vercel (chemin relatif SANS slash final)
      const response = await fetch('/api/v1/projects', {
        mode: 'cors',
        credentials: 'same-origin',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setProjects(data.map((p: any) => ({
          id: String(p.id),
          name: p.name,
          description: p.description,
          createdAt: p.created_at,
          updatedAt: p.updated_at,
          status: p.status || 'draft',
          creators: p.creators || [],
          platforms: p.platforms || [],
          scope_query: p.scope_query || '',
        })));
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container py-8 max-w-7xl">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>My Projects</CardTitle>
            {projects.length > 0 && (
              <Button onClick={() => navigate('/projects/new')}>
                <Plus className="h-4 w-4 mr-2" />
                New project
              </Button>
            )}
          </CardHeader>
          <CardContent className="p-6">
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
              /* Projects Grid */
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {projects.map((project) => {
                  // Obtenir les créateurs (max 5)
                  const projectCreators = (project.creators || []).slice(0, 5);
                  // Si pas de créateurs mais scope_query, extraire
                  const creatorsList = projectCreators.length > 0 
                    ? projectCreators 
                    : (project.scope_query || '').split(',').slice(0, 5).map((q: string) => ({
                        id: 0,
                        creator_username: q.trim().replace('@', ''),
                        platform_id: 0,
                      })).filter((c: any) => c.creator_username);
                  
                  // Obtenir les posts récents (max 4)
                  const recentPosts = getFakeProjectPosts(project.id).slice(0, 4);
                  
                  return (
                    <Card key={project.id} className="hover:shadow-md transition-shadow">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <CardTitle className="text-base mb-1">{project.name}</CardTitle>
                            {project.description && (
                              <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                                {project.description}
                              </p>
                            )}
                          </div>
                          <Badge 
                            variant={
                              project.status === 'active' ? 'default' : 
                              project.status === 'archived' ? 'secondary' : 
                              'outline'
                            }
                            className="ml-2"
                          >
                            {project.status === 'active' ? 'Active' : 
                             project.status === 'archived' ? 'Archived' : 
                             'Draft'}
                          </Badge>
                        </div>
                        
                        {/* Photos de profil des créateurs en cascade */}
                        {creatorsList.length > 0 && (
                          <div className="flex items-center gap-2 mb-3">
                            <div className="flex -space-x-2">
                              {creatorsList.map((creator, idx) => (
                                <img
                                  key={creator.id || creator.creator_username}
                                  src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${creator.creator_username}`}
                                  alt={creator.creator_username}
                                  className="w-8 h-8 rounded-full border-2 border-background"
                                  style={{ zIndex: creatorsList.length - idx }}
                                  title={creator.creator_username}
                                />
                              ))}
                            </div>
                            <span className="text-xs text-muted-foreground">
                              {creatorsList.length} {creatorsList.length > 1 ? 'créateurs' : 'créateur'}
                            </span>
                          </div>
                        )}
                        
                        {/* Posts récents en ligne horizontale */}
                        {recentPosts.length > 0 && (
                          <div className="flex gap-2 overflow-x-auto pb-2">
                            {recentPosts.map((post) => (
                              <div
                                key={post.id}
                                className="flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden bg-muted"
                                onClick={() => navigate(`/projects/${project.id}`)}
                              >
                                <img
                                  src={post.media_url}
                                  alt={post.caption}
                                  className="w-full h-full object-cover cursor-pointer hover:opacity-80 transition-opacity"
                                />
                              </div>
                            ))}
                          </div>
                        )}
                      </CardHeader>
                      <CardContent className="pt-0">
                        <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            <span>
                              {format(new Date(project.updatedAt), 'dd MMM yyyy', { locale: fr })}
                            </span>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="flex-1"
                            onClick={() => navigate(`/projects/${project.id}`)}
                          >
                            <Edit className="h-4 w-4 mr-2" />
                            View
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-destructive hover:text-destructive"
                            onClick={async () => {
                              if (confirm(`Voulez-vous supprimer le projet "${project.name}" ?`)) {
                                try {
                                  const token = localStorage.getItem('token');
                                  // Utiliser le proxy Vercel (chemin relatif)
                                  const response = await fetch(`/api/v1/projects/${project.id}`, {
                                    method: 'DELETE',
                                    mode: 'cors',
                                    credentials: 'same-origin',
                                    headers: {
                                      'Authorization': `Bearer ${token}`
                                    }
                                  });
                                  if (response.ok) {
                                    setProjects(projects.filter(p => p.id !== project.id));
                                    toast({
                                      title: 'Success',
                                      description: 'Projet supprimé',
                                    });
                                  } else {
                                    toast({
                                      title: 'Error',
                                      description: 'Erreur lors de la suppression',
                                      variant: 'destructive',
                                    });
                                  }
                                } catch (error) {
                                  console.error('Error deleting project:', error);
                                  toast({
                                    title: 'Error',
                                    description: 'Erreur lors de la suppression',
                                    variant: 'destructive',
                                  });
                                }
                              }
                            }}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

