import { Link } from 'react-router-dom';
import { Building, Users, Shield, Zap, Mail, Phone, MessageCircle, CheckCircle2, ArrowRight, Target } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';

export default function Enterprise() {
  const features = [
    {
      icon: Building,
      title: 'Solutions Sur Mesure',
      description: 'Fonctionnalités et intégrations personnalisées pour votre organisation',
    },
    {
      icon: Users,
      title: 'Collaboration d\'Équipe',
      description: 'Outils avancés pour que les équipes travaillent ensemble de manière transparente',
    },
    {
      icon: Shield,
      title: 'Sécurité Entreprise',
      description: 'Conformité SOC 2, SSO, et fonctionnalités de sécurité avancées',
    },
    {
      icon: Zap,
      title: 'Support Prioritaire',
      description: 'Responsable de compte dédié et support prioritaire 24/7',
    },
  ];

  const benefits = [
    'Accès prioritaire aux nouvelles fonctionnalités',
    'Intégrations API personnalisées',
    'Formation dédiée pour vos équipes',
    'Dashboard analytics avancé',
    'Export de données en masse',
    'Support SLA garanti',
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <section className="container py-16 md:py-24">
        {/* Header */}
        <div className="max-w-4xl mx-auto text-center mb-16 space-y-6">
          <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Solutions Entreprise
          </h1>
          <p className="text-xl text-muted-foreground">
            Scalez votre intelligence sociale avec des solutions personnalisées conçues pour les grandes organisations et agences
          </p>
          <div className="flex flex-wrap justify-center gap-3 pt-4">
            <Badge variant="outline" className="px-4 py-2">
              Pour les agences
            </Badge>
            <Badge variant="outline" className="px-4 py-2">
              Pour les grandes entreprises
            </Badge>
            <Badge variant="outline" className="px-4 py-2">
              Beta testing ouvert
            </Badge>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto mb-16">
          {features.map((feature) => (
            <Card key={feature.title} className="hover:border-primary/50 transition-colors">
              <CardContent className="p-8">
                <feature.icon className="h-12 w-12 text-primary mb-4" />
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Benefits */}
        <Card className="p-12 max-w-4xl mx-auto mb-16 bg-gradient-to-br from-card to-card/50">
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
                <Target className="h-6 w-6 text-primary" />
                Avantages Entreprise
              </h2>
              <ul className="space-y-3">
                {benefits.map((benefit, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <CheckCircle2 className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-muted-foreground">{benefit}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
                <Users className="h-6 w-6 text-primary" />
                Recherche Beta Testeurs
              </h2>
              <p className="text-muted-foreground mb-4">
                Nous recherchons activement des <strong>agences d'influence</strong> et des 
                <strong> entreprises</strong> pour tester nos solutions en beta et nous aider à 
                façonner le produit selon vos besoins réels.
              </p>
              <p className="text-sm text-muted-foreground mb-6">
                En tant que beta testeur, vous bénéficiez d'un accès prioritaire, d'un support dédié 
                et d'une influence directe sur le développement des fonctionnalités.
              </p>
              <Button asChild variant="default" className="w-full sm:w-auto">
                <Link to="#contact" className="flex items-center gap-2">
                  <MessageCircle className="h-4 w-4" />
                  Rejoindre le programme Beta
                </Link>
              </Button>
            </div>
          </div>
        </Card>

        {/* Contact Section */}
        <Card id="contact" className="p-12 max-w-3xl mx-auto mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-4">Contactez-nous</h2>
            <p className="text-muted-foreground">
              Discutons de la manière dont veyl.io peut aider votre organisation à atteindre ses objectifs
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <Card className="p-6 hover:border-primary/50 transition-colors">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <Mail className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-bold mb-2">Email</h3>
                  <a 
                    href="mailto:contact@veyl.io" 
                    className="text-muted-foreground hover:text-primary transition-colors text-sm break-all"
                  >
                    contact@veyl.io
                  </a>
                </div>
              </div>
            </Card>

            <Card className="p-6 hover:border-primary/50 transition-colors">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <MessageCircle className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-bold mb-2">Discord</h3>
                  <a 
                    href="https://discord.gg/TKbNuuV4sX" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-muted-foreground hover:text-primary transition-colors text-sm flex items-center gap-2"
                  >
                    Rejoindre le serveur
                    <ArrowRight className="h-4 w-4" />
                  </a>
                </div>
              </div>
            </Card>
          </div>

          {/* Contact Form */}
          <form className="space-y-6">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium mb-2">
                  Nom complet
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  className="w-full px-4 py-2 rounded-lg bg-background border border-input focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="Votre nom"
                  required
                />
              </div>
              <div>
                <label htmlFor="email" className="block text-sm font-medium mb-2">
                  Email professionnel
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  className="w-full px-4 py-2 rounded-lg bg-background border border-input focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="votre@entreprise.com"
                  required
                />
              </div>
            </div>
            <div>
              <label htmlFor="company" className="block text-sm font-medium mb-2">
                Entreprise / Agence
              </label>
              <input
                type="text"
                id="company"
                name="company"
                className="w-full px-4 py-2 rounded-lg bg-background border border-input focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Nom de votre organisation"
                required
              />
            </div>
            <div>
              <label htmlFor="message" className="block text-sm font-medium mb-2">
                Message
              </label>
              <textarea
                id="message"
                name="message"
                rows={6}
                className="w-full px-4 py-2 rounded-lg bg-background border border-input focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                placeholder="Décrivez vos besoins et comment veyl.io peut vous aider..."
                required
              />
            </div>
            <Button type="submit" size="lg" className="w-full">
              <Mail className="mr-2 h-4 w-4" />
              Envoyer la demande
            </Button>
            <p className="text-xs text-center text-muted-foreground">
              En soumettant ce formulaire, vous acceptez d'être contacté par notre équipe.
            </p>
          </form>
        </Card>

        {/* CTA */}
        <Card className="p-12 max-w-3xl mx-auto text-center bg-gradient-to-br from-card to-card/50 border-primary/20">
          <h2 className="text-3xl font-bold mb-4">Prêt à démarrer ?</h2>
          <p className="text-muted-foreground mb-8">
            Planifiez une démonstration personnalisée et découvrez comment veyl.io peut transformer votre veille sociale
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" asChild>
              <Link to="#contact">
                <Zap className="mr-2 h-5 w-5" />
                Planifier une démo
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link to="/docs">
                Consulter la documentation
              </Link>
            </Button>
          </div>
        </Card>
      </section>

      <Footer />
    </div>
  );
}
