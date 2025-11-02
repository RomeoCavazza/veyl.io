import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

export default function AuthCallback() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { setUser, setToken } = useAuth();

  useEffect(() => {
    const token = searchParams.get('token');
    const userId = searchParams.get('user_id');
    const email = searchParams.get('email');
    const name = searchParams.get('name');
    const error = searchParams.get('error');
    const errorDescription = searchParams.get('error_description');

    console.log('📥 AuthCallback - Paramètres reçus:', { 
      hasToken: !!token, 
      hasUserId: !!userId, 
      hasEmail: !!email,
      hasName: !!name,
      error,
      errorDescription
    });

    // Gérer les erreurs OAuth
    if (error) {
      console.error('❌ OAuth error:', error, errorDescription);
      // Afficher l'erreur dans l'URL pour debugging, mais rediriger vers /auth/callback avec l'erreur
      // pour que l'utilisateur puisse voir le message d'erreur sur la page de callback
      const errorMsg = errorDescription || error;
      console.error('Redirection vers /auth avec erreur:', errorMsg);
      // Rediriger vers /auth au lieu de /auth/callback pour afficher l'erreur sur la page de connexion
      navigate('/auth?error=' + encodeURIComponent(errorMsg));
      return;
    }

    // Si on a un token, stocker immédiatement et rediriger vers / (landing page)
    // Le AuthContext chargera le user depuis le token au chargement
    if (token) {
      // Décoder le token si nécessaire (il est URL-encodé)
      let decodedToken: string;
      try {
        decodedToken = decodeURIComponent(token);
      } catch (e) {
        // Si le décodage échoue, utiliser le token tel quel
        decodedToken = token;
      }
      
      console.log('🔑 Token décodé, longueur:', decodedToken.length);
      
      // Stocker le token immédiatement
      localStorage.setItem('token', decodedToken);
      setToken(decodedToken);
      
      // Si on a aussi userId/email dans l'URL, créer un user temporaire pour éviter ProtectedRoute
      if (userId && email) {
        const decodedEmail = email ? decodeURIComponent(email) : '';
        const decodedName = name ? decodeURIComponent(name) : '';
        setUser({
          id: parseInt(userId),
          email: decodedEmail,
          name: decodedName || decodedEmail.split('@')[0],
          role: 'user',
          created_at: new Date().toISOString(),
          is_active: true
        });
      }
      
      // Rediriger vers la landing page (/)
      console.log('🚀 Redirection vers landing page');
      navigate('/');
      return;
    } else if (userId && email) {
      // Fallback: utiliser les paramètres URL si le token n'est pas dans l'URL
      // (cas où on stocke le token différemment)
      const decodedEmail = decodeURIComponent(email);
      const decodedName = name ? decodeURIComponent(name) : '';
      setUser({
        id: parseInt(userId),
        email: decodedEmail,
        name: decodedName || decodedEmail.split('@')[0],
        role: 'user',
        created_at: new Date().toISOString(),
        is_active: true
      });
      setTimeout(() => {
        console.log('🚀 Redirection vers landing page (fallback userId)');
        navigate('/');
      }, 300);
    } else {
      // En cas d'erreur, rediriger vers la page de connexion
      console.error('Missing required parameters:', { token, userId, email });
      navigate('/auth?error=missing_params');
    }
  }, [searchParams, navigate, setUser, setToken]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Connexion en cours...</p>
      </div>
    </div>
  );
}
