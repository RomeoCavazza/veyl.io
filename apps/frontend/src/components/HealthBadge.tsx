import { useEffect, useState } from 'react';
import { Badge } from './ui/badge';
import { Activity } from 'lucide-react';

export function HealthBadge() {
  const [status, setStatus] = useState<'checking' | 'healthy' | 'down'>('checking');

  useEffect(() => {
    // Utiliser getApiBase pour forcer HTTPS
    const getApiBase = (): string => {
      if (import.meta.env.DEV) {
        return '';
      }
      const envUrl = import.meta.env.VITE_API_URL;
      if (envUrl) {
        const url = envUrl.startsWith('http://') 
          ? envUrl.replace('http://', 'https://') 
          : envUrl;
        return url.startsWith('https://') ? url : `https://${url}`;
      }
      return 'https://api.veyl.io';
    };
    
    const apiBase = getApiBase();
    
    const checkHealth = async () => {
      try {
        const url = `${apiBase}/api/healthz`;
        // S'assurer que l'URL est en HTTPS en production
        const finalUrl = !import.meta.env.DEV && !url.startsWith('https://')
          ? url.replace('http://', 'https://')
          : url;
        const response = await fetch(finalUrl, { mode: 'cors', credentials: 'omit' });
        setStatus(response.ok ? 'healthy' : 'down');
      } catch {
        setStatus('down');
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const getVariant = () => {
    switch (status) {
      case 'healthy': return 'secondary';
      case 'down': return 'destructive';
      default: return 'outline';
    }
  };

  const getText = () => {
    switch (status) {
      case 'healthy': return 'API OK';
      case 'down': return 'API Off';
      default: return 'Health...';
    }
  };

  return (
    <Badge
      variant={getVariant()}
      className="gap-1.5 text-xs"
      title={status === 'healthy' ? 'Backend opérationnel' : 'Backend non disponible'}
    >
      <Activity className="h-3 w-3" />
      {getText()}
    </Badge>
  );
}
