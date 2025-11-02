import { Link } from 'react-router-dom';
import { TrendingUp, Sparkles, Users2, FileBarChart, TrendingUpDown, FileText, Search as SearchIcon, Brain, Server, Zap, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { Card, CardContent } from '@/components/ui/card';

export default function Landing() {
  const features = [
    {
      icon: Sparkles,
      title: 'Recherche Avancée',
      description: 'Découvrez les tendances avec des filtres puissants grâce à Meilisearch.',
    },
    {
      icon: Users2,
      title: 'Intelligence Créateurs',
      description: 'Analysez les performances des influenceurs et leurs partenariats.',
    },
    {
      icon: FileBarChart,
      title: 'Génération de Rapports',
      description: 'Générez des rapports professionnels avec insights et visualisations.',
    },
    {
      icon: TrendingUpDown,
      title: 'Analytics Temps Réel',
      description: 'Suivez l\'engagement et les tendances de croissance en direct.',
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero Section */}
      <section className="container py-16 md:py-24">
        <div className="flex flex-col items-center text-center space-y-8 max-w-4xl mx-auto">
          {/* Badges partenariats */}
          <div className="flex flex-wrap justify-center gap-3 mb-4">
            <Badge variant="outline" className="px-4 py-2 text-sm border-primary/50">
              <span className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                Partenaire Meta for Developers
              </span>
            </Badge>
            <Badge variant="outline" className="px-4 py-2 text-sm border-primary/50">
              <span className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                Partenaire TikTok for Developers
              </span>
            </Badge>
          </div>

          <div className="space-y-6">
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
              Intelligence Sociale & Veille des Tendances
            </h1>
            
            <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              Plateforme de veille culturelle et d'analyse des tendances sur les réseaux sociaux. 
              Surveillez, analysez et anticipez les tendances émergentes sur Instagram et TikTok.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/projects/new">
              <Button size="lg" className="gradient-primary shadow-glow">
                <Sparkles className="mr-2 h-5 w-5" />
                Démarrer une démo
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

      {/* Section Meilisearch - Mise en avant */}
      <section className="container py-16 bg-muted/30 rounded-2xl my-8">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          <div className="flex items-center justify-center gap-3">
            <Brain className="h-8 w-8 text-primary" />
            <h2 className="text-2xl md:text-3xl font-bold">Powered by Meilisearch</h2>
          </div>
          <p className="text-muted-foreground text-lg leading-relaxed max-w-2xl mx-auto">
            veyl.io utilise <strong className="text-foreground">Meilisearch</strong>, un moteur de recherche 
            ultra-rapide et typo-tolerant, pour indexer et rechercher des millions de posts en temps réel.
          </p>
          <p className="text-sm text-muted-foreground">
            Recherche instantanée avec typo-tolerance, facettes, filtres avancés et résultats pertinents.
          </p>
          <div className="flex justify-center pt-4">
            <Button variant="outline" asChild>
              <a href="https://www.meilisearch.com" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2">
                <ExternalLink className="h-4 w-4" />
                En savoir plus sur Meilisearch
              </a>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="container py-16">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Fonctionnalités</h2>
          <div className="grid md:grid-cols-2 gap-8 mb-8">
            {features.map((feature, index) => (
              <Card key={index} className="hover:border-primary/50 transition-colors">
                <CardContent className="p-8 flex flex-col items-center text-center space-y-4">
                  <feature.icon className="h-12 w-12 text-primary" />
                  <h3 className="text-xl font-semibold">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Stack Technique */}
      <section className="container py-16">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center gap-3 mb-8">
            <Server className="h-8 w-8 text-primary" />
            <h2 className="text-3xl font-bold text-center">Stack Technique</h2>
          </div>
          
          <Card className="p-8">
            <div className="text-center mb-6">
              <p className="text-muted-foreground mb-4">
                Technologies modernes et performantes pour une plateforme robuste et scalable
              </p>
            </div>
            
            <div className="flex flex-wrap justify-center gap-3">
              <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python" />
              <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
              <img src="https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL" />
              <img src="https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white" alt="Redis" />
              <img src="https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black" alt="React" />
              <img src="https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white" alt="TypeScript" />
              <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" alt="Docker" />
              <a href="https://www.meilisearch.com" target="_blank" rel="noopener noreferrer" className="inline-block">
                <img src="https://img.shields.io/badge/MeiliSearch-FF006D?logo=meilisearch&logoColor=white" alt="Meilisearch" />
              </a>
            </div>
          </Card>
        </div>
      </section>

      {/* Section Partenariats API */}
      <section className="container py-16">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center gap-3 mb-8">
            <Zap className="h-8 w-8 text-primary" />
            <h2 className="text-3xl font-bold text-center">Intégrations Social Media</h2>
          </div>
          
          <div className="grid md:grid-cols-2 gap-6">
            <Card className="p-6 hover:border-primary/50 transition-colors">
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold">
                    M
                  </div>
                  <h3 className="text-xl font-bold">Meta for Developers</h3>
                </div>
                <p className="text-muted-foreground text-sm">
                  Intégration avec Instagram Graph API et Facebook Pages API pour accéder aux contenus publics 
                  et aux métriques d'engagement.
                </p>
                <Button variant="outline" size="sm" asChild>
                  <a href="https://developers.facebook.com/" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2">
                    <ExternalLink className="h-4 w-4" />
                    Documentation Meta
                  </a>
                </Button>
              </div>
            </Card>
            
            <Card className="p-6 hover:border-primary/50 transition-colors">
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-black to-gray-800 flex items-center justify-center text-white font-bold text-xs">
                    TT
                  </div>
                  <h3 className="text-xl font-bold">TikTok for Developers</h3>
                </div>
                <p className="text-muted-foreground text-sm">
                  Intégration avec TikTok Login Kit et TikTok API pour accéder aux vidéos publiques 
                  et aux statistiques des créateurs.
                </p>
                <Button variant="outline" size="sm" asChild>
                  <a href="https://developers.tiktok.com/" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2">
                    <ExternalLink className="h-4 w-4" />
                    Documentation TikTok
                  </a>
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="container py-16">
        <Card className="p-12 max-w-3xl mx-auto text-center bg-gradient-to-br from-card to-card/50 border-primary/20">
          <h2 className="text-3xl font-bold mb-4">Prêt à commencer ?</h2>
          <p className="text-muted-foreground mb-8">
            Créez votre premier projet de veille et découvrez les tendances qui façonnent les réseaux sociaux
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/projects/new">
              <Button size="lg" className="gradient-primary shadow-glow">
                <Sparkles className="mr-2 h-5 w-5" />
                Créer un projet
              </Button>
            </Link>
            <Link to="/community">
              <Button size="lg" variant="outline">
                <Users2 className="mr-2 h-5 w-5" />
                Rejoindre la communauté
              </Button>
            </Link>
          </div>
        </Card>
      </section>

      <Footer />
    </div>
  );
}
