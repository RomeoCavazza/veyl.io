import { useState } from 'react';
import { Globe, Mic, X, Instagram } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';

interface AISearchBarProps {
  onSearch?: (query: string, platforms: string[]) => void;
}

const platforms = [
  { id: 'instagram', name: 'Instagram', icon: Instagram },
  { id: 'tiktok', name: 'TikTok', icon: Globe },
  { id: 'x', name: 'X', icon: Globe },
];

export function AISearchBar({ onSearch }: AISearchBarProps) {
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [query, setQuery] = useState('');

  const togglePlatform = (platformId: string) => {
    setSelectedPlatforms(prev =>
      prev.includes(platformId)
        ? prev.filter(id => id !== platformId)
        : [...prev, platformId]
    );
  };

  const clearFilters = () => {
    setSelectedPlatforms([]);
  };

  const handleSearch = () => {
    if (query.trim() && onSearch) {
      onSearch(query.trim(), selectedPlatforms);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="relative flex flex-col gap-3 p-4 rounded-2xl bg-card shadow-elegant hover:shadow-glow transition-all">
        {/* Search Input Row */}
        <div className="flex items-center gap-3">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Search trends, hashtags, creators..."
            className="flex-1 !border-0 border-none bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 text-base h-12 outline-none"
          />
          <Button 
            variant="ghost" 
            size="icon"
            className="h-10 w-10 rounded-xl hover:bg-accent"
          >
            <Mic className="h-5 w-5" />
          </Button>
        </div>

        {/* Options Row */}
        <div className="flex items-center gap-2">
          <Popover>
            <PopoverTrigger asChild>
              <Button 
                variant="ghost" 
                size="sm"
                className="h-9 rounded-xl hover:bg-accent"
              >
                {selectedPlatforms.length > 0 ? (
                  <>
                    <X className="h-4 w-4 mr-2" onClick={(e) => { e.stopPropagation(); clearFilters(); }} />
                    {selectedPlatforms.map(id => platforms.find(p => p.id === id)?.name).join(', ')}
                  </>
                ) : (
                  <>
                    <Globe className="h-4 w-4 mr-2" />
                    Platform
                  </>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-64 p-2" align="start">
              <div className="space-y-1">
                {platforms.map((platform) => (
                  <button
                    key={platform.id}
                    onClick={() => togglePlatform(platform.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-accent transition-colors ${
                      selectedPlatforms.includes(platform.id) ? 'bg-accent' : ''
                    }`}
                  >
                    <platform.icon className="h-5 w-5 text-primary" />
                    <span className="text-sm font-medium">{platform.name}</span>
                  </button>
                ))}
              </div>
            </PopoverContent>
          </Popover>
        </div>
      </div>
    </div>
  );
}
