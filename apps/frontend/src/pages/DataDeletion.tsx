import { Link } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { AlertCircle, Trash2, Shield, Clock, Database, ExternalLink } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';

export default function DataDeletion() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container py-8">
        <div className="max-w-3xl mx-auto space-y-8">
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Demande de Suppression de Données
            </h1>
            <p className="text-muted-foreground">
              Demandez la suppression de vos données personnelles de veyl.io
            </p>
            
            {/* Badges conformité */}
            <div className="flex flex-wrap justify-center gap-3 pt-4">
              <Badge variant="outline" className="px-4 py-2">
                <Shield className="h-3 w-3 mr-2" />
                Conforme RGPD
              </Badge>
              <Badge variant="outline" className="px-4 py-2">
                <Shield className="h-3 w-3 mr-2" />
                Conforme Meta/TikTok
              </Badge>
            </div>
          </div>

          <Alert>
            <Shield className="h-4 w-4" />
            <AlertTitle>Vos Droits sur les Données</AlertTitle>
            <AlertDescription>
              Conformément au RGPD et aux réglementations sur la confidentialité, vous avez le droit de demander 
              la suppression de vos données personnelles. Ce processus prend généralement <strong>30 jours</strong> à compléter.
            </AlertDescription>
          </Alert>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5 text-primary" />
                Ce qui sera supprimé
              </CardTitle>
              <CardDescription>
                La soumission de cette demande supprimera définitivement les données suivantes :
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3 text-sm">
                <li className="flex items-start gap-3">
                  <Trash2 className="h-5 w-5 text-destructive mt-0.5 flex-shrink-0" />
                  <div>
                    <strong className="text-foreground">Votre profil de compte et données d'authentification</strong>
                    <p className="text-muted-foreground mt-1">Email, nom, identifiants OAuth (Meta, TikTok, Google)</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <Trash2 className="h-5 w-5 text-destructive mt-0.5 flex-shrink-0" />
                  <div>
                    <strong className="text-foreground">Comptes Instagram Business et Pages TikTok connectés</strong>
                    <p className="text-muted-foreground mt-1">Tokens OAuth, métadonnées de compte</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <Trash2 className="h-5 w-5 text-destructive mt-0.5 flex-shrink-0" />
                  <div>
                    <strong className="text-foreground">Projets créés et configurations de veille</strong>
                    <p className="text-muted-foreground mt-1">Nom, description, hashtags surveillés, créateurs suivis</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <Trash2 className="h-5 w-5 text-destructive mt-0.5 flex-shrink-0" />
                  <div>
                    <strong className="text-foreground">Rapports analytiques générés et insights</strong>
                    <p className="text-muted-foreground mt-1">Graphiques, métriques, analyses personnalisées</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <Trash2 className="h-5 w-5 text-destructive mt-0.5 flex-shrink-0" />
                  <div>
                    <strong className="text-foreground">Logs d'utilisation et historique d'activité</strong>
                    <p className="text-muted-foreground mt-1">Historique de recherche, requêtes API, actions utilisateur</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <Trash2 className="h-5 w-5 text-destructive mt-0.5 flex-shrink-0" />
                  <div>
                    <strong className="text-foreground">Données dans Meilisearch</strong>
                    <p className="text-muted-foreground mt-1">Index de recherche liés à vos projets</p>
                  </div>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Formulaire de Demande de Suppression</CardTitle>
              <CardDescription>
                Remplissez ce formulaire pour demander la suppression de vos données
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form className="space-y-6">
                <div className="space-y-2">
                  <label htmlFor="email" className="text-sm font-medium">
                    Adresse Email *
                  </label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="votre.email@exemple.com"
                    required
                  />
                  <p className="text-xs text-muted-foreground">
                    Entrez l'email associé à votre compte veyl.io
                  </p>
                </div>

                <div className="space-y-2">
                  <label htmlFor="user-id" className="text-sm font-medium">
                    User ID (Optionnel)
                  </label>
                  <Input
                    id="user-id"
                    type="text"
                    placeholder="Trouvé dans vos paramètres de profil"
                  />
                  <p className="text-xs text-muted-foreground">
                    Facilite le traitement de votre demande
                  </p>
                </div>

                <div className="space-y-2">
                  <label htmlFor="reason" className="text-sm font-medium">
                    Raison de la Suppression (Optionnel)
                  </label>
                  <Textarea
                    id="reason"
                    placeholder="Aidez-nous à nous améliorer en partageant pourquoi vous partez..."
                    rows={4}
                  />
                </div>

                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Attention : Cette action est irréversible</AlertTitle>
                  <AlertDescription>
                    Une fois vos données supprimées, elles ne peuvent pas être récupérées. 
                    Vous devrez créer un nouveau compte pour utiliser veyl.io à nouveau.
                  </AlertDescription>
                </Alert>

                <div className="flex gap-3">
                  <Button type="submit" variant="destructive" className="flex-1">
                    <Trash2 className="h-4 w-4 mr-2" />
                    Demander la Suppression des Données
                  </Button>
                  <Button type="button" variant="outline">
                    Annuler
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Options Alternatives</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h4 className="font-medium mb-2 flex items-center gap-2">
                  <Database className="h-4 w-4 text-primary" />
                  Télécharger Vos Données
                </h4>
                <p className="text-sm text-muted-foreground mb-3">
                  Avant de supprimer, vous pouvez demander une copie de vos données au format JSON
                </p>
                <Button variant="outline" size="sm">
                  Demander un Export de Données
                </Button>
              </div>

              <div className="pt-4 border-t">
                <h4 className="font-medium mb-2">Déconnecter Instagram/TikTok uniquement</h4>
                <p className="text-sm text-muted-foreground mb-3">
                  Retirer l'accès Instagram/TikTok sans supprimer votre compte veyl.io
                </p>
                <Button variant="outline" size="sm" asChild>
                  <Link to="/profile">Aller aux Paramètres de Profil</Link>
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                Conformité Meta & TikTok
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>
                En tant que partenaire <strong>Meta for Developers</strong> et <strong>TikTok for Developers</strong>, 
                nous sommes tenus de fournir un mécanisme de suppression des données conforme à leurs politiques.
              </p>
              <ul className="space-y-2 mt-4">
                <li className="flex items-start gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                  <span>
                    Les données seront supprimées de nos systèmes (PostgreSQL, Redis, Meilisearch)
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                  <span>
                    Les tokens OAuth seront révoqués via les API Meta et TikTok
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                  <span>
                    Vous recevrez une confirmation par email une fois la suppression complétée
                  </span>
                </li>
              </ul>
              <p className="mt-4 text-xs text-muted-foreground bg-muted p-3 rounded-lg">
                <strong>Délai de traitement :</strong> Les demandes de suppression sont traitées dans un délai de 30 jours 
                conformément au RGPD et aux réglementations applicables sur la protection des données. 
                Vous recevrez un email de confirmation une fois la suppression complétée.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-primary" />
                Questions ou Problèmes ?
              </CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none">
              <p>
                Si vous avez besoin d'assistance avec votre demande de suppression de données ou avez des questions 
                concernant nos pratiques de données :
              </p>
              <ul className="space-y-2">
                <li>
                  <strong>Email :</strong>{' '}
                  <a href="mailto:privacy@veyl.io" className="text-primary hover:underline">privacy@veyl.io</a>
                </li>
                <li>
                  <strong>Support :</strong>{' '}
                  <a href="mailto:support@veyl.io" className="text-primary hover:underline">support@veyl.io</a>
                </li>
                <li>
                  <strong>Discord :</strong>{' '}
                  <a href="https://discord.gg/TKbNuuV4sX" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                    Rejoindre le serveur Discord
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </li>
              </ul>
              <p className="text-xs text-muted-foreground mt-4">
                Les demandes de suppression de données sont traitées dans un délai de 30 jours conformément au RGPD et 
                aux réglementations applicables sur la protection des données. Vous recevrez un email de confirmation 
                une fois la suppression complétée.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      <Footer />
    </div>
  );
}
