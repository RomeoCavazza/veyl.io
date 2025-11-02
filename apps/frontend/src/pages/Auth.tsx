import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { Loader2, Facebook, Twitter, Instagram } from 'lucide-react';
import { TikTokIcon } from '@/components/icons/TikTokIcon';
import { toast } from 'sonner';
import { Link } from 'react-router-dom';
import { Navbar } from '@/components/Navbar';
import { Footer } from '@/components/Footer';
import { getApiBase } from '@/lib/api';

export default function Auth() {
  const { signIn, signUp } = useAuth();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('login');

  // Sign In form
  const [signInEmail, setSignInEmail] = useState('');
  const [signInPassword, setSignInPassword] = useState('');

  // Sign Up form
  const [signUpEmail, setSignUpEmail] = useState('');
  const [signUpPassword, setSignUpPassword] = useState('');
  const [signUpName, setSignUpName] = useState('');

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    const { error } = await signIn(signInEmail, signInPassword);
    
    if (error) {
      toast.error(error.message || 'Failed to sign in');
    } else {
      toast.success('Welcome back!');
    }
    
    setLoading(false);
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    const { error } = await signUp(signUpEmail, signUpPassword, signUpName);
    
    if (error) {
      toast.error(error.message || 'Failed to sign up');
    } else {
      toast.success('Account created successfully!');
    }
    
    setLoading(false);
  };

  const handleGoogleSignIn = () => {
    // Pour OAuth, utiliser le proxy Vercel (chemin relatif)
    // Le proxy Vercel redirige vers Railway
    window.location.href = '/api/v1/auth/google/start';
  };

  const handleInstagramSignIn = () => {
    window.location.href = '/api/v1/auth/instagram/start';
  };

  const handleFacebookSignIn = () => {
    window.location.href = '/api/v1/auth/facebook/start';
  };

  const handleTikTokSignIn = () => {
    window.location.href = '/api/v1/auth/tiktok/start';
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Navbar />
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-10">
          <Link to="/" className="inline-block">
            <img src="/logo.svg" alt="veyl.io" className="h-10 w-auto mx-auto" />
          </Link>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-border mb-6">
          <button
            onClick={() => setActiveTab('login')}
            className={`flex-1 py-3 text-sm font-medium transition-colors border-b-2 ${
              activeTab === 'login'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setActiveTab('register')}
            className={`flex-1 py-3 text-sm font-medium transition-colors border-b-2 ${
              activeTab === 'register'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            Register
          </button>
        </div>

        {/* Login/Register Content */}
        <div className="space-y-4">
          {/* Login Tab */}
          {activeTab === 'login' && (
            <>
              {/* Social Login Buttons - Style uniformisé avec footer */}
              <div className="text-center mb-4">
                <p className="text-sm text-muted-foreground mb-3">Sign in with:</p>
                <div className="flex justify-center gap-3 mb-2">
                  <Button
                    variant="outline"
                    size="icon"
                    className="rounded-xl border-border hover:bg-accent/50"
                    onClick={handleGoogleSignIn}
                  >
                    <svg className="h-5 w-5 text-muted-foreground hover:text-foreground" viewBox="0 0 24 24">
                      <path
                        fill="currentColor"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="currentColor"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      />
                    </svg>
                  </Button>
                  <Button 
                    variant="outline" 
                    size="icon" 
                    className="rounded-xl border-border hover:bg-accent/50 group relative"
                    onClick={handleInstagramSignIn}
                    title="Se connecter avec Instagram - Accès aux tendances et analytics"
                  >
                    <Instagram className="h-5 w-5 text-muted-foreground hover:text-foreground" />
                    <span className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 bg-popover text-popover-foreground text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-10 border">
                      Instagram Business
                    </span>
                  </Button>
                  <Button 
                    variant="outline" 
                    size="icon" 
                    className="rounded-xl border-border hover:bg-accent/50"
                    onClick={handleFacebookSignIn}
                  >
                    <Facebook className="h-5 w-5 text-muted-foreground hover:text-foreground" />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="icon" 
                    className="rounded-xl border-border hover:bg-accent/50"
                    onClick={handleTikTokSignIn}
                  >
                    <TikTokIcon className="h-5 w-5 text-muted-foreground hover:text-foreground" />
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground px-4">
                  Instagram nécessite une connexion via Facebook pour accéder aux tendances et analytics
                </p>
                <p className="text-sm text-muted-foreground mt-4">or:</p>
              </div>

              <form onSubmit={handleSignIn} className="space-y-4">
                <div className="space-y-2">
                  <Input
                    placeholder="Email address"
                    type="email"
                    value={signInEmail}
                    onChange={(e) => setSignInEmail(e.target.value)}
                    required
                    disabled={loading}
                  />
                </div>
                <div className="space-y-2">
                  <Input
                    placeholder="Password"
                    type="password"
                    value={signInPassword}
                    onChange={(e) => setSignInPassword(e.target.value)}
                    required
                    disabled={loading}
                  />
                </div>

                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <Checkbox id="remember" />
                    <label htmlFor="remember" className="text-muted-foreground cursor-pointer">
                      Remember me
                    </label>
                  </div>
                  <a href="#" className="text-primary hover:underline">
                    Forgot password?
                  </a>
                </div>

                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Signing in...
                    </>
                  ) : (
                    'Sign in'
                  )}
                </Button>

                <p className="text-center text-sm text-muted-foreground">
                  Not a member?{' '}
                  <button
                    type="button"
                    onClick={() => setActiveTab('register')}
                    className="text-primary hover:underline"
                  >
                    Register
                  </button>
                </p>
              </form>
            </>
          )}

          {/* Register Form */}
          {activeTab === 'register' && (
            <form onSubmit={handleSignUp} className="space-y-4">
              <div className="space-y-2">
                <Input
                  placeholder="Name"
                  type="text"
                  value={signUpName}
                  onChange={(e) => setSignUpName(e.target.value)}
                  required
                  disabled={loading}
                />
              </div>
              <div className="space-y-2">
                <Input
                  placeholder="Email"
                  type="email"
                  value={signUpEmail}
                  onChange={(e) => setSignUpEmail(e.target.value)}
                  required
                  disabled={loading}
                />
              </div>
              <div className="space-y-2">
                <Input
                  placeholder="Password"
                  type="password"
                  value={signUpPassword}
                  onChange={(e) => setSignUpPassword(e.target.value)}
                  required
                  disabled={loading}
                  minLength={6}
                />
              </div>

              <div className="flex items-center gap-2 text-sm">
                <Checkbox id="terms" />
                <label htmlFor="terms" className="text-muted-foreground cursor-pointer">
                  I have read and agree to the terms
                </label>
              </div>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating account...
                  </>
                ) : (
                  'Sign up'
                )}
              </Button>
            </form>
          )}
        </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
