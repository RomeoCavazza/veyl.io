import { FileText, Code, Database, Layers, Users, Shield, Zap, BookOpen, ArrowRight, ExternalLink, Github, Brain, MessageCircle, GraduationCap, Search, Link2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { useNavigate } from 'react-router-dom';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function Docs() {
  const navigate = useNavigate();

  const sections = [
    {
      id: 'getting-started',
      icon: BookOpen,
      title: 'Démarrage Rapide',
      description: 'Installation et configuration en quelques minutes',
      link: 'https://github.com/RomeoCavazza/veyl.io#démarrage-rapide',
      topics: [
        'Installation backend (FastAPI)',
        'Installation frontend (React)',
        'Configuration variables d\'environnement',
        'Lancement local'
      ]
    },
    {
      id: 'architecture',
      icon: Layers,
      title: 'Architecture',
      description: 'Structure technique, stack et vision produit',
      topics: [
        'Stack technique (FastAPI, React, PostgreSQL, Redis)',
        'Architecture modulaire backend',
        'Structure frontend (components, pages, libs)',
        'Infrastructure (Railway, Vercel)',
        'Roadmap et phases de développement'
      ]
    },
    {
      id: 'api',
      icon: Code,
      title: 'API Reference',
      description: 'Endpoints REST, schémas et contrats techniques',
      topics: [
        'Authentification & OAuth (Instagram, TikTok, Google)',
        'Projects CRUD (GET, POST, PATCH, DELETE)',
        'Recherche posts (Meilisearch)',
        'Analytics endpoints',
        'Format des réponses et codes d\'erreur'
      ]
    },
    {
      id: 'database',
      icon: Database,
      title: 'Base de Données',
      description: 'Schéma PostgreSQL, tables et relations',
      topics: [
        'Tables core (users, posts, hashtags, platforms)',
        'Tables projects (projects, project_hashtags, project_creators)',
        'Relations et contraintes',
        'Views matérialisées',
        'Migrations Alembic'
      ]
    },
    {
      id: 'frontend',
      icon: FileText,
      title: 'Frontend',
      description: 'Pages, composants et routing React',
      topics: [
        'Structure des pages (Projects, Analytics, Search)',
        'Composants réutilisables (ProjectPanel, Navbar)',
        'Routing et navigation',
        'Intégration API',
        'State management (Contexts)'
      ]
    },
    {
      id: 'backend',
      icon: Layers,
      title: 'Backend',
      description: 'Modules FastAPI, services et endpoints',
      topics: [
        'Modules backend (auth, posts, projects, analytics)',
        'Services (Meilisearch, Redis, TikTok)',
        'Configuration et middleware',
        'Rate limiting et sécurité',
        'Gaps identifiés et plan d\'action'
      ]
    },
    {
      id: 'oauth',
      icon: Shield,
      title: 'OAuth & Permissions',
      description: 'Configuration OAuth Meta/Facebook et TikTok',
      topics: [
        'Meta/Facebook permissions (Instagram Business, Pages)',
        'TikTok Login Kit permissions',
        'OAuth flow et callbacks',
        'Gestion des tokens et refresh'
      ]
    },
    {
      id: 'meilisearch',
      icon: Search,
      title: 'Meilisearch',
      description: 'Moteur de recherche ultra-rapide et typo-tolerant',
      topics: [
        'Indexation des posts en temps réel',
        'Recherche typo-tolerant avec facettes',
        'Filtres avancés et tri',
        'Performance et scalabilité',
        'Configuration et intégration backend'
      ]
    },
    {
      id: 'partnerships',
      icon: Link2,
      title: 'Partenariats & Intégrations',
      description: 'Programmes Meta for Developers et TikTok for Developers',
      topics: [
        'Partenariat Meta for Developers (Instagram Graph API, Facebook Pages API)',
        'Partenariat TikTok for Developers (Login Kit, TikTok API)',
        'Produits et scopes demandés',
        'App Review et conformité',
        'Documentation officielle des plateformes'
      ]
    },
    {
      id: 'community',
      icon: MessageCircle,
      title: 'Communauté',
      description: 'GitHub open source, Discord et partenariats académiques',
      topics: [
        'Repository GitHub ouvert et collaboratif',
        'Serveur Discord pour la communauté',
        'Contribution et Pull Requests',
        'Partenariats ISCOM Paris et EPITECH Paris',
        'Programme beta testing pour agences'
      ]
    }
  ];

  const quickLinks = [
    {
      title: 'GitHub Repository',
      description: 'Code source complet',
      icon: Github,
      link: 'https://github.com/RomeoCavazza/veyl.io',
      external: true
    },
    {
      title: 'API Documentation',
      description: 'Swagger/OpenAPI docs',
      icon: Code,
      link: '/api/docs',
      external: false
    },
    {
      title: 'Try Search',
      description: 'Tester la recherche',
      icon: Zap,
      onClick: () => navigate('/search')
    },
    {
      title: 'My Projects',
      description: 'Gérer vos projets',
      icon: FileText,
      onClick: () => navigate('/projects')
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="container py-16">
        <div className="max-w-6xl mx-auto space-y-16">
          {/* Header */}
          <div className="text-center space-y-6">
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Documentation
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Documentation technique complète pour veyl.io - Plateforme de veille culturelle et d'analyse des tendances
            </p>
            
            {/* Badges partenariats */}
            <div className="flex flex-wrap justify-center gap-3 pt-4">
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
          </div>

          {/* Quick Links */}
          <section>
            <h2 className="text-2xl font-bold mb-6">Accès Rapide</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {quickLinks.map((link, index) => (
                <Card 
                  key={index} 
                  className="cursor-pointer hover:border-primary transition-all"
                  onClick={() => {
                    if (link.onClick) {
                      link.onClick();
                    } else if (link.link) {
                      if (link.external) {
                        window.open(link.link, '_blank');
                      } else {
                        navigate(link.link);
                      }
                    }
                  }}
                >
                  <CardContent className="p-6 text-center space-y-2">
                    <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                      <link.icon className="h-6 w-6 text-primary" />
                    </div>
                    <h3 className="font-semibold">{link.title}</h3>
                    <p className="text-sm text-muted-foreground">{link.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>

          {/* Partenariats & Intégrations */}
          <section>
            <Card className="bg-gradient-to-br from-card to-card/50 border-primary/20">
              <CardHeader>
                <div className="flex items-center gap-3 mb-4">
                  <Link2 className="h-8 w-8 text-primary" />
                  <CardTitle className="text-2xl">Partenariats & Intégrations Social Media</CardTitle>
                </div>
                <CardDescription className="text-base">
                  veyl.io est partenaire officiel des programmes Meta for Developers et TikTok for Developers
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold">
                        M
                      </div>
                      <h3 className="text-xl font-bold">Meta for Developers</h3>
                    </div>
                    <p className="text-muted-foreground text-sm">
                      Intégration avec <strong>Instagram Graph API</strong> et <strong>Facebook Pages API</strong> 
                      pour accéder aux contenus publics et aux métriques d'engagement.
                    </p>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li className="flex items-start gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                        <span>Permissions: <code className="text-xs bg-muted px-1 rounded">instagram_business_basic</code>, <code className="text-xs bg-muted px-1 rounded">pages_read_engagement</code></span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                        <span>Produits: Instagram Graph API, Facebook Pages API</span>
                      </li>
                    </ul>
                    <Button variant="outline" size="sm" asChild>
                      <a href="https://developers.facebook.com/" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2">
                        Documentation Meta
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </Button>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-black to-gray-800 flex items-center justify-center text-white font-bold text-xs">
                        TT
                      </div>
                      <h3 className="text-xl font-bold">TikTok for Developers</h3>
                    </div>
                    <p className="text-muted-foreground text-sm">
                      Intégration avec <strong>TikTok Login Kit</strong> et <strong>TikTok API</strong> 
                      pour accéder aux vidéos publiques et aux statistiques des créateurs.
                    </p>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li className="flex items-start gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                        <span>Permissions: <code className="text-xs bg-muted px-1 rounded">user.info.basic</code>, <code className="text-xs bg-muted px-1 rounded">video.list</code></span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                        <span>Produits: TikTok Login Kit, TikTok API</span>
                      </li>
                    </ul>
                    <Button variant="outline" size="sm" asChild>
                      <a href="https://developers.tiktok.com/" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2">
                        Documentation TikTok
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Meilisearch Highlight */}
          <section>
            <Card className="bg-gradient-to-br from-card to-card/50 border-primary/20">
              <CardHeader>
                <div className="flex items-center gap-3 mb-4">
                  <Brain className="h-8 w-8 text-primary" />
                  <CardTitle className="text-2xl">Powered by Meilisearch</CardTitle>
                </div>
                <CardDescription className="text-base">
                  Moteur de recherche ultra-rapide et typo-tolerant pour indexer et rechercher des millions de posts
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-muted-foreground">
                    <strong className="text-foreground">Meilisearch</strong> est au cœur de la fonctionnalité de recherche de veyl.io. 
                    Il permet une recherche instantanée avec typo-tolerance, facettes, filtres avancés et résultats pertinents.
                  </p>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li className="flex items-start gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                      <span>Recherche typo-tolerant : trouvez les résultats même avec des fautes de frappe</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                      <span>Facettes et filtres : affinez vos recherches par plateforme, date, hashtags</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                      <span>Performance : recherche en millisecondes sur des millions de documents</span>
                    </li>
                  </ul>
                  <Button variant="outline" size="sm" asChild>
                    <a href="https://www.meilisearch.com" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2">
                      En savoir plus sur Meilisearch
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Communauté */}
          <section>
            <Card className="bg-gradient-to-br from-card to-card/50 border-primary/20">
              <CardHeader>
                <div className="flex items-center gap-3 mb-4">
                  <MessageCircle className="h-8 w-8 text-primary" />
                  <CardTitle className="text-2xl">Communauté Open Source</CardTitle>
                </div>
                <CardDescription className="text-base">
                  Rejoignez notre communauté GitHub et Discord pour contribuer et échanger
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <Github className="h-6 w-6 text-primary" />
                      <h3 className="text-lg font-bold">GitHub Repository</h3>
                    </div>
                    <p className="text-muted-foreground text-sm">
                      Le code source de veyl.io est entièrement <strong>open source</strong> et disponible sur GitHub. 
                      Contribuez au projet via des Pull Requests !
                    </p>
                    <Button variant="outline" size="sm" asChild>
                      <a href="https://github.com/RomeoCavazza/veyl.io" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2">
                        <Github className="h-4 w-4" />
                        Voir le repository
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </Button>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <MessageCircle className="h-6 w-6 text-primary" />
                      <h3 className="text-lg font-bold">Discord Community</h3>
                    </div>
                    <p className="text-muted-foreground text-sm">
                      Rejoignez notre serveur Discord pour échanger avec la communauté, poser des questions 
                      et partager vos découvertes.
                    </p>
                    <Button variant="outline" size="sm" asChild>
                      <a href="https://discord.gg/TKbNuuV4sX" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2">
                        <MessageCircle className="h-4 w-4" />
                        Rejoindre Discord
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </Button>
                  </div>
                </div>
                
                <div className="mt-6 pt-6 border-t border-border">
                  <div className="flex items-center gap-3 mb-4">
                    <GraduationCap className="h-6 w-6 text-primary" />
                    <h3 className="text-lg font-bold">Partenariats Académiques</h3>
                  </div>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <Badge variant="outline" className="mb-2">ISCOM PARIS</Badge>
                      <p className="text-sm text-muted-foreground">
                        Collaboration avec les étudiants pour le développement et l'analyse des tendances marketing.
                      </p>
                    </div>
                    <div>
                      <Badge variant="outline" className="mb-2">EPITECH PARIS</Badge>
                      <p className="text-sm text-muted-foreground">
                        Partenariat pour le développement technique, l'architecture backend et les intégrations API.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Documentation Sections */}
          <section>
            <h2 className="text-2xl font-bold mb-6">Documentation Technique</h2>
            <div className="grid md:grid-cols-2 gap-6">
              {sections.map((section, index) => (
                <Card key={index} className="bg-card border-border hover:border-primary/50 transition-all">
                  <CardHeader>
                    <div className="flex items-start justify-between mb-4">
                      <div className="h-12 w-12 rounded-lg bg-primary/20 flex items-center justify-center">
                        <section.icon className="h-6 w-6 text-primary" />
                      </div>
                      <Badge variant="outline">Documentation</Badge>
                    </div>
                    <CardTitle className="text-xl">{section.title}</CardTitle>
                    <CardDescription className="text-base">
                      {section.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <ul className="space-y-2">
                      {section.topics.map((topic, i) => (
                        <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                          <span className="h-1.5 w-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                          <span>{topic}</span>
                        </li>
                      ))}
                    </ul>
                    {section.link && (
                      <Button 
                        variant="outline" 
                        className="w-full"
                        onClick={() => window.open(section.link, '_blank')}
                      >
                        Voir la documentation
                        <ExternalLink className="h-4 w-4 ml-2" />
                      </Button>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>

          {/* API Status */}
          <section>
            <Card className="bg-card border-border">
              <CardHeader>
                <CardTitle className="text-2xl">État des Services</CardTitle>
                <CardDescription>
                  Statut des services backend et intégrations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-green-500" />
                      <span className="font-semibold">API Backend</span>
                    </div>
                    <p className="text-sm text-muted-foreground">FastAPI opérationnel</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-green-500" />
                      <span className="font-semibold">PostgreSQL</span>
                    </div>
                    <p className="text-sm text-muted-foreground">Base de données active</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-green-500" />
                      <span className="font-semibold">Meilisearch</span>
                    </div>
                    <p className="text-sm text-muted-foreground">Recherche full-text active</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-yellow-500" />
                      <span className="font-semibold">Redis</span>
                    </div>
                    <p className="text-sm text-muted-foreground">Cache (optionnel)</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-yellow-500" />
                      <span className="font-semibold">Qdrant</span>
                    </div>
                    <p className="text-sm text-muted-foreground">Recherche vectorielle (Phase 2)</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-yellow-500" />
                      <span className="font-semibold">Celery</span>
                    </div>
                    <p className="text-sm text-muted-foreground">Workers (Phase 3)</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Support */}
          <Card className="gradient-primary border-0 shadow-glow">
            <CardContent className="p-8 text-center space-y-4">
              <h2 className="text-2xl font-bold text-white">Besoin d'Aide ?</h2>
              <p className="text-white/80">
                Consultez la documentation GitHub ou contactez l'équipe de développement
              </p>
              <div className="flex gap-4 justify-center">
                <Button 
                  variant="secondary" 
                  className="bg-white text-primary hover:bg-white/90"
                  onClick={() => window.open('https://github.com/RomeoCavazza/veyl.io', '_blank')}
                >
                  <Github className="h-4 w-4 mr-2" />
                  GitHub Repository
                </Button>
                <Button 
                  variant="outline" 
                  className="border-white/20 text-white hover:bg-white/10"
                  onClick={() => navigate('/projects')}
                >
                  Essayer la plateforme
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Footer />
    </div>
  );
}
