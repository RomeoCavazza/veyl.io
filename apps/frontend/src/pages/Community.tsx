import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Github, MessageCircle, Users, GraduationCap, ExternalLink, Code2, Heart } from 'lucide-react';
import '@/assets/css/github-window.css';
import '@/assets/css/discord-button.css';

export default function Community() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container py-12 px-4 max-w-6xl">
        {/* Section Contribution - En haut */}
        <section className="mb-20">
          <Card className="p-8 bg-gradient-to-br from-card to-card/50 border-primary/20">
            <div className="text-center space-y-4">
              <div className="flex justify-center">
                <Heart className="h-12 w-12 text-primary" />
              </div>
              <h2 className="text-2xl font-bold">Contribuer au projet</h2>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Que vous soyez développeur, designer, marketeur ou simplement passionné par l'intelligence sociale, 
                votre contribution est la bienvenue !
              </p>
              <div className="flex flex-wrap justify-center gap-4 pt-4">
                <Button asChild variant="default">
                  <a href="https://github.com/RomeoCavazza/veyl.io" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2">
                    <Github className="h-4 w-4" />
                    Contribuer sur GitHub
                  </a>
                </Button>
                <Button asChild variant="outline">
                  <a href="https://discord.gg/TKbNuuV4sX" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2">
                    <MessageCircle className="h-4 w-4" />
                    Rejoindre Discord
                  </a>
                </Button>
              </div>
            </div>
          </Card>
        </section>

        {/* Rang 1 : ISCOM Paris */}
        <section className="mb-20">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            {/* Illustration (50%) */}
            <div className="flex items-center justify-center">
              <div className="p-8 rounded-lg border border-border bg-card/50">
                <Badge variant="outline" className="px-6 py-3 text-base">
                  ISCOM PARIS
                </Badge>
              </div>
            </div>
            
            {/* Texte (50%) */}
            <div className="space-y-3">
              <h2 className="text-2xl font-bold">Projet né dans un contexte universitaire</h2>
              <p className="text-muted-foreground">
                Imaginé et inspiré dans l'école <strong>ISCOM Paris</strong>, pour les insights métiers et l'audit de la niche choisie.
              </p>
            </div>
          </div>
        </section>

        {/* Rang 2 : EPITECH Paris */}
        <section className="mb-20">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            {/* Texte (50%) */}
            <div className="space-y-3">
              <h2 className="text-2xl font-bold">Rendu possible par les enseignements techniques</h2>
              <p className="text-muted-foreground">
                Développement technique rendu possible grâce aux enseignements de <strong>EPITECH Paris</strong>.
              </p>
            </div>
            
            {/* Illustration (50%) */}
            <div className="flex items-center justify-center">
              <div className="p-8 rounded-lg border border-border bg-card/50">
                <Badge variant="outline" className="px-6 py-3 text-base">
                  EPITECH PARIS
                </Badge>
              </div>
            </div>
          </div>
        </section>

        {/* Rang 3 : Projet Open Source - GitHub */}
        <section className="mb-20">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            {/* Illustration (50%) - Fenêtre GitHub */}
            <div className="w-full flex justify-center">
              <a 
                href="https://github.com/RomeoCavazza/veyl.io" 
                target="_blank" 
                rel="noopener noreferrer"
                className="block"
              >
                <div className="card-container hover:scale-[1.02] transition-transform cursor-pointer">
                  <div className="card-border"></div>
                  <div className="card">
                    <div className="header">
                      <div className="top-header">
                        <div className="repo">
                          <svg className="gh-icon" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                          </svg>
                          <span className="repo-slash">/</span>
                          <span className="repo-name">RomeoCavazza</span>
                          <span className="repo-slash">/</span>
                          <span className="repo-name">veyl.io</span>
                        </div>
                        <div className="space"></div>
                      </div>
                      <div className="btm-header">
                        <div className="tab active">
                          <span>Files</span>
                        </div>
                        <div className="tab">
                          <span>Contributors</span>
                        </div>
                      </div>
                    </div>
                    <div className="content">
                      <div className="prs">
                        <div className="pr">
                          <input type="checkbox" checked readOnly />
                          <div className="checkbox"></div>
                          <svg className="pr-icon" viewBox="0 0 24 24">
                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                          </svg>
                          <div className="pr-text">
                            <div className="pr-title">Backend API Routes</div>
                            <div className="pr-desc">FastAPI endpoints + authentication</div>
                          </div>
                        </div>
                        <div className="pr">
                          <input type="checkbox" checked readOnly />
                          <div className="checkbox"></div>
                          <svg className="pr-icon" viewBox="0 0 24 24">
                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                          </svg>
                          <div className="pr-text">
                            <div className="pr-title">Frontend Components</div>
                            <div className="pr-desc">React + TypeScript SPA</div>
                          </div>
                        </div>
                        <div className="pr">
                          <input type="checkbox" checked readOnly />
                          <div className="checkbox"></div>
                          <svg className="pr-icon" viewBox="0 0 24 24">
                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                          </svg>
                          <div className="pr-text">
                            <div className="pr-title">Documentation</div>
                            <div className="pr-desc">API reference + guides</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </a>
            </div>
            
            {/* Texte (50%) */}
            <div className="space-y-3">
              <h2 className="text-2xl font-bold">Projet Open Source</h2>
              <p className="text-muted-foreground">
                veyl.io est entièrement <strong>open source</strong> et disponible sur GitHub. Contribuez via des Pull Requests.
              </p>
              <Button asChild variant="outline" size="sm">
                <a href="https://github.com/RomeoCavazza/veyl.io" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2">
                  <Github className="h-4 w-4" />
                  Voir le repository
                  <ExternalLink className="h-4 w-4" />
                </a>
              </Button>
            </div>
          </div>
        </section>

        {/* Rang 4 : Communauté Discord */}
        <section className="mb-20">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            {/* Texte (50%) */}
            <div className="space-y-3">
              <h2 className="text-2xl font-bold">Communauté en construction</h2>
              <p className="text-muted-foreground">
                Rejoignez notre serveur Discord pour échanger avec la communauté et contribuer au projet.
              </p>
              <Button asChild variant="outline" size="sm">
                <a href="https://discord.gg/TKbNuuV4sX" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2">
                  <MessageCircle className="h-4 w-4" />
                  Rejoindre Discord
                  <ExternalLink className="h-4 w-4" />
                </a>
              </Button>
            </div>
            
            {/* Illustration (50%) - Bouton Discord */}
            <div className="w-full flex justify-center">
              <a href="https://discord.gg/TKbNuuV4sX" target="_blank" rel="noopener noreferrer" className="discord-button">
                <div className="discord-button-bg"></div>
                <div className="discord-button-content">
                  <div className="discord-icon-wrapper">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512" className="discord-icon">
                      <path d="M524.531 69.836a1.5 1.5 0 0 0-.764-.7A485.065 485.065 0 0 0 404.081 32.03a1.816 1.816 0 0 0-1.923.91 337.461 337.461 0 0 0-14.9 30.6 447.848 447.848 0 0 0-134.426 0 309.541 309.541 0 0 0-15.135-30.6 1.89 1.89 0 0 0-1.924-.91 483.689 483.689 0 0 0-119.688 37.107 1.712 1.712 0 0 0-.788.676C39.068 183.651 18.186 294.69 28.43 404.354a2.016 2.016 0 0 0 .765 1.375 487.666 487.666 0 0 0 146.825 74.189 1.9 1.9 0 0 0 2.063-.676A348.2 348.2 0 0 0 208.12 430.4a1.86 1.86 0 0 0-1.019-2.588 321.173 321.173 0 0 1-45.868-21.853 1.885 1.885 0 0 1-.185-3.126 251.047 251.047 0 0 0 9.109-7.137 1.819 1.819 0 0 1 1.9-.256c96.229 43.917 200.41 43.917 295.5 0a1.812 1.812 0 0 1 1.924.233 234.533 234.533 0 0 0 9.132 7.16 1.884 1.884 0 0 1-.162 3.126 301.407 301.407 0 0 1-45.89 21.83 1.875 1.875 0 0 0-1 2.611 391.055 391.055 0 0 0 30.014 48.815 1.864 1.864 0 0 0 2.063.7A486.048 486.048 0 0 0 610.7 405.729a1.882 1.882 0 0 0 .765-1.352c12.264-126.783-20.532-236.912-86.934-334.541zM222.491 337.58c-28.972 0-52.844-26.587-52.844-59.239s23.409-59.241 52.844-59.241c29.665 0 53.306 26.82 52.843 59.239 0 32.654-23.41 59.241-52.843 59.241zm195.38 0c-28.971 0-52.843-26.587-52.843-59.239s23.409-59.241 52.843-59.241c29.667 0 53.307 26.820 52.844 59.239 0 32.654-23.177 59.241-52.844 59.241z"/>
                    </svg>
                  </div>
                  <div style={{ flex: 1, textAlign: 'left' }}>
                    <p style={{ color: '#818cf8', fontWeight: 'bold', fontSize: '18px', margin: 0 }}>Discord</p>
                    <p style={{ color: 'rgba(129, 140, 248, 0.6)', fontSize: '14px', margin: 0 }}>Rejoindre la communauté</p>
                  </div>
                  <div className="discord-arrow">
                    <svg viewBox="0 0 24 24" stroke="currentColor" fill="none" style={{ width: '20px', height: '20px', color: '#818cf8' }}>
                      <path d="M9 5l7 7-7 7" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round"/>
                    </svg>
                  </div>
                </div>
              </a>
            </div>
          </div>
        </section>
      </div>
      
      <Footer />
    </div>
  );
}
