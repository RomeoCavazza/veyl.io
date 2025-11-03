import { ExternalLink, Sparkles, Search, Share2, Video } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import metaLogo from '@/assets/img/meta-for-dev.png';
import tiktokLogo from '@/assets/img/tiktok-for-dev.png';
import meilisearchLogo from '@/assets/img/meilisearch.png';

export default function Docs() {
  const metaProducts = [
    {
      name: 'Instagram',
      description: 'Manage messages, comments, publish content, track insights, hashtags and mentions.'
    },
    {
      name: 'Page Public Content Access',
      description: 'Access Pages Search API and read public data to analyze posts and engagement.'
    },
    {
      name: 'Instagram Public Content Access',
      description: 'Access Hashtag Search endpoints to discover content and understand public sentiment.'
    },
    {
      name: 'Meta oEmbed Read',
      description: 'Get embed HTML and basic metadata for public Facebook and Instagram pages, posts, and videos.'
    },
    {
      name: 'Page Public Metadata Access',
      description: 'Read public metadata to analyze engagement with public Pages (likes, followers, analytics).'
    }
  ];

  const metaScopes = [
    {
      name: 'instagram_business_basic',
      product: 'Instagram',
      description: 'Read Instagram Business account profile info and media.'
    },
    {
      name: 'instagram_manage_insights',
      product: 'Instagram',
      description: 'Get insights for Instagram Business account metadata and media.'
    },
    {
      name: 'instagram_business_manage_insights',
      product: 'Instagram',
      description: 'Get insights for Instagram professional account metadata, posts, photos, and videos.'
    },
    {
      name: 'pages_show_list',
      product: 'Facebook Pages',
      description: 'Access list of Pages a person manages.'
    },
    {
      name: 'pages_read_user_content',
      product: 'Facebook Pages',
      description: 'Read user-generated content on the Page (posts, comments, ratings).'
    },
    {
      name: 'pages_read_engagement',
      product: 'Facebook Pages',
      description: 'Read content posted by the Page, followers data, and insights.'
    },
    {
      name: 'read_insights',
      product: 'Facebook Pages',
      description: 'Read Insights data for Pages, apps and web domains.'
    },
    {
      name: 'public_profile',
      product: 'Authentication',
      description: 'Read Default Public Profile Fields for authentication and personalization.'
    }
  ];

  const tiktokProduct = {
    name: 'Login Kit',
    description: 'Give users a quick and secure way to log in to your app or website.'
  };

  const tiktokScopes = [
    {
      name: 'user.info.basic',
      description: 'Read profile info (open id, avatar, display name).'
    },
    {
      name: 'user.info.profile',
      description: 'Read profile_web_link, profile_deep_link, bio_description, is_verified.'
    },
    {
      name: 'user.info.stats',
      description: 'Read statistical data (likes count, follower count, following count, video count).'
    },
    {
      name: 'video.list',
      description: 'Read user\'s public videos on TikTok.'
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
              Scopes and products used for Meta and TikTok integrations
            </p>
          </div>

          {/* Stack Technique */}
          <Card className="bg-gradient-to-br from-card to-card/50 border-primary/20">
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row gap-8 items-center">
                {/* Description et badges à gauche */}
                <div className="flex-1 space-y-4">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-6 w-6 text-primary" />
                    <h3 className="text-xl font-bold">Strategic Intelligence Platform</h3>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Born from strategic planning in influence agencies. Real-time social media intelligence and trend analysis.
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
                    <img src="/logo.svg" alt="veyl.io" className="h-16 w-auto max-w-none" />
                  </a>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Powered by Meilisearch */}
          <Card className="bg-gradient-to-br from-card to-card/50 border-primary/20">
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row gap-8 items-center">
                {/* Description à gauche */}
                <div className="flex-1 space-y-4">
                  <div className="flex items-center gap-2">
                    <Search className="h-6 w-6 text-primary" />
                    <h3 className="text-xl font-bold">Meilisearch</h3>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Indexing and searching millions of posts is powered by <strong>Meilisearch</strong>, 
                    an ultra-fast and typo-tolerant search engine enabling instant search with advanced facets and filters.
                  </p>
                  <a 
                    href="https://www.meilisearch.com/" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline flex items-center gap-1"
                  >
                    meilisearch.com
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>

                {/* Logo à droite */}
                <div className="flex-shrink-0">
                  <a href="https://www.meilisearch.com/" target="_blank" rel="noopener noreferrer" className="block transition-transform hover:scale-105">
                    <img src={meilisearchLogo} alt="Meilisearch" className="h-[300px] w-auto max-w-none" />
                  </a>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Meta for Developers */}
          <Card className="bg-gradient-to-br from-card to-card/50 border-primary/20">
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row gap-8 items-center mb-6">
                {/* Description à gauche */}
                <div className="flex-1 space-y-4">
                  <div className="flex items-center gap-2">
                    <Share2 className="h-6 w-6 text-primary" />
                    <h3 className="text-xl font-bold">Meta for Developers</h3>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Integration with <strong>Instagram Graph API</strong> and <strong>Facebook Pages API</strong> 
                    to access public content and engagement metrics.
                  </p>
                  <a 
                    href="https://developers.facebook.com/" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline flex items-center gap-1"
                  >
                    developers.facebook.com
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>

                {/* Logo à droite */}
                <div className="flex-shrink-0">
                  <a href="https://developers.facebook.com/" target="_blank" rel="noopener noreferrer" className="block transition-transform hover:scale-105">
                    <img src={metaLogo} alt="Meta for Developers" className="h-[280px] w-auto max-w-none" />
                  </a>
                </div>
              </div>

              {/* Products */}
              <div className="space-y-3 border-t border-border pt-6 mb-6">
                <h4 className="text-sm font-semibold text-foreground mb-3">Products</h4>
                {metaProducts.map((product, index) => (
                  <div key={index} className="border-l-2 border-primary/30 pl-3 py-1.5">
                    <div className="flex items-start gap-2 mb-1">
                      <span className="text-xs font-medium text-foreground">{product.name}</span>
                    </div>
                    <p className="text-xs text-muted-foreground">{product.description}</p>
                  </div>
                ))}
              </div>

              {/* Scopes */}
              <div className="space-y-3 border-t border-border pt-6">
                <h4 className="text-sm font-semibold text-foreground mb-3">Scopes</h4>
                {metaScopes.map((scope, index) => (
                  <div key={index} className="border-l-2 border-primary/30 pl-3 py-1.5">
                    <div className="flex items-start gap-2 mb-1">
                      <code className="text-xs bg-muted px-1.5 py-0.5 rounded font-mono">{scope.name}</code>
                      <Badge variant="outline" className="text-xs">{scope.product}</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">{scope.description}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* TikTok for Developers */}
          <Card className="bg-gradient-to-br from-card to-card/50 border-primary/20">
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row gap-8 items-center mb-6">
                {/* Description à gauche */}
                <div className="flex-1 space-y-4">
                  <div className="flex items-center gap-2">
                    <Video className="h-6 w-6 text-primary" />
                    <h3 className="text-xl font-bold">TikTok for Developers</h3>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {tiktokProduct.description}
                  </p>
                  <a 
                    href="https://developers.tiktok.com/" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-sm text-primary hover:underline flex items-center gap-1"
                  >
                    developers.tiktok.com
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>

                {/* Logo à droite */}
                <div className="flex-shrink-0">
                  <a href="https://developers.tiktok.com/" target="_blank" rel="noopener noreferrer" className="block transition-transform hover:scale-105">
                    <img src={tiktokLogo} alt="TikTok for Developers" className="h-[260px] w-auto max-w-none" />
                  </a>
                </div>
              </div>

              {/* Product */}
              <div className="space-y-3 border-t border-border pt-6 mb-6">
                <h4 className="text-sm font-semibold text-foreground mb-3">Product</h4>
                <div className="border-l-2 border-primary/30 pl-3 py-1.5">
                  <div className="flex items-start gap-2 mb-1">
                    <span className="text-xs font-medium text-foreground">{tiktokProduct.name}</span>
                  </div>
                  <p className="text-xs text-muted-foreground">{tiktokProduct.description}</p>
                </div>
              </div>

              {/* Scopes */}
              <div className="space-y-3 border-t border-border pt-6">
                <h4 className="text-sm font-semibold text-foreground mb-3">Scopes</h4>
                {tiktokScopes.map((scope, index) => (
                  <div key={index} className="border-l-2 border-primary/30 pl-3 py-1.5">
                    <div className="flex items-start gap-2 mb-1">
                      <code className="text-xs bg-muted px-1.5 py-0.5 rounded font-mono">{scope.name}</code>
                    </div>
                    <p className="text-xs text-muted-foreground">{scope.description}</p>
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
