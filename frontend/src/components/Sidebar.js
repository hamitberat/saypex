import React from 'react';
import { Home, Compass, PlaySquare, Clock, ThumbsUp, Video, User, TrendingUp, Gamepad2, ChefHat, Coffee, Calendar, Users, Settings, HelpCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Separator } from './ui/separator';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { authHelpers } from '../services/api';

const Sidebar = ({ isOpen, isMobile }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const currentUser = authHelpers.getCurrentUser();

  const mainMenuItems = [
    { icon: Home, label: 'Home', path: '/' },
    { icon: TrendingUp, label: 'Trending', path: '/trending' },
    { icon: Compass, label: 'Explore', path: '/explore' },
    { icon: PlaySquare, label: 'Shorts', path: '/shorts' },
  ];

  const libraryItems = currentUser ? [
    { icon: Video, label: 'Your videos', path: '/channel' },
    { icon: Clock, label: 'History', path: '/history' },
    { icon: ThumbsUp, label: 'Liked videos', path: '/liked' },
  ] : [];

  const subscriptionItems = currentUser ? [
    { icon: Users, label: 'Subscriptions', path: '/subscriptions' },
  ] : [];

  const exploreItems = [
    { icon: TrendingUp, label: 'Trending', path: '/', category: 'trending' },
    { icon: Gamepad2, label: 'Gaming', path: '/', category: 'gaming' },
    { icon: ChefHat, label: 'Cooking', path: '/', category: 'cooking' },
    { icon: Coffee, label: 'Mukbang', path: '/', category: 'mukbang' },
    { icon: Calendar, label: 'Daily', path: '/', category: 'daily' },
  ];

  const settingsItems = [
    { icon: Settings, label: 'Settings', path: '/settings' },
    { icon: HelpCircle, label: 'Help', path: '/help' },
  ];

  const isActive = (path, category = null) => {
    if (category) {
      // For category-based items, check if we're on home page with the right category
      const currentCategory = searchParams.get('category');
      return location.pathname === '/' && currentCategory === category;
    }
    
    // For regular items, check path match
    if (path === '/') {
      // Home is active when on root path with no category parameters
      return location.pathname === '/' && !searchParams.get('category');
    }
    
    return location.pathname === path;
  };

  const handleNavigation = (path, category = null) => {
    if (category) {
      // Navigate to home with category filter
      navigate(`/?category=${category}`);
    } else if (path === '/') {
      // Navigate to home and clear any category parameters
      navigate('/', { replace: true });
    } else {
      navigate(path);
    }
  };

  // Always render sidebar as icon-only permanent sidebar

  return (
    <aside className="fixed left-0 top-14 h-[calc(100vh-56px)] bg-white border-r border-purple-100 z-40 overflow-y-auto w-16 shadow-sm">
      <div className="py-2">
        {/* Main Menu - Icons Only */}
        <div className="px-2">
          {mainMenuItems.map((item) => (
            <Button
              key={item.path}
              variant="ghost"
              className={`w-full justify-center px-3 py-2 mb-1 h-12 transition-all duration-200 ${
                isActive(item.path) 
                  ? 'bg-gradient-to-r from-pink-100 to-blue-100 text-pink-700 font-medium border-r-2 border-pink-500' 
                  : 'hover:bg-pink-50 text-gray-700'
              }`}
              onClick={() => handleNavigation(item.path)}
              title={item.label}
            >
              <item.icon className={`w-6 h-6 flex-shrink-0 ${isActive(item.path) ? 'text-pink-600' : ''}`} />
            </Button>
          ))}
        </div>

        {/* User Library - Icons Only */}
        {currentUser && libraryItems.length > 0 && (
          <>
            <Separator className="my-3 bg-purple-100" />
            <div className="px-2">
              {libraryItems.map((item) => (
                <Button
                  key={item.path}
                  variant="ghost"
                  className={`w-full justify-center px-3 py-2 mb-1 h-12 transition-all duration-200 ${
                    isActive(item.path) 
                      ? 'bg-gradient-to-r from-purple-100 to-blue-100 text-purple-700 font-medium border-r-2 border-purple-500' 
                      : 'hover:bg-purple-50 text-gray-700'
                  }`}
                  onClick={() => handleNavigation(item.path)}
                  title={item.label}
                >
                  <item.icon className={`w-6 h-6 flex-shrink-0 ${isActive(item.path) ? 'text-pink-600' : ''}`} />
                </Button>
              ))}
            </div>
          </>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;