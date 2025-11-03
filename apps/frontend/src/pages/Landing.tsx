import { Link } from 'react-router-dom';
import { Database, Search, Zap, Workflow, Brain, Github, MessageCircle } from 'lucide-react';
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
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Plateforme de veille culturelle et d'analyse des tendances sur les réseaux sociaux.
          </p>
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
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Rejoignez notre communauté open source pour contribuer au projet et échanger avec les développeurs.
          </p>
          <div className="flex flex-wrap justify-center gap-4 pt-4">
            <Button variant="outline" size="lg" asChild>
              <a 
                href="https://github.com/RomeoCavazza/veyl.io" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-2"
              >
                <Github className="h-5 w-5" />
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
                <MessageCircle className="h-5 w-5" />
                Discord
              </a>
            </Button>
            <Link to="/community">
              <Button size="lg" variant="outline">
                En savoir plus
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container py-12">
        <div className="max-w-2xl mx-auto text-center space-y-6">
          <Link to="/projects/new">
            <Button size="lg" className="gradient-primary shadow-glow">
              Créer un projet
            </Button>
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
}
