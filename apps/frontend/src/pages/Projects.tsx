import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, Calendar, Plus } from 'lucide-react';
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
                  // Obtenir les créateurs (plus de têtes - au moins 5-7)
                  const projectCreators = (project.creators || []);
                  // Si pas de créateurs mais scope_query, extraire plus
                  let creatorsList = projectCreators.length > 0 
                    ? projectCreators 
                    : (project.scope_query || '').split(',').map((q: string) => ({
                        id: 0,
                        creator_username: q.trim().replace('@', ''),
                        platform_id: 0,
                      })).filter((c: any) => c.creator_username);
                  
                  // Si toujours pas assez, générer des créateurs mock supplémentaires
                  if (creatorsList.length < 5) {
                    const additionalCreators = Array.from({ length: 7 - creatorsList.length }, (_, i) => ({
                      id: 1000 + i,
                      creator_username: `creator_${project.id}_${i}`,
                      platform_id: 0,
                    }));
                    creatorsList = [...creatorsList, ...additionalCreators].slice(0, 7);
                  }
                  
                  // Obtenir les posts récents (plus de posts pour s'étaler)
                  const recentPosts = getFakeProjectPosts(project.id).slice(0, 10);
                  
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
                                  {format(new Date(project.updatedAt), 'dd MMM yyyy', { locale: fr })}
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
                          
                          {/* Photos de profil des créateurs en cascade */}
                          {creatorsList.length > 0 && (
                            <div className="flex items-center gap-2 mt-3">
                              <div className="flex -space-x-2">
                                {creatorsList.map((creator, idx) => (
                                  <img
                                    key={creator.id || creator.creator_username}
                                    src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${creator.creator_username}`}
                                    alt={creator.creator_username}
                                    className="w-10 h-10 rounded-full border-2 border-background"
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

