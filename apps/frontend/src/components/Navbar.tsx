import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useAuth } from '@/contexts/AuthContext';
import { useState } from 'react';
import { Menu, X, ChevronDown } from 'lucide-react';

export function Navbar() {
  const { user } = useAuth();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Navigation commune (toujours visible)
  const commonNavItems = [
    { path: '/docs', label: 'Documentation' },
    { path: '/enterprise', label: 'Entreprise' },
    { path: '/community', label: 'Communauté' },
  ];

  const isActive = (path: string) => location.pathname === path;
  const isProductActive = location.pathname === '/' || location.pathname === '/search' || location.pathname === '/projects';
  const isProfileActive = location.pathname === '/profile';

  return (
    <>
      <header className="sticky top-0 z-50 w-full border-b bg-background backdrop-blur-sm">
        <div className="container flex h-16 items-center justify-between px-4 md:px-8">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            <img src="/logo.svg" alt="Insider" className="h-8 w-auto" />
          </Link>

          {/* Desktop Navigation - LEFT ALIGNED with spacing */}
          <nav className="hidden lg:flex items-center gap-6 ml-8">
            {/* Product - Simple link si non connecté, menu déroulant si connecté */}
            {user ? (
              <DropdownMenu>
                <DropdownMenuTrigger className={`text-sm transition-all flex items-center gap-1 ${
                  isProductActive
                    ? 'text-white'
                    : 'text-gray-400 hover:text-white'
                }`}>
                  Product
                  <ChevronDown className="h-4 w-4" />
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start">
                  <DropdownMenuItem asChild>
                    <Link to="/search">Search</Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/projects">My projects</Link>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Link
                to="/"
                className={`text-sm transition-all ${
                  isActive('/')
                    ? 'text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Product
              </Link>
            )}

            {/* Navigation commune */}
            {commonNavItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`text-sm transition-all ${
                  isActive(item.path)
                    ? 'text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          {/* Spacer */}
          <div className="hidden lg:block flex-1" />

          {/* Desktop Actions - Profile à droite */}
          <div className="hidden lg:flex items-center gap-3">
            {user ? (
              <Link to="/profile" className={`text-sm transition-all ${
                isProfileActive
                  ? 'text-white'
                  : 'text-gray-400 hover:text-white'
              }`}>
                Profile
              </Link>
            ) : (
              <Link to="/profile" className={`text-sm transition-all ${
                isProfileActive
                  ? 'text-white'
                  : 'text-gray-400 hover:text-white'
              }`}>
                Profile
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden text-gray-400 hover:text-white transition-colors"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {/* Mobile Navigation Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-border bg-background">
            <nav className="flex flex-col py-4 px-4 gap-1">
              {/* Product */}
              {user ? (
                <>
                  <div className="py-2 px-4 text-sm font-medium text-white border-b border-border mb-1">
                    Product
                  </div>
                  <Link
                    to="/search"
                    onClick={() => setMobileMenuOpen(false)}
                    className={`py-2 px-4 text-sm transition-colors pl-8 ${
                      isActive('/search')
                        ? 'text-white font-medium'
                        : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    Search
                  </Link>
                  <Link
                    to="/projects"
                    onClick={() => setMobileMenuOpen(false)}
                    className={`py-2 px-4 text-sm transition-colors pl-8 ${
                      isActive('/projects')
                        ? 'text-white font-medium'
                        : 'text-gray-400 hover:text-white'
                    }`}
                  >
                    My projects
                  </Link>
                </>
              ) : (
                <Link
                  to="/"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`py-2 px-4 text-sm transition-colors ${
                    isActive('/')
                      ? 'text-white font-medium'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  Product
                </Link>
              )}

              {/* Navigation commune */}
              {commonNavItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`py-2 px-4 text-sm transition-colors ${
                    isActive(item.path)
                      ? 'text-white font-medium'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {item.label}
                </Link>
              ))}

              {/* Profile */}
              <Link
                to="/profile"
                onClick={() => setMobileMenuOpen(false)}
                className={`py-2 px-4 text-sm transition-colors ${
                  isProfileActive
                    ? 'text-white font-medium'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Profile
              </Link>
            </nav>
          </div>
        )}
      </header>
    </>
  );
}
