import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Loader2 } from 'lucide-react';

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Ne rediriger que si le loading est terminé ET qu'il n'y a pas de token
    if (!loading && !user) {
      const token = localStorage.getItem('token');
      if (!token) {
        if (import.meta.env.DEV) {
          console.log('🔒 ProtectedRoute: No token found, redirecting to /auth');
        }
        // Sauvegarder la page demandée pour rediriger après login
        sessionStorage.setItem('redirectAfterLogin', location.pathname + location.search);
        navigate('/auth');
      } else {
        if (import.meta.env.DEV) {
          console.log('⚠️ ProtectedRoute: Token exists but no user. Waiting for AuthContext to load...');
        }
        // Token existe mais user est null - attendre un peu plus pour laisser le temps au AuthContext de charger
        // Ne pas rediriger immédiatement, attendre que le contexte charge
        const timer = setTimeout(() => {
          // Si après 2 secondes user est toujours null malgré le token, vérifier à nouveau
          if (!user && token) {
            if (import.meta.env.DEV) {
              console.log('⚠️ ProtectedRoute: User still null after delay, token might be invalid');
            }
            // Ne pas rediriger automatiquement, laisser AuthContext gérer
          }
        }, 2000);
        return () => clearTimeout(timer);
      }
    }
  }, [user, loading, navigate, location]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return <>{children}</>;
}
