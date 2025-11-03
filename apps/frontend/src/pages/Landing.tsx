import { Link } from 'react-router-dom';
import { Database, Search, Zap, Workflow, Brain, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { Card, CardContent } from '@/components/ui/card';

export default function Landing() {
  const cadrans = [
    {
      icon: Database,
      title: 'Indexation de Posts',
      description: 'Indexation automatique de posts via API Meta for Developers et TikTok for Developers.',
      status: 'live',
    },
    {
      icon: Search,
      title: 'Recherche Sémantique',
      description: 'Recherche sémantique vs sémiotique via Meilisearch pour une exploration intelligente du contenu.',
      status: 'live',
    },
    {
      icon: Zap,
      title: 'Recherche Avancée',
      description: 'Meilisearch : search UX, filtres avancés et ranking rules personnalisées.',
      status: 'future',
    },
    {
      icon: Brain,
      title: 'Stockage & Ingestion',
      description: 'Supabase + pgvector (semantic storage, RAG, similarity search). Make / n8n (ingestion). Dust (agent reasoning si besoin).',
      status: 'future',
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="container py-16 md:py-24">
        <div className="flex flex-col items-center text-center space-y-6 max-w-3xl mx-auto">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
            veyl.io
          </h1>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/projects/new">
              <Button size="lg" className="gradient-primary shadow-glow">
                Créer un projet
              </Button>
            </Link>
            <Link to="/docs">
              <Button size="lg" variant="outline">
                <FileText className="mr-2 h-5 w-5" />
                Documentation
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Video Section */}
      <section className="container py-8 md:py-12">
        <div className="max-w-4xl mx-auto">
          <div className="aspect-video rounded-lg bg-muted/30 border border-border/50 overflow-hidden">
            {/* Placeholder pour vidéo - à remplacer par <video> ou <iframe> */}
            <div className="w-full h-full flex items-center justify-center">
              <p className="text-muted-foreground text-sm">Vidéo à venir</p>
            </div>
          </div>
        </div>
      </section>

      {/* 4 Cadrans - Présentation du Projet */}
      <section className="container py-12 md:py-16">
        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {cadrans.map((cadran, index) => (
            <Card key={index} className="hover:border-primary/50 transition-colors">
              <CardContent className="p-6 space-y-4">
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-lg ${
                    cadran.status === 'live' 
                      ? 'bg-primary/10 text-primary' 
                      : 'bg-muted text-muted-foreground'
                  }`}>
                    <cadran.icon className="h-5 w-5" />
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-semibold">{cadran.title}</h3>
                      {cadran.status === 'live' && (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-primary/20 text-primary">
                          Live
                        </span>
                      )}
                      {cadran.status === 'future' && (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-muted text-muted-foreground">
                          Future
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {cadran.description}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Communauté */}
      <section className="container py-12 md:py-16">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          <h2 className="text-2xl md:text-3xl font-bold">Communauté</h2>
          <div className="flex flex-wrap justify-center gap-4 pt-4">
            <Button variant="outline" size="lg" asChild>
              <a 
                href="https://github.com/RomeoCavazza/veyl.io" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-2"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.532 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
                GitHub
              </a>
            </Button>
            <Button variant="outline" size="lg" asChild>
              <a 
                href="https://discord.gg/TKbNuuV4sX" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-2"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 640 512" aria-hidden="true">
                  <path d="M524.531 69.836a1.5 1.5 0 0 0-.764-.7A485.065 485.065 0 0 0 404.081 32.03a1.816 1.816 0 0 0-1.923.91 337.461 337.461 0 0 0-14.9 30.6 447.848 447.848 0 0 0-134.426 0 309.541 309.541 0 0 0-15.135-30.6 1.89 1.89 0 0 0-1.924-.91 483.689 483.689 0 0 0-119.688 37.107 1.712 1.712 0 0 0-.788.676C39.068 183.651 18.186 294.69 28.43 404.354a2.016 2.016 0 0 0 .765 1.375 487.666 487.666 0 0 0 146.825 74.189 1.9 1.9 0 0 0 2.063-.676A348.2 348.2 0 0 0 208.12 430.4a1.86 1.86 0 0 0-1.019-2.588 321.173 321.173 0 0 1-45.868-21.853 1.885 1.885 0 0 1-.185-3.126 251.047 251.047 0 0 0 9.109-7.137 1.819 1.819 0 0 1 1.9-.256c96.229 43.917 200.41 43.917 295.5 0a1.812 1.812 0 0 1 1.924.233 234.533 234.533 0 0 0 9.132 7.16 1.884 1.884 0 0 1-.162 3.126 301.407 301.407 0 0 1-45.89 21.83 1.875 1.875 0 0 0-1 2.611 391.055 391.055 0 0 0 30.014 48.815 1.864 1.864 0 0 0 2.063.7A486.048 486.048 0 0 0 610.7 405.729a1.882 1.882 0 0 0 .765-1.352c12.264-126.783-20.532-236.912-86.934-334.541zM222.491 337.58c-28.972 0-52.844-26.587-52.844-59.239s23.409-59.241 52.844-59.241c29.665 0 53.306 26.82 52.843 59.239 0 32.654-23.41 59.241-52.843 59.241zm195.38 0c-28.971 0-52.843-26.587-52.843-59.239s23.409-59.241 52.843-59.241c29.667 0 53.307 26.820 52.844 59.239 0 32.654-23.177 59.241-52.844 59.241z"/>
                </svg>
                Discord
              </a>
            </Button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
