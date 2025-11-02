import { Link } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileText, AlertTriangle, Shield, ExternalLink } from 'lucide-react';

export default function Terms() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container py-8">
        <div className="max-w-4xl mx-auto space-y-8">
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Conditions d'Utilisation
            </h1>
            <p className="text-muted-foreground">Dernière mise à jour : 02 novembre 2025</p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                1. Acceptation des Conditions
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>
                En accédant et en utilisant <strong>veyl.io</strong> ("Service"), vous acceptez et vous engagez 
                à être lié par ces Conditions d'Utilisation. Si vous n'acceptez pas ces conditions, 
                veuillez ne pas utiliser notre Service.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>2. Description du Service</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>
                <strong>veyl.io</strong> est une plateforme d'intelligence sociale qui fournit :
              </p>
              <ul className="space-y-2">
                <li>Recherche et analyse de hashtags sur Instagram et TikTok</li>
                <li>Analytics de comptes Instagram Business et TikTok</li>
                <li>Suivi des performances de contenu</li>
                <li>Surveillance des tendances et alertes</li>
                <li>Création de projets de veille personnalisés</li>
                <li>Analyse de créateurs et d'influenceurs</li>
                <li>Recherche full-text ultra-rapide via <strong>Meilisearch</strong></li>
              </ul>
              <p className="mt-4">
                Le Service est accessible via une interface web et une API REST. L'application est actuellement 
                en phase de développement actif et soumise aux processus d'App Review de <strong>Meta</strong> et <strong>TikTok</strong>.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>3. Obligations de l'Utilisateur</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>Vous vous engagez à :</p>
              <ul className="space-y-2">
                <li>Fournir des informations de compte précises et à jour</li>
                <li>Maintenir la sécurité de vos identifiants de compte</li>
                <li>Utiliser le Service en conformité avec les lois applicables</li>
                <li>Ne pas vous engager dans du scraping ou de la collecte de données non autorisés</li>
                <li>Respecter les droits de propriété intellectuelle</li>
                <li>Respecter les <a href="https://developers.facebook.com/policies" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">Platform Terms et Policies de Meta <ExternalLink className="h-3 w-3" /></a></li>
                <li>Respecter les <a href="https://developers.tiktok.com/doc/tiktok-api-terms-of-service" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">TikTok API Terms of Service <ExternalLink className="h-3 w-3" /></a></li>
                <li>Utiliser le Service uniquement pour des fins légitimes et conformes à l'éthique</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-destructive" />
                4. Activités Interdites
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>Vous ne devez PAS :</p>
              <ul className="space-y-2">
                <li>Utiliser le Service pour du spam ou des activités malveillantes</li>
                <li>Tenter de rétro-ingénier ou de pirater la plateforme</li>
                <li>Violer toute loi ou réglementation applicable</li>
                <li>Enfreindre les droits de vie privée ou de propriété intellectuelle d'autrui</li>
                <li>Utiliser des bots ou scripts automatisés sans autorisation</li>
                <li>Violer les rate limits de l'API ou surcharger les serveurs</li>
                <li>Partager ou vendre vos identifiants d'accès avec des tiers</li>
                <li>Utiliser le Service pour collecter des données à des fins de profilage non autorisé</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                5. Utilisation des Données & Confidentialité
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>
                Votre utilisation du Service est également régie par notre{' '}
                <Link to="/privacy" className="text-primary hover:underline font-semibold">Politique de Confidentialité</Link>.
              </p>
              <p className="mt-2">
                Nous collectons et traitons des données Instagram et TikTok conformément aux politiques de 
                <strong> Meta</strong> et <strong>TikTok</strong> et aux lois applicables sur la protection des données (RGPD, CCPA).
              </p>
              <p className="mt-4 text-sm bg-muted p-3 rounded-lg">
                <strong>Important :</strong> En tant que partenaire <strong>Meta for Developers</strong> et 
                <strong> TikTok for Developers</strong>, nous respectons strictement leurs conditions d'utilisation 
                et leurs politiques de données. Toute violation de ces conditions peut entraîner la suspension 
                immédiate de votre compte.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>6. Propriété Intellectuelle</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>
                Tous les contenus, fonctionnalités et outils de <strong>veyl.io</strong> sont notre propriété 
                et protégés par les lois sur le droit d'auteur, les marques de commerce et autres lois 
                sur la propriété intellectuelle.
              </p>
              <p className="mt-4">
                Le code source de veyl.io est disponible sous licence open source sur{' '}
                <a href="https://github.com/RomeoCavazza/veyl.io" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                  GitHub
                  <ExternalLink className="h-3 w-3" />
                </a>. 
                Consultez le fichier LICENSE pour plus de détails.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>7. Limitation de Responsabilité</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>
                <strong>veyl.io</strong> est fourni "en l'état" sans garanties d'aucune sorte. Nous ne sommes pas responsables 
                des dommages indirects, incidents ou consécutifs découlant de votre utilisation du Service.
              </p>
              <p className="mt-4">
                Le Service peut être indisponible temporairement en raison de maintenance, de mises à jour, 
                ou de modifications des API tiers (Meta, TikTok). Nous ne garantissons pas une disponibilité à 100%.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>8. Résiliation</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>
                Nous nous réservons le droit de suspendre ou de résilier votre accès au Service à tout moment 
                pour violation de ces Conditions, violation des politiques Meta/TikTok, ou pour toute autre raison 
                à notre seule discrétion.
              </p>
              <p className="mt-4">
                En cas de résiliation, vos données seront supprimées conformément à notre Politique de Confidentialité 
                et aux exigences de Meta et TikTok.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>9. Modifications des Conditions</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>
                Nous pouvons modifier ces Conditions de temps à autre. Toute modification sera publiée sur cette page 
                avec une date de mise à jour révisée.
              </p>
              <p className="mt-4">
                L'utilisation continue du Service après les modifications constitue l'acceptation des Conditions mises à jour.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>10. Informations de Contact</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>Pour toute question concernant ces Conditions :</p>
              <ul className="space-y-2">
                <li><strong>Email légal :</strong> <a href="mailto:legal@veyl.io" className="text-primary hover:underline">legal@veyl.io</a></li>
                <li><strong>Support :</strong> <a href="mailto:support@veyl.io" className="text-primary hover:underline">support@veyl.io</a></li>
                <li><strong>Communauté :</strong> <a href="https://discord.gg/TKbNuuV4sX" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">Discord <ExternalLink className="h-3 w-3" /></a></li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>

      <Footer />
    </div>
  );
}
