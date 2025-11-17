import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/contexts/AuthContext';
import { Globe, Instagram, Facebook, LogOut } from 'lucide-react';
import { toast } from 'sonner';
import { TikTokIcon } from '@/components/icons/TikTokIcon';
import { getApiBase, type ConnectedAccount } from '@/lib/api';

export default function Profile() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [connectedAccounts, setConnectedAccounts] = useState<ConnectedAccount[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchConnectedAccounts();
    
    // Reload accounts after OAuth connection (check URL parameters)
    const params = new URLSearchParams(window.location.search);
    if (params.get('token') || params.get('error')) {
      // Reload after a delay to give the backend time to save
      const timer = setTimeout(() => {
        fetchConnectedAccounts();
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, []);

  const fetchConnectedAccounts = async () => {
    try {
      const { getConnectedAccounts } = await import('@/lib/api');
      const data = await getConnectedAccounts();
      setConnectedAccounts(data.accounts || []);
    } catch (error) {
      console.error('Error fetching connected accounts:', error);
    } finally {
      setLoading(false);
    }
  };


  const handleDisconnect = async (accountId: number, provider: string) => {
    if (!confirm(`Do you want to disconnect your ${provider} account?`)) {
      return;
    }

    try {
      const { disconnectAccount } = await import('@/lib/api');
      await disconnectAccount(accountId);
      toast.success(`${provider} account disconnected`);
      fetchConnectedAccounts();
    } catch (error) {
      console.error('Error during disconnection:', error);
      toast.error('Error during disconnection');
    }
  };

  const handleConnect = (provider: string) => {
    // Passer l'user_id actuel pour lier le nouveau compte OAuth au User existant
    const userId = user?.id;
    const apiBase = getApiBase();
    const basePath = apiBase || '';
    const url = userId 
      ? `${basePath}/api/v1/auth/${provider}/start?user_id=${userId}`
      : `${basePath}/api/v1/auth/${provider}/start`;
    window.location.href = url;
  };

  const getProviderIcon = (provider: string) => {
    switch (provider) {
      case 'instagram':
        return <Instagram className="h-5 w-5" style={{ color: '#ac2bac' }} />;
      case 'facebook':
        return <Facebook className="h-5 w-5" style={{ color: '#3b5998' }} />;
      case 'tiktok':
        return <TikTokIcon className="h-5 w-5" />;
      default:
        return <Globe className="h-5 w-5" />;
    }
  };

  const getProviderName = (provider: string) => {
    const names: Record<string, string> = {
      instagram: 'Instagram',
      facebook: 'Facebook',
      tiktok: 'TikTok'
    };
    return names[provider] || provider;
  };

  const handleSignOut = () => {
    localStorage.removeItem('token');
    window.location.href = '/';
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container py-8">

        <div className="max-w-2xl mx-auto">
          {/* Profile Section */}
          <div className="space-y-6">
            {/* Profile Card */}
            <Card className="mb-6">
              <CardContent className="pt-8 pb-6 text-center">
                <img
                  src={`https://api.dicebear.com/7.x/shapes/svg?seed=${user?.email || 'user'}`}
                  alt="avatar"
                  className="rounded-full w-24 h-24 mx-auto mb-4 border-2 border-primary/20"
                />
                <h2 className="text-lg font-semibold mb-1">{user?.name || 'User'}</h2>
                <p className="text-sm text-muted-foreground">{user?.email || 'user@example.com'}</p>
              </CardContent>
            </Card>

            {/* Social Links */}
            <Card>
              <CardHeader className="pb-4">
                <CardTitle className="text-lg">Social Networks</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {['instagram', 'facebook', 'tiktok'].map((provider) => {
                  const account = connectedAccounts.find(acc => acc.provider === provider);
                  const isConnected = !!account;
                  
                  return (
                    <div
                      key={provider}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <div className="flex-shrink-0">
                          {getProviderIcon(provider)}
                        </div>
                        <div>
                          <p className="text-sm font-medium">{getProviderName(provider)}</p>
                          <p className={`text-xs mt-0.5 ${isConnected ? 'text-green-500' : 'text-muted-foreground'}`}>
                            {isConnected ? 'Connected' : 'Not connected'}
                          </p>
                        </div>
                      </div>
                      {isConnected ? (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDisconnect(account!.id, provider)}
                          className="text-destructive hover:text-destructive hover:bg-destructive/10"
                        >
                          Disconnect
                        </Button>
                      ) : (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleConnect(provider)}
                        >
                          Connect
                        </Button>
                      )}
                    </div>
                  );
                })}
              </CardContent>
            </Card>

            {/* Sign Out Button */}
            <div className="pt-4">
              <Button 
                variant="outline" 
                className="w-full gap-2 border-destructive/50 text-destructive hover:bg-destructive/10 hover:text-destructive"
                onClick={handleSignOut}
              >
                <LogOut className="h-4 w-4" />
                Sign Out
              </Button>
            </div>
          </div>

        </div>
      </div>
      <Footer />
    </div>
  );
}
