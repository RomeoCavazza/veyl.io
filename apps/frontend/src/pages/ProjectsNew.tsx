import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { createProject } from '@/lib/api';

export default function ProjectsNew() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isCreating, setIsCreating] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const runCreation = async (options?: { cancelled?: () => boolean }) => {
    setIsCreating(true);
    setError(null);
    try {
      const project = await createProject({});
      if (options?.cancelled?.()) {
        return;
      }
      navigate(`/projects/${project.id}`, { replace: true });
    } catch (err: any) {
      if (options?.cancelled?.()) {
        return;
      }
      console.error('Error auto-creating project:', err);
      const message = err?.message || 'Unable to create a new project';
      toast({
        title: 'Creation failed',
        description: message,
        variant: 'destructive',
      });
      setError(message);
      setIsCreating(false);
    }
  };

  useEffect(() => {
    let cancelled = false;
    runCreation({ cancelled: () => cancelled });
    return () => {
      cancelled = true;
    };
  }, [navigate, toast]);

  const handleRetry = () => {
    runCreation();
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <div className="container max-w-lg py-16 flex flex-col items-center gap-6 text-center">
        {isCreating ? (
          <>
            <Loader2 className="h-10 w-10 animate-spin text-primary" />
            <div>
              <p className="text-xl font-semibold">Creating your project workspace…</p>
              <p className="text-muted-foreground mt-2">You will be redirected in a moment.</p>
            </div>
          </>
        ) : (
          <>
            <div>
              <p className="text-xl font-semibold">Creation failed</p>
              <p className="text-muted-foreground mt-2">{error}</p>
            </div>
            <div className="flex flex-col gap-2 w-full max-w-sm">
              <Button onClick={handleRetry}>Try again</Button>
              <Button variant="ghost" onClick={() => navigate('/projects')}>
                Back to Projects
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
