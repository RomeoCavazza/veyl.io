import { Link } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Shield, Lock, Eye, Database, ExternalLink } from 'lucide-react';

export default function Privacy() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container py-8">
        <div className="max-w-4xl mx-auto space-y-8">
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Politique de Confidentialité
            </h1>
            <p className="text-muted-foreground">Dernière mise à jour : 02 novembre 2025</p>
            
            {/* Badges conformité */}
            <div className="flex flex-wrap justify-center gap-3 pt-4">
              <Badge variant="outline" className="px-4 py-2">
                <Shield className="h-3 w-3 mr-2" />
                Conforme RGPD
              </Badge>
              <Badge variant="outline" className="px-4 py-2">
                <Lock className="h-3 w-3 mr-2" />
                Conforme CCPA
              </Badge>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5 text-primary" />
                1. Collecte de Données
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>
                <strong>veyl.io</strong> ("nous", "notre", "nos") collecte et traite des données publiques Instagram et TikTok 
                via les endpoints autorisés des <strong>Meta Graph API</strong> et <strong>TikTok API</strong>. 
                Nous collectons uniquement les données que vous nous autorisez explicitement à accéder.
              </p>
              <h4 className="font-semibold mt-4 mb-2">Données que nous collectons :</h4>
              <ul className="space-y-2">
                <li>Posts Instagram et TikTok publics et données de hashtags</li>
                <li>Métadonnées de pages (likes, followers, métriques d'engagement)</li>
                <li>Contenu généré par les utilisateurs sur les Pages connectées (commentaires, notes)</li>
                <li>Informations de profil de compte (nom d'utilisateur, bio, photo de profil)</li>
                <li>Insights analytiques (agrégés et anonymisés)</li>
                <li>Données de projets créés par l'utilisateur (nom, description, hashtags, créateurs suivis)</li>
              </ul>
              <p className="mt-4 text-sm bg-muted p-3 rounded-lg">
                <strong>Conformité App Review :</strong> Notre application est soumise aux politiques et exigences 
                des programmes <strong>Meta for Developers</strong> et <strong>TikTok for Developers</strong>. 
                Nous respectons strictement leurs conditions d'utilisation et leurs politiques de données.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5 text-primary" />
                2. Utilisation de Vos Données
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>Nous utilisons les données collectées pour :</p>
              <ul className="space-y-2">
                <li>Fournir des services d'intelligence des tendances et d'analytics</li>
                <li>Générer des insights pour le marketing et la publicité</li>
                <li>Améliorer notre application et l'expérience utilisateur</li>
                <li>Agréger et anonymiser les données à des fins de recherche</li>
                <li>Indexer les posts dans notre moteur de recherche <strong>Meilisearch</strong> pour des recherches rapides</li>
              </ul>
              <p className="font-semibold mt-4 bg-destructive/10 p-3 rounded-lg border border-destructive/20">
                <strong className="text-destructive">Nous n'utilisons PAS vos données</strong> à des fins de profilage individuel 
                ou de ré-identification. Tous les insights analytiques sont agrégés, dé-identifiés et anonymisés.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="h-5 w-5 text-primary" />
                3. Stockage & Sécurité des Données
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>
                Nous mettons en œuvre des mesures de sécurité de niveau industrie pour protéger vos données :
              </p>
              <ul className="space-y-2">
                <li><strong>Chiffrement des transmissions</strong> : HTTPS/TLS pour toutes les communications</li>
                <li><strong>Infrastructure cloud sécurisée</strong> : Hébergement sur Railway (backend) et Vercel (frontend) avec contrôles d'accès</li>
                <li><strong>Base de données PostgreSQL</strong> : Chiffrement au repos avec connexions SSL</li>
                <li><strong>Redis</strong> : Cache sécurisé avec authentification</li>
                <li><strong>Meilisearch</strong> : Index de recherche sécurisé avec clé API maître</li>
                <li><strong>Audits de sécurité réguliers</strong> : Mises à jour et revues périodiques</li>
                <li><strong>Rétention limitée</strong> : Données conservées 90 jours par défaut (configurable)</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>4. Services Tiers & Intégrations</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>
                Nous intégrons avec les services suivants et respectons leurs conditions :
              </p>
              <ul className="space-y-3">
                <li>
                  <strong>Meta (Instagram/Facebook)</strong> : Conformité avec les{' '}
                  <a href="https://developers.facebook.com/policies" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                    Platform Terms et Developer Policies de Meta
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </li>
                <li>
                  <strong>TikTok</strong> : Conformité avec les{' '}
                  <a href="https://developers.tiktok.com/doc/tiktok-api-terms-of-service" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                    TikTok API Terms of Service
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </li>
                <li><strong>Railway</strong> : Hébergement backend (PostgreSQL, Redis)</li>
                <li><strong>Vercel</strong> : Hébergement frontend et CDN</li>
                <li><strong>Meilisearch</strong> : Moteur de recherche (self-hosted ou cloud)</li>
              </ul>
              <p className="mt-4">
                Nous ne partageons pas vos données personnelles avec des tiers, sauf si nécessaire pour fournir nos services 
                ou pour se conformer à des obligations légales.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>5. Vos Droits (Conformité RGPD)</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>En vertu du RGPD et des lois sur la protection des données, vous avez le droit de :</p>
              <ul className="space-y-2">
                <li><strong>Accès :</strong> Demander une copie de vos données</li>
                <li><strong>Rectification :</strong> Corriger les données inexactes</li>
                <li><strong>Effacement :</strong> Demander la suppression de vos données</li>
                <li><strong>Restriction :</strong> Limiter le traitement de vos données</li>
                <li><strong>Portabilité :</strong> Recevoir vos données dans un format structuré (JSON)</li>
                <li><strong>Opposition :</strong> Vous opposer au traitement de vos données</li>
                <li><strong>Retrait du consentement :</strong> Retirer votre consentement à tout moment</li>
              </ul>
              <p className="mt-4">
                Pour exercer ces droits, visitez notre{' '}
                <Link to="/data-deletion" className="text-primary hover:underline font-semibold">
                  page de suppression de données
                </Link>{' '}
                ou contactez-nous à <a href="mailto:privacy@veyl.io" className="text-primary hover:underline">privacy@veyl.io</a>
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>6. Conformité Meta & TikTok</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p className="mb-4">
                En tant que partenaire <strong>Meta for Developers</strong> et <strong>TikTok for Developers</strong>, 
                nous nous engageons à :
              </p>
              <ul className="space-y-2">
                <li>Respecter les politiques de données de Meta et TikTok</li>
                <li>Utiliser uniquement les endpoints API autorisés et documentés</li>
                <li>Ne pas stocker de données au-delà de la période autorisée</li>
                <li>Fournir un mécanisme de suppression des données conforme aux exigences des plateformes</li>
                <li>Maintenir un environnement de test/démo pour l'App Review avec des données mock</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>7. Contact</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>Pour toute question ou préoccupation liée à la confidentialité :</p>
              <ul className="space-y-2">
                <li><strong>Email :</strong> <a href="mailto:privacy@veyl.io" className="text-primary hover:underline">privacy@veyl.io</a></li>
                <li><strong>Demandes de suppression :</strong> <Link to="/data-deletion" className="text-primary hover:underline">/data-deletion</Link></li>
                <li><strong>Support :</strong> <a href="mailto:support@veyl.io" className="text-primary hover:underline">support@veyl.io</a></li>
              </ul>
              <p className="mt-4 text-xs text-muted-foreground">
                Nous répondons à toutes les demandes dans un délai de 30 jours conformément au RGPD.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      <Footer />
    </div>
  );
}
