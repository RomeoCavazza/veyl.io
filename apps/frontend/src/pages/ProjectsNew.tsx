import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Loader2, Hash, User, Plus } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { createProject } from '@/lib/api';

// Listes de suggestions pour autocomplétion
const SUGGESTED_HASHTAGS = [
  'fashion', 'style', 'ootd', 'fashionblogger', 'streetstyle', 'fashionista',
  'makeup', 'beauty', 'makeuptutorial', 'beautytips', 'makeupartist',
  'fitness', 'workout', 'gym', 'fitnessmotivation', 'healthylifestyle',
  'travel', 'wanderlust', 'travelgram', 'travelblogger', 'explore',
  'food', 'foodie', 'foodporn', 'instafood', 'delicious',
  'photography', 'photooftheday', 'instagood', 'picoftheday',
  'lifestyle', 'motivation', 'inspiration', 'happy',
];

const SUGGESTED_CREATORS = [
  'selenagomez', 'cristiano', 'kyliejenner', 'beyonce', 'kendalljenner',
  'fashionista_alice', 'style_blogger', 'fashion_designer', 'beauty_guru',
  'makeup_artist', 'beauty_tips', 'tech_trends', 'tech_reviewer',
  'fitness_coach', 'travel_explorer', 'food_lover', 'photographer_pro',
];

