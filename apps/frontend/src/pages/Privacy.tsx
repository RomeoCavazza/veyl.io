import { Link } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Shield, Lock, Eye, Database, Building2, Globe, Clock, Mail, ExternalLink, FileText } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function Privacy() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container py-8 md:py-12">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div className="text-center space-y-4 pb-6">
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
              Privacy Policy
            </h1>
            <p className="text-muted-foreground">Last updated: November 2, 2025</p>
            
            <div className="flex flex-wrap justify-center gap-3 pt-2">
              <Badge variant="outline" className="px-4 py-2">
                <Shield className="h-3 w-3 mr-2" />
                GDPR Compliant
              </Badge>
              <Badge variant="outline" className="px-4 py-2">
                <Lock className="h-3 w-3 mr-2" />
                CCPA Compliant
              </Badge>
            </div>
          </div>

          {/* Responsable du Traitement - RGPD Art. 13.1(a) */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5 text-primary" />
                1. Data Controller
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                In accordance with Article 13.1(a) of the GDPR, we inform you that the controller of your personal data is:
              </p>
              <div className="bg-muted/50 p-4 rounded-lg space-y-2 text-sm">
                <p><strong>veyl.io</strong></p>
                <p>Cultural intelligence and trend analysis platform</p>
                <p>
                  <strong>Contact:</strong>{' '}
                  <a href="mailto:romeo.cavazza@gmail.com" className="text-primary hover:underline">
                    romeo.cavazza@gmail.com
                  </a>
                </p>
                <p>
                  <strong>Support:</strong>{' '}
                  <a href="https://discord.gg/TKbNuuV4sX" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                    Discord
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </p>
              </div>
              <p className="text-xs text-muted-foreground">
                For any questions regarding the processing of your data, you can also consult our{' '}
                <Link to="/data-deletion" className="text-primary hover:underline">data deletion page</Link>.
              </p>
            </CardContent>
          </Card>

          {/* Collecte de Données */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5 text-primary" />
                2. Data Collection
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm">
                <strong>veyl.io</strong> collects and processes public Instagram and TikTok data via authorized endpoints 
                of the <strong>Meta Graph API</strong> and <strong>TikTok API</strong>. We only collect data that 
                you explicitly authorize us to access during OAuth connection.
              </p>
              
              <div>
                <h4 className="font-semibold text-sm mb-2">Collected data:</h4>
                <ul className="space-y-2 text-sm list-disc list-inside text-muted-foreground">
                  <li>Public Instagram and TikTok posts and hashtag data</li>
                  <li>Page metadata (likes, followers, engagement metrics)</li>
                  <li>User-generated content on connected Pages (comments, notes)</li>
                  <li>Account profile information (username, bio, profile picture)</li>
                  <li>Analytical insights (aggregated and anonymized)</li>
                  <li>User-created project data (name, description, hashtags, followed creators)</li>
                  <li>Authentication data (email, name via OAuth)</li>
                  <li>Automatic technical data (IP address, user-agent, access logs)</li>
                </ul>
              </div>

              <Alert>
                <Shield className="h-4 w-4" />
                <AlertDescription className="text-xs">
                  <strong>App Review Compliance:</strong> Our application is subject to the policies and requirements 
                  of the <strong>Meta for Developers</strong> and <strong>TikTok for Developers</strong> programs. 
                  We strictly comply with their terms of use and data policies.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>

          {/* Base Légale du Traitement - RGPD Art. 13.1(c) */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                3. Legal Basis for Processing
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <p>
                In accordance with Article 6 of the GDPR, the processing of your personal data is based on the following legal bases:
              </p>
              <ul className="space-y-2 list-disc list-inside text-muted-foreground">
                <li>
                  <strong>Consent (Art. 6.1.a):</strong> You explicitly give us your consent during 
                  OAuth connection (Meta, TikTok, Google). You can withdraw your consent at any time.
                </li>
                <li>
                  <strong>Contract performance (Art. 6.1.b):</strong> Processing is necessary for the performance of the service 
                  contract you have entered into with us by using veyl.io.
                </li>
                <li>
                  <strong>Legitimate interest (Art. 6.1.f):</strong> For improving our services, aggregated and anonymized usage 
                  analysis, and platform security.
                </li>
              </ul>
            </CardContent>
          </Card>

          {/* Utilisation des Données */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5 text-primary" />
                4. Use of Your Data
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <p>We use the collected data to:</p>
              <ul className="space-y-2 list-disc list-inside text-muted-foreground">
                <li>Provide trend intelligence and analytics services</li>
                <li>Generate insights for marketing and advertising</li>
                <li>Improve our application and user experience</li>
                <li>Aggregate and anonymize data for research purposes</li>
                <li>Index posts in our <strong>Meilisearch</strong> search engine for fast searches</li>
                <li>Ensure security and prevent abuse</li>
              </ul>
              <Alert className="mt-4 border-destructive/20 bg-destructive/5">
                <Shield className="h-4 w-4 text-destructive" />
                <AlertDescription className="text-xs">
                  <strong className="text-destructive">We DO NOT use your data</strong> for individual profiling 
                  or re-identification purposes. All analytical insights are aggregated, de-identified, and anonymized.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>

          {/* Délais de Conservation - RGPD Art. 13.2(a) */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-primary" />
                5. Data Retention Periods
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <p>
                In accordance with Article 13.2(a) of the GDPR, your data is retained for the following periods:
              </p>
              <div className="bg-muted/50 p-4 rounded-lg space-y-2">
                <div>
                  <strong>User data (profile, projects):</strong>{' '}
                  <span className="text-muted-foreground">Until account deletion or erasure request</span>
                </div>
                <div>
                  <strong>Instagram/TikTok post data:</strong>{' '}
                  <span className="text-muted-foreground">90 days after last consultation of the associated project</span>
                </div>
                <div>
                  <strong>OAuth tokens:</strong>{' '}
                  <span className="text-muted-foreground">Until revocation or disconnection</span>
                </div>
                <div>
                  <strong>Access logs and technical data:</strong>{' '}
                  <span className="text-muted-foreground">30 days</span>
                </div>
                <div>
                  <strong>Anonymized/aggregated data:</strong>{' '}
                  <span className="text-muted-foreground">Indefinitely (does not allow identification)</span>
                </div>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                After these periods, your data is automatically deleted from our systems, except for legal retention obligations.
              </p>
            </CardContent>
          </Card>

          {/* Stockage & Sécurité */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="h-5 w-5 text-primary" />
                6. Data Storage & Security
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <p>We implement industry-standard security measures:</p>
              <ul className="space-y-2 list-disc list-inside text-muted-foreground">
                <li><strong>Transmission encryption:</strong> HTTPS/TLS for all communications</li>
                <li><strong>Secure cloud infrastructure:</strong> Railway (backend) and Vercel (frontend) with access controls</li>
                <li><strong>PostgreSQL database:</strong> Encryption at rest with SSL connections</li>
                <li><strong>Redis:</strong> Secure cache with authentication</li>
                <li><strong>Meilisearch:</strong> Secure search index with master API key</li>
                <li><strong>Regular security audits:</strong> Updates and periodic reviews</li>
              </ul>
            </CardContent>
          </Card>

          {/* Transferts Internationaux - RGPD Art. 13.1(f) */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5 text-primary" />
                7. International Data Transfers
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <p>
                In accordance with Article 13.1(f) of the GDPR, we inform you that some of your data may be transferred 
                to third countries (United States) via our hosting providers:
              </p>
              <ul className="space-y-2 list-disc list-inside text-muted-foreground">
                <li>
                  <strong>Railway (United States):</strong> Backend hosting (PostgreSQL, Redis) - 
                  Compliance via <a href="https://www.railway.app/legal/privacy" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                    Railway Privacy Policy
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </li>
                <li>
                  <strong>Vercel (United States):</strong> Frontend hosting and CDN - 
                  Compliance via <a href="https://vercel.com/legal/privacy-policy" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                    Vercel Privacy Policy
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </li>
                <li>
                  <strong>Meilisearch:</strong> Search engine (self-hosted or cloud depending on configuration)
                </li>
              </ul>
              <Alert className="mt-4">
                <Shield className="h-4 w-4" />
                <AlertDescription className="text-xs">
                  These transfers are governed by <strong>Standard Contractual Clauses (SCC)</strong> approved by the European Commission 
                  and data protection guarantees. You have the right to object to these transfers by contacting us.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>

          {/* Services Tiers */}
          <Card>
            <CardHeader>
              <CardTitle>8. Third-Party Services & Integrations</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <p>We integrate with the following services:</p>
              <ul className="space-y-2 list-disc list-inside text-muted-foreground">
                <li>
                  <strong>Meta (Instagram/Facebook):</strong>{' '}
                  <a href="https://developers.facebook.com/policies" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                    Platform Terms and Developer Policies
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </li>
                <li>
                  <strong>TikTok:</strong>{' '}
                  <a href="https://developers.tiktok.com/doc/tiktok-api-terms-of-service" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                    TikTok API Terms of Service
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </li>
              </ul>
              <p className="mt-3">
                We do not share your personal data with third parties, except when necessary to provide our services 
                or to comply with legal obligations.
              </p>
            </CardContent>
          </Card>

          {/* Vos Droits RGPD */}
          <Card>
            <CardHeader>
              <CardTitle>9. Your Rights (GDPR Compliance)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <p>Under the GDPR, you have the following rights:</p>
              <div className="grid md:grid-cols-2 gap-3">
                <div className="bg-muted/50 p-3 rounded-lg">
                  <strong className="text-sm">Access (Art. 15)</strong>
                  <p className="text-xs text-muted-foreground mt-1">Request a copy of your data</p>
                </div>
                <div className="bg-muted/50 p-3 rounded-lg">
                  <strong className="text-sm">Rectification (Art. 16)</strong>
                  <p className="text-xs text-muted-foreground mt-1">Correct inaccurate data</p>
                </div>
                <div className="bg-muted/50 p-3 rounded-lg">
                  <strong className="text-sm">Erasure (Art. 17)</strong>
                  <p className="text-xs text-muted-foreground mt-1">Request deletion of your data</p>
                </div>
                <div className="bg-muted/50 p-3 rounded-lg">
                  <strong className="text-sm">Restriction (Art. 18)</strong>
                  <p className="text-xs text-muted-foreground mt-1">Limit processing</p>
                </div>
                <div className="bg-muted/50 p-3 rounded-lg">
                  <strong className="text-sm">Portability (Art. 20)</strong>
                  <p className="text-xs text-muted-foreground mt-1">Receive your data (JSON)</p>
                </div>
                <div className="bg-muted/50 p-3 rounded-lg">
                  <strong className="text-sm">Objection (Art. 21)</strong>
                  <p className="text-xs text-muted-foreground mt-1">Object to processing</p>
                </div>
              </div>
              <div className="mt-4 space-y-2">
                <p className="text-xs">
                  <strong>To exercise these rights:</strong>
                </p>
                <ul className="space-y-1 text-xs text-muted-foreground list-disc list-inside">
                  <li>
                    Visit our{' '}
                    <Link to="/data-deletion" className="text-primary hover:underline font-semibold">
                      data deletion page
                    </Link>
                  </li>
                  <li>
                    Contact us by email:{' '}
                    <a href="mailto:romeo.cavazza@gmail.com" className="text-primary hover:underline">
                      romeo.cavazza@gmail.com
                    </a>
                  </li>
                </ul>
                <p className="text-xs text-muted-foreground mt-3">
                  <strong>Response time:</strong> We respond to all requests within <strong>30 days</strong> 
                  in accordance with the GDPR (Art. 12.3).
                </p>
                <p className="text-xs text-muted-foreground">
                  <strong>Recourse:</strong> You have the right to lodge a complaint with the competent supervisory authority 
                  (in France: <a href="https://www.cnil.fr" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                    CNIL
                    <ExternalLink className="h-3 w-3" />
                  </a>) if you believe that the processing of your data constitutes a violation of the GDPR.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Conformité Meta & TikTok */}
          <Card>
            <CardHeader>
              <CardTitle>10. Meta & TikTok Compliance</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <p>
                As a partner of <strong>Meta for Developers</strong> and <strong>TikTok for Developers</strong>, 
                we commit to:
              </p>
              <ul className="space-y-2 list-disc list-inside text-muted-foreground">
                <li>Respecting Meta and TikTok data policies</li>
                <li>Using only authorized and documented API endpoints</li>
                <li>Not storing data beyond the authorized period</li>
                <li>Providing a data deletion mechanism compliant with platform requirements</li>
                <li>Maintaining a test/demo environment for App Review with mock data</li>
              </ul>
              <p className="mt-3 text-xs text-muted-foreground">
                To remove veyl.io's access to your Instagram/TikTok accounts, you can also do so directly 
                from your Meta/TikTok account settings.
              </p>
            </CardContent>
          </Card>

          {/* Contact */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="h-5 w-5 text-primary" />
                11. Contact
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <p>For any questions or concerns regarding privacy:</p>
              <ul className="space-y-2">
                <li>
                  <strong>Email:</strong>{' '}
                  <a href="mailto:romeo.cavazza@gmail.com" className="text-primary hover:underline">
                    romeo.cavazza@gmail.com
                  </a>
                </li>
                <li>
                  <strong>Deletion requests:</strong>{' '}
                  <Link to="/data-deletion" className="text-primary hover:underline">/data-deletion</Link>
                </li>
                <li>
                  <strong>Support:</strong>{' '}
                  <a href="https://discord.gg/TKbNuuV4sX" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                    Discord
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </li>
              </ul>
              <p className="text-xs text-muted-foreground mt-4">
                We respond to all requests within <strong>30 days</strong> in accordance with the GDPR (Art. 12.3).
              </p>
            </CardContent>
          </Card>
        </div>
      </div>

      <Footer />
    </div>
  );
}
