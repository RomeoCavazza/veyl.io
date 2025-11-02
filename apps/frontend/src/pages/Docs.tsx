import { ExternalLink, Brain } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import metaLogo from '@/assets/img/meta-for-dev.png';
import tiktokLogo from '@/assets/img/tiktok-for-dev.png';
import meilisearchLogo from '@/assets/img/meilisearch.png';

export default function Docs() {
  const metaScopes = [
    {
      name: 'instagram_business_basic',
      product: 'Instagram Graph API',
      description: 'Accès basique Instagram Business pour lecture profil et médias'
    },
    {
      name: 'instagram_manage_insights',
      product: 'Instagram Graph API',
      description: 'Gestion des insights Instagram Business pour accès aux métriques'
    },
    {
      name: 'instagram_business_manage_insights',
      product: 'Instagram Graph API',
      description: 'Gestion avancée insights pour comptes professionnels'
    },
    {
      name: 'pages_show_list',
      product: 'Facebook Pages API',
      description: 'Liste des pages gérées pour afficher pages Facebook connectées'
    },
    {
      name: 'pages_read_user_content',
      product: 'Facebook Pages API',
      description: 'Lecture contenu utilisateur : posts, commentaires, notes'
    },
    {
      name: 'pages_read_engagement',
      product: 'Facebook Pages API',
      description: 'Lecture métriques d\'engagement : likes, followers, métriques de pages'
    },
    {
      name: 'read_insights',
      product: 'Facebook Pages API',
      description: 'Lecture données Insights pour analytics pages, apps, domaines'
    },
    {
      name: 'Page Public Content Access',
      product: 'Facebook Pages API',
      description: 'Accès contenu public des pages pour analyser posts et engagement'
    },
    {
      name: 'Instagram Public Content Access',
      product: 'Instagram Graph API',
      description: 'Accès contenu public Instagram pour endpoints Hashtag Search API'
    }
  ];

  const tiktokScopes = [
    {
      name: 'user.info.basic',
      product: 'Login Kit',
      description: 'Informations utilisateur basiques : open_id, avatar, display_name'
    },
    {
      name: 'user.info.profile',
      product: 'Login Kit',
      description: 'Informations profil utilisateur : profile_web_link, bio_description, is_verified'
    },
    {
      name: 'user.info.stats',
      product: 'Login Kit',
      description: 'Statistiques utilisateur : likes, follower, following, video count'
    },
    {
      name: 'video.list',
      product: 'TikTok API',
      description: 'Liste vidéos publiques pour accès aux vidéos publiques TikTok'
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="container py-12 px-4 max-w-4xl">
        <div className="space-y-12">
          {/* Header */}
          <div className="text-center space-y-4">
            <h1 className="text-3xl md:text-4xl font-bold">Documentation</h1>
            <p className="text-muted-foreground">
              Scopes et produits utilisés pour les intégrations Meta et TikTok
            </p>
          </div>

          {/* Stack Technique */}
          <Card className="bg-gradient-to-br from-card to-card/50 border-primary/20">
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row gap-8 items-center">
                {/* Description et badges à gauche */}
                <div className="flex-1 space-y-4">
                  <div className="flex items-center gap-2">
                    <Brain className="h-6 w-6 text-primary" />
                    <h3 className="text-xl font-bold">Strategic Intelligence Platform</h3>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Born from strategic planning in influence agencies. Real-time social media intelligence and trend analysis.
                  </p>
                  <p className="text-xs text-muted-foreground flex items-center gap-2">
                    Powered by{' '}
                    <a 
                      href="https://www.meilisearch.com" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-primary hover:underline font-semibold flex items-center gap-1"
                    >
                      MeiliSearch
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python" className="h-5" />
                    <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI" className="h-5" />
                    <img src="https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL" className="h-5" />
                    <img src="https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white" alt="Redis" className="h-5" />
                    <img src="https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black" alt="React" className="h-5" />
                    <img src="https://img.shields.io/badge/TypeScript-3178C6?logo=typescript&logoColor=white" alt="TypeScript" className="h-5" />
                    <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" alt="Docker" className="h-5" />
                    <a href="https://www.meilisearch.com" target="_blank" rel="noopener noreferrer">
                      <img src="https://img.shields.io/badge/MeiliSearch-FF006D?logo=meilisearch&logoColor=white" alt="MeiliSearch" className="h-5" />
                    </a>
                    <img src="https://img.shields.io/badge/Vercel-000000?logo=vercel&logoColor=white" alt="Vercel" className="h-5" />
                    <img src="https://img.shields.io/badge/Railway-131415?logo=railway&logoColor=white" alt="Railway" className="h-5" />
                  </div>
                </div>

                {/* Logo à droite */}
                <div className="flex-shrink-0">
                  <a href="/" className="block transition-transform hover:scale-105">
                    <img src="/logo.svg" alt="veyl.io" className="h-20 w-auto" />
                  </a>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Powered by Meilisearch */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-4 mb-4">
                <a href="https://www.meilisearch.com/" target="_blank" rel="noopener noreferrer">
                  <img src={meilisearchLogo} alt="Meilisearch" className="h-12" />
                </a>
                <div className="flex-1">
                  <CardTitle className="text-xl">Powered by Meilisearch</CardTitle>
                  <a 
                    href="https://www.meilisearch.com/" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline flex items-center gap-1 mt-1"
                  >
                    meilisearch.com
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                L'indexation et la recherche de millions de posts sont alimentées par <strong>Meilisearch</strong>, 
                un moteur de recherche ultra-rapide et typo-tolerant permettant une recherche instantanée avec facettes et filtres avancés.
              </p>
            </CardContent>
          </Card>

          {/* Meta for Developers */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-4 mb-4">
                <a href="https://developers.facebook.com/" target="_blank" rel="noopener noreferrer">
                  <img src={metaLogo} alt="Meta for Developers" className="h-12" />
                </a>
                <div className="flex-1">
                  <CardTitle className="text-xl">Meta for Developers</CardTitle>
                  <a 
                    href="https://developers.facebook.com/" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline flex items-center gap-1 mt-1"
                  >
                    developers.facebook.com
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {metaScopes.map((scope, index) => (
                  <div key={index} className="border-l-2 border-primary/30 pl-4 py-2">
                    <div className="flex items-start gap-2 mb-1">
                      <code className="text-xs bg-muted px-2 py-1 rounded font-mono">{scope.name}</code>
                      <Badge variant="outline" className="text-xs">{scope.product}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{scope.description}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* TikTok for Developers */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-4 mb-4">
                <a href="https://developers.tiktok.com/" target="_blank" rel="noopener noreferrer">
                  <img src={tiktokLogo} alt="TikTok for Developers" className="h-12" />
                </a>
                <div className="flex-1">
                  <CardTitle className="text-xl">TikTok for Developers</CardTitle>
                  <a 
                    href="https://developers.tiktok.com/" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline flex items-center gap-1 mt-1"
                  >
                    developers.tiktok.com
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {tiktokScopes.map((scope, index) => (
                  <div key={index} className="border-l-2 border-primary/30 pl-4 py-2">
                    <div className="flex items-start gap-2 mb-1">
                      <code className="text-xs bg-muted px-2 py-1 rounded font-mono">{scope.name}</code>
                      <Badge variant="outline" className="text-xs">{scope.product}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{scope.description}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Footer />
    </div>
  );
}