export default function ProjectsNew() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  // Form state
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [hashtags, setHashtags] = useState<string[]>([]);
  const [creators, setCreators] = useState<string[]>([]);

  // Input states
  const [hashtagInput, setHashtagInput] = useState('');
  const [creatorInput, setCreatorInput] = useState('');
  const [showHashtagSuggestions, setShowHashtagSuggestions] = useState(false);
  const [showCreatorSuggestions, setShowCreatorSuggestions] = useState(false);

  // Filtrer les suggestions pour hashtags
  const filteredHashtags = useMemo(() => {
    if (!hashtagInput.trim()) return [];
    const query = hashtagInput.trim().toLowerCase().replace(/^#/, '');
    return SUGGESTED_HASHTAGS
      .filter(tag => tag.toLowerCase().includes(query))
      .filter(tag => !hashtags.includes(tag))
      .slice(0, 5);
  }, [hashtagInput, hashtags]);

  // Filtrer les suggestions pour créateurs
  const filteredCreators = useMemo(() => {
    if (!creatorInput.trim()) return [];
    const query = creatorInput.trim().toLowerCase().replace(/^@/, '');
    return SUGGESTED_CREATORS
      .filter(creator => creator.toLowerCase().includes(query))
      .filter(creator => !creators.includes(creator))
      .slice(0, 5);
  }, [creatorInput, creators]);

  // Ajouter un hashtag
  const handleAddHashtag = (tagToAdd?: string) => {
    const tag = (tagToAdd || hashtagInput.trim()).replace(/^#/, '');
    if (!tag || hashtags.includes(tag)) return;
    setHashtags([...hashtags, tag]);
    setHashtagInput('');
    setShowHashtagSuggestions(false);
  };

  // Ajouter un créateur
  const handleAddCreator = (creatorToAdd?: string) => {
    const creator = (creatorToAdd || creatorInput.trim()).replace(/^@/, '');
    if (!creator || creators.includes(creator)) return;
    setCreators([...creators, creator]);
    setCreatorInput('');
    setShowCreatorSuggestions(false);
  };

  // Créer le projet
  const handleCreate = async () => {
    if (!name.trim()) {
      toast({
        title: 'Name required',
        description: 'Please enter a project name',
        variant: 'destructive',
      });
      return;
    }

    if (hashtags.length === 0 && creators.length === 0) {
      toast({
        title: 'Content required',
        description: 'Please add at least one hashtag or creator',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    try {
      const projectData = {
        name: name.trim(),
        description: description.trim() || undefined,
        platforms: ['instagram'], // Default Instagram
        scope_type: hashtags.length > 0 && creators.length > 0 
          ? 'both' 
          : hashtags.length > 0 
            ? 'hashtags' 
            : 'creators',
        scope_query: [
          ...hashtags.map(t => `#${t}`),
          ...creators.map(c => `@${c}`)
        ].join(', '),
        hashtag_names: hashtags,
        creator_usernames: creators,
      };

      const createdProject = await createProject(projectData);

      toast({
        title: 'Project created!',
        description: 'Your project is ready to use',
      });

      navigate(`/projects/${createdProject.id}`, { replace: true });
    } catch (error: any) {
      console.error('Error creating project:', error);
      toast({
        title: 'Error',
        description: error.message || 'Failed to create project',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container py-8 max-w-2xl">
        {/* Header */}
        <div className="mb-8 text-center">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/projects')}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Projects
          </Button>
          <h1 className="text-4xl font-bold tracking-tight">Create New Project</h1>
        </div>

        {/* Form */}
        <Card>
          <CardContent className="pt-6 space-y-6">
            {/* Project Name */}
            <div className="space-y-2">
              <Label htmlFor="name">Project Name *</Label>
              <Input
                id="name"
                placeholder="e.g., Fashion Trends 2025"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                placeholder="What is this project about? (optional)"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            {/* Hashtags */}
            <div className="space-y-2 relative">
              <Label htmlFor="hashtags">Hashtags</Label>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Input
                    id="hashtags"
                    placeholder="Add hashtags (e.g., fashion, style)"
                    value={hashtagInput}
                    onChange={(e) => {
                      setHashtagInput(e.target.value);
                      setShowHashtagSuggestions(true);
                    }}
                    onFocus={() => {
                      if (filteredHashtags.length > 0) {
                        setShowHashtagSuggestions(true);
                      }
                    }}
                    onBlur={() => {
                      // Délai pour permettre le clic sur les suggestions
                      setTimeout(() => setShowHashtagSuggestions(false), 200);
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        if (filteredHashtags.length > 0) {
                          handleAddHashtag(filteredHashtags[0]);
                        } else {
                          handleAddHashtag();
                        }
                      }
                    }}
                  />
                  {/* Suggestions */}
                  {showHashtagSuggestions && filteredHashtags.length > 0 && (
                    <div className="absolute z-10 w-full mt-1 bg-card border border-border rounded-md shadow-lg max-h-48 overflow-y-auto">
                      {filteredHashtags.map((tag) => (
                        <div
                          key={tag}
                          className="px-4 py-2 hover:bg-muted cursor-pointer flex items-center gap-2"
                          onClick={() => handleAddHashtag(tag)}
                        >
                          <Hash className="h-3 w-3 text-muted-foreground" />
                          <span className="text-sm">{tag}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => handleAddHashtag()}
                  disabled={!hashtagInput.trim()}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              {hashtags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {hashtags.map((tag) => (
                    <Badge
                      key={tag}
                      variant="secondary"
                      className="flex items-center gap-1"
                    >
                      <Hash className="h-3 w-3" />
                      {tag}
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            {/* Creators */}
            <div className="space-y-2 relative">
              <Label htmlFor="creators">Creators</Label>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Input
                    id="creators"
                    placeholder="Add creators (e.g., username1, username2)"
                    value={creatorInput}
                    onChange={(e) => {
                      setCreatorInput(e.target.value);
                      setShowCreatorSuggestions(true);
                    }}
                    onFocus={() => {
                      if (filteredCreators.length > 0) {
                        setShowCreatorSuggestions(true);
                      }
                    }}
                    onBlur={() => {
                      // Délai pour permettre le clic sur les suggestions
                      setTimeout(() => setShowCreatorSuggestions(false), 200);
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        if (filteredCreators.length > 0) {
                          handleAddCreator(filteredCreators[0]);
                        } else {
                          handleAddCreator();
                        }
                      }
                    }}
                  />
                  {/* Suggestions */}
                  {showCreatorSuggestions && filteredCreators.length > 0 && (
                    <div className="absolute z-10 w-full mt-1 bg-card border border-border rounded-md shadow-lg max-h-48 overflow-y-auto">
                      {filteredCreators.map((creator) => (
                        <div
                          key={creator}
                          className="px-4 py-2 hover:bg-muted cursor-pointer flex items-center gap-2"
                          onClick={() => handleAddCreator(creator)}
                        >
                          <User className="h-3 w-3 text-muted-foreground" />
                          <span className="text-sm">{creator}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => handleAddCreator()}
                  disabled={!creatorInput.trim()}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              {creators.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {creators.map((creator) => (
                    <Badge
                      key={creator}
                      variant="secondary"
                      className="flex items-center gap-1"
                    >
                      <User className="h-3 w-3" />
                      {creator}
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            {/* Create Button */}
            <Button
              onClick={handleCreate}
              disabled={loading || !name.trim() || (hashtags.length === 0 && creators.length === 0)}
              className="w-full"
              size="lg"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Project'
              )}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
