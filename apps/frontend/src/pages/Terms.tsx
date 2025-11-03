import { Link } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileText, AlertTriangle, Shield, Scale, Gavel, ExternalLink, Mail, Bell } from 'lucide-react';

export default function Terms() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container py-8 md:py-12">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div className="text-center space-y-4 pb-6">
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
              Terms of Service
            </h1>
            <p className="text-muted-foreground">Last updated: November 2, 2025</p>
          </div>

          {/* Acceptation */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                1. Acceptance of Terms
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <p>
                By accessing and using <strong>veyl.io</strong> ("Service"), you accept and agree 
                to be bound by these Terms of Service. If you do not accept these terms, 
                please do not use our Service.
              </p>
              <p className="text-muted-foreground">
                These terms apply to all users of the Service, including visitors, 
                authenticated users, and contributors.
              </p>
            </CardContent>
          </Card>

          {/* Description du Service */}
          <Card>
            <CardHeader>
              <CardTitle>2. Service Description</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-3">
              <p>
                <strong>veyl.io</strong> is a social intelligence platform that provides:
              </p>
              <ul className="space-y-2 list-disc list-inside text-muted-foreground">
                <li>Hashtag search and analysis on Instagram and TikTok</li>
                <li>Instagram Business and TikTok account analytics</li>
                <li>Content performance tracking</li>
                <li>Trend monitoring and alerts</li>
                <li>Custom monitoring project creation</li>
                <li>Creator and influencer analysis</li>
                <li>Ultra-fast full-text search via <strong>Meilisearch</strong></li>
              </ul>
              <p className="mt-3">
                The Service is accessible via a web interface and REST API. The application is currently 
                in active development phase and subject to <strong>Meta</strong> and <strong>TikTok</strong> App Review processes.
              </p>
              <p className="text-xs text-muted-foreground">
                The Service is provided "as is" and may be modified, suspended, or interrupted at any time without notice.
              </p>
            </CardContent>
          </Card>

          {/* Obligations Utilisateur */}
          <Card>
            <CardHeader>
              <CardTitle>3. User Obligations</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-3">
              <p>You agree to:</p>
              <ul className="space-y-2 list-disc list-inside text-muted-foreground">
                <li>Provide accurate and up-to-date account information</li>
                <li>Maintain the security of your account credentials</li>
                <li>Use the Service in compliance with applicable laws</li>
                <li>Not engage in unauthorized scraping or data collection</li>
                <li>Respect intellectual property rights</li>
                <li>Comply with <a href="https://developers.facebook.com/policies" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">Meta Platform Terms and Policies <ExternalLink className="h-3 w-3" /></a></li>
                <li>Comply with <a href="https://developers.tiktok.com/doc/tiktok-api-terms-of-service" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">TikTok API Terms of Service <ExternalLink className="h-3 w-3" /></a></li>
                <li>Use the Service only for legitimate and ethical purposes</li>
                <li>Respect API rate limits and not overload servers</li>
              </ul>
            </CardContent>
          </Card>

          {/* Activités Interdites */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-destructive" />
                4. Prohibited Activities
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-3">
              <p>You must NOT:</p>
              <ul className="space-y-2 list-disc list-inside text-muted-foreground">
                <li>Use the Service for spam or malicious activities</li>
                <li>Attempt to reverse engineer or hack the platform</li>
                <li>Violate any applicable law or regulation</li>
                <li>Infringe on others' privacy or intellectual property rights</li>
                <li>Use bots or automated scripts without authorization</li>
                <li>Violate API rate limits or overload servers</li>
                <li>Share or sell your access credentials with third parties</li>
                <li>Use the Service to collect data for unauthorized profiling purposes</li>
                <li>Reproduce, copy, or sell the Service without authorization</li>
                <li>Interfere with the normal operation of the Service</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-3">
                Any violation of these rules may result in immediate suspension of your account and legal action.
              </p>
            </CardContent>
          </Card>

          {/* Données & Confidentialité */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                5. Data Use & Privacy
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-3">
              <p>
                Your use of the Service is also governed by our{' '}
                <Link to="/privacy" className="text-primary hover:underline font-semibold">Privacy Policy</Link>.
              </p>
              <p>
                We collect and process Instagram and TikTok data in accordance with 
                <strong> Meta</strong> and <strong>TikTok</strong> policies and applicable data protection laws (GDPR, CCPA).
              </p>
              <div className="bg-muted/50 p-3 rounded-lg mt-3">
                <p className="text-xs">
                  <strong>Important:</strong> As a partner of <strong>Meta for Developers</strong> and 
                  <strong> TikTok for Developers</strong>, we strictly comply with their terms of use 
                  and data policies. Any violation of these terms may result in immediate suspension 
                  of your account.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Propriété Intellectuelle */}
          <Card>
            <CardHeader>
              <CardTitle>6. Intellectual Property</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-3">
              <p>
                All content, features, and tools of <strong>veyl.io</strong> are our property 
                and protected by copyright, trademark, and other intellectual property laws.
              </p>
              <p>
                The veyl.io source code is available under an open source license on{' '}
                <a href="https://github.com/RomeoCavazza/veyl.io" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                  GitHub
                  <ExternalLink className="h-3 w-3" />
                </a>. 
                See the LICENSE file for more details.
              </p>
              <p className="text-xs text-muted-foreground">
                You retain all rights to content you create via the Service (projects, configurations). 
                By using the Service, you grant us a limited license to host and process this content.
              </p>
            </CardContent>
          </Card>

          {/* Limitation Responsabilité */}
          <Card>
            <CardHeader>
              <CardTitle>7. Limitation of Liability</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-3">
              <p>
                <strong>veyl.io</strong> is provided "as is" without warranties of any kind, express or implied. 
                We do not guarantee that the Service will be uninterrupted, secure, error-free, or meet your needs.
              </p>
              <p>
                We are not liable for indirect, incidental, consequential, or accessory damages arising 
                from your use of the Service, including but not limited to: data loss, loss of profits, 
                business interruption.
              </p>
              <p>
                The Service may be temporarily unavailable due to maintenance, updates, 
                or changes to third-party APIs (Meta, TikTok). We do not guarantee 100% availability.
              </p>
              <p className="text-xs text-muted-foreground">
                To the extent permitted by law, our total liability to you shall not exceed the amount 
                you have paid to use the Service in the last 12 months, or €100 if the Service is free.
              </p>
            </CardContent>
          </Card>

          {/* Force Majeure */}
          <Card>
            <CardHeader>
              <CardTitle>8. Force Majeure</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <p>
                We shall not be liable for any delay or failure in the performance of our obligations 
                resulting from circumstances beyond our reasonable control, including:
              </p>
              <ul className="space-y-1 list-disc list-inside text-muted-foreground">
                <li>Meta or TikTok API interruptions</li>
                <li>Server or infrastructure failures (Railway, Vercel)</li>
                <li>Natural disasters, acts of war, terrorism</li>
                <li>Strikes, social conflicts</li>
                <li>Changes to Meta/TikTok policies or terms of use</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                In case of force majeure, we will inform you as soon as possible and take all reasonable 
                measures to minimize the impact.
              </p>
            </CardContent>
          </Card>

          {/* Résiliation */}
          <Card>
            <CardHeader>
              <CardTitle>9. Termination</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-3">
              <p>
                We reserve the right to suspend or terminate your access to the Service at any time 
                for violation of these Terms, violation of Meta/TikTok policies, or for any other reason 
                at our sole discretion.
              </p>
              <p>
                You may terminate your account at any time by using our{' '}
                <Link to="/data-deletion" className="text-primary hover:underline">data deletion page</Link>.
              </p>
              <p>
                Upon termination, your data will be deleted in accordance with our Privacy Policy 
                and Meta and TikTok requirements, within 30 days.
              </p>
              <p className="text-xs text-muted-foreground">
                Sections relating to intellectual property, limitation of liability, and dispute resolution 
                will survive termination of these Terms.
              </p>
            </CardContent>
          </Card>

          {/* Modifications Conditions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-primary" />
                10. Terms Modifications
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-3">
              <p>
                We may modify these Terms from time to time to reflect changes in our services, 
                legal requirements, or best practices. Any modification will be published on this page 
                with a revised update date.
              </p>
              <p>
                <strong>Modification notifications:</strong>
              </p>
              <ul className="space-y-1 list-disc list-inside text-muted-foreground">
                <li>Major modifications: email notification to the address associated with your account (30 days before)</li>
                <li>Minor modifications: notification via a banner on the Service (14 days before)</li>
                <li>Urgent modifications (security, compliance): immediate notification</li>
              </ul>
              <p className="mt-3">
                Continued use of the Service after modifications constitutes acceptance of the updated Terms. 
                If you do not accept the modifications, you must stop using the Service and terminate your account.
              </p>
            </CardContent>
          </Card>

          {/* Juridiction & Droit Applicable */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gavel className="h-5 w-5 text-primary" />
                11. Jurisdiction & Applicable Law
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-3">
              <p>
                These Terms of Service are governed by <strong>French law</strong>.
              </p>
              <p>
                In case of dispute, and after attempting amicable resolution, the parties agree to seek a solution 
                through <strong>mediation</strong> before any legal action.
              </p>
              <p>
                In the absence of an amicable agreement or mediation, any dispute relating to the interpretation or execution of these Terms 
                shall be submitted to the competent courts of <strong>Paris, France</strong>.
              </p>
              <p className="text-xs text-muted-foreground">
                This jurisdiction clause does not apply to consumers residing in the European Union, who retain 
                the right to bring proceedings before the courts of their country of residence.
              </p>
            </CardContent>
          </Card>

          {/* Résolution des Litiges */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Scale className="h-5 w-5 text-primary" />
                12. Dispute Resolution
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-3">
              <p>
                <strong>Prior mediation:</strong> In case of dispute, you may resort to a consumer mediator. 
                For more information, visit the{' '}
                <a href="https://www.economie.gouv.fr/mediation-conso" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                  Consumer Mediation
                  <ExternalLink className="h-3 w-3" />
                </a> website.
              </p>
              <p>
                <strong>CNIL complaint:</strong> For any question regarding the processing of your personal data, 
                you may lodge a complaint with the{' '}
                <a href="https://www.cnil.fr" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                  CNIL
                  <ExternalLink className="h-3 w-3" />
                </a>.
              </p>
              <p>
                <strong>Arbitration:</strong> The parties may also agree to submit their dispute to arbitration 
                in accordance with French arbitration rules.
              </p>
            </CardContent>
          </Card>

          {/* Contact */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="h-5 w-5 text-primary" />
                13. Contact Information
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <p>For any questions regarding these Terms:</p>
              <ul className="space-y-2">
                <li>
                  <strong>Legal email:</strong>{' '}
                  <a href="mailto:romeo.cavazza@gmail.com" className="text-primary hover:underline">
                    romeo.cavazza@gmail.com
                  </a>
                </li>
                <li>
                  <strong>Support:</strong>{' '}
                  <a href="https://discord.gg/TKbNuuV4sX" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline inline-flex items-center gap-1">
                    Discord
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </li>
                <li>
                  <strong>Privacy Policy:</strong>{' '}
                  <Link to="/privacy" className="text-primary hover:underline">/privacy</Link>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>

      <Footer />
    </div>
  );
}
