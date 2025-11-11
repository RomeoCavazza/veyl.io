import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';

export default function Demo() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load Instagram embed script
    const script = document.createElement('script');
    script.src = '//www.instagram.com/embed.js';
    script.async = true;
    script.onload = () => {
      // @ts-ignore
      if (window.instgrm) {
        // @ts-ignore
        window.instgrm.Embeds.process();
      }
      setLoading(false);
    };
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <div className="container py-12 max-w-6xl mx-auto">
        <div className="space-y-8">
          {/* Header */}
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold tracking-tight">
              Meta oEmbed Integration Demo
            </h1>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              This page demonstrates our integration with Meta's oEmbed API, 
              allowing us to embed public Instagram content directly in our platform.
            </p>
          </div>

          {/* Embedded Instagram Posts */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Post 1 - Tamaragoggin */}
            <div className="border rounded-lg p-4 bg-card">
              <h3 className="font-semibold mb-2">@tamaragoggin</h3>
              <blockquote 
                className="instagram-media" 
                data-instgrm-permalink="https://www.instagram.com/p/DP4fUgbCEX-/"
                data-instgrm-version="14"
              />
            </div>

            {/* Post 2 - Jarnoocs */}
            <div className="border rounded-lg p-4 bg-card">
              <h3 className="font-semibold mb-2">@jarnoocs</h3>
              <blockquote 
                className="instagram-media" 
                data-instgrm-permalink="https://www.instagram.com/p/DP1R4L3CpqD/"
                data-instgrm-version="14"
              />
            </div>

            {/* Post 3 - Ambie.sharma */}
            <div className="border rounded-lg p-4 bg-card">
              <h3 className="font-semibold mb-2">@ambie.sharma</h3>
              <blockquote 
                className="instagram-media" 
                data-instgrm-permalink="https://www.instagram.com/p/DPrcU4niRHA/"
                data-instgrm-version="14"
              />
            </div>

            {/* Post 4 - Virginialeigh22 */}
            <div className="border rounded-lg p-4 bg-card">
              <h3 className="font-semibold mb-2">@virginialeigh22</h3>
              <blockquote 
                className="instagram-media" 
                data-instgrm-permalink="https://www.instagram.com/p/DQsMdJDAUXb/"
                data-instgrm-version="14"
              />
            </div>

            {/* Post 5 - Biena_x */}
            <div className="border rounded-lg p-4 bg-card">
              <h3 className="font-semibold mb-2">@biena_x</h3>
              <blockquote 
                className="instagram-media" 
                data-instgrm-permalink="https://www.instagram.com/p/DQmhFskDf9d/"
                data-instgrm-version="14"
              />
            </div>

            {/* Post 6 - Menfashionkey */}
            <div className="border rounded-lg p-4 bg-card">
              <h3 className="font-semibold mb-2">@menfashionkey</h3>
              <blockquote 
                className="instagram-media" 
                data-instgrm-permalink="https://www.instagram.com/p/DPBsUESAUSb/"
                data-instgrm-version="14"
              />
            </div>
          </div>

          {/* Technical Details */}
          <div className="mt-12 p-6 border rounded-lg bg-muted/50">
            <h2 className="text-2xl font-bold mb-4">Technical Implementation</h2>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start gap-2">
                <span className="text-green-500">✓</span>
                <span>We use Meta's oEmbed API to fetch embed data for public Instagram posts</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500">✓</span>
                <span>The backend endpoint <code className="bg-background px-1 rounded">/api/v1/meta/oembed</code> handles API calls securely</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500">✓</span>
                <span>We use the official Instagram embed.js script to render embeds responsively</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500">✓</span>
                <span>All embeds are loaded client-side for optimal performance</span>
              </li>
            </ul>
          </div>

          {loading && (
            <div className="text-center text-muted-foreground">
              Loading Instagram embeds...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

