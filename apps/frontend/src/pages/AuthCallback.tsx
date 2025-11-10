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

    console.log('📥 AuthCallback - Received parameters:', { 
      hasToken: !!token, 
      hasUserId: !!userId, 
      hasEmail: !!email,
      hasName: !!name,
      error,
      errorDescription
    });

    // Handle OAuth errors
    if (error) {
      console.error('❌ OAuth error:', error, errorDescription);
      // Display error in URL for debugging, but redirect to /auth/callback with error
      // so user can see the error message on the callback page
      const errorMsg = errorDescription || error;
      console.error('Redirecting to /auth with error:', errorMsg);
      // Redirect to /auth instead of /auth/callback to display error on login page
      navigate('/auth?error=' + encodeURIComponent(errorMsg));
      return;
    }

    // If we have a token, store it immediately and redirect to / (landing page)
    // AuthContext will load the user from the token on load
    if (token) {
      // Decode token if necessary (it's URL-encoded)
      let decodedToken: string;
      try {
        decodedToken = decodeURIComponent(token);
      } catch (e) {
        // If decoding fails, use token as-is
        decodedToken = token;
      }
      
      console.log('🔑 Decoded token, length:', decodedToken.length);
      
      // Store token immediately
      localStorage.setItem('token', decodedToken);
      setToken(decodedToken);
      
      // If we also have userId/email in URL, create temporary user to avoid ProtectedRoute
      if (userId && email) {
        const decodedEmail = email ? decodeURIComponent(email) : '';
        const decodedName = name ? decodeURIComponent(name) : '';
        setUser({
          id: userId,
          email: decodedEmail,
          name: decodedName || decodedEmail.split('@')[0],
          role: 'user',
          created_at: new Date().toISOString(),
          is_active: true
        });
      }
      
      // Redirect to landing page (/)
      console.log('🚀 Redirecting to landing page');
      navigate('/');
      return;
    } else if (userId && email) {
      // Fallback: use URL parameters if token is not in URL
      // (case where token is stored differently)
      const decodedEmail = decodeURIComponent(email);
      const decodedName = name ? decodeURIComponent(name) : '';
      setUser({
        id: userId,
        email: decodedEmail,
        name: decodedName || decodedEmail.split('@')[0],
        role: 'user',
        created_at: new Date().toISOString(),
        is_active: true
      });
      setTimeout(() => {
        console.log('🚀 Redirecting to landing page (fallback userId)');
        navigate('/');
      }, 300);
    } else {
      // On error, redirect to login page
      console.error('Missing required parameters:', { token, userId, email });
      navigate('/auth?error=missing_params');
    }
  }, [searchParams, navigate, setUser, setToken]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Connecting...</p>
      </div>
    </div>
  );
}
