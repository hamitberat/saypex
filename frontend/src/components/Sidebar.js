import React from 'react';
import { Home, Compass, PlaySquare, Clock, ThumbsUp, Video, User, TrendingUp, Music, Gamepad2, Trophy, Film, Lightbulb, Shirt, Plus, Users, Settings, HelpCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Separator } from './ui/separator';
import { useNavigate, useLocation } from 'react-router-dom';
import { authHelpers } from '../services/api';

const Sidebar = ({ isOpen, isMobile }) => {
  const navigate = useNavigate();
  const location = useLocation();
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
    { icon: Plus, label: 'Upload Video', path: '/upload' },
  ] : [];

  const subscriptionItems = currentUser ? [
    { icon: Users, label: 'Subscriptions', path: '/subscriptions' },
  ] : [];

  const exploreItems = [
    { icon: Music, label: 'Music', path: '/', category: 'music' },
    { icon: Gamepad2, label: 'Gaming', path: '/', category: 'gaming' },
    { icon: Trophy, label: 'Sports', path: '/', category: 'sports' },
    { icon: Film, label: 'Movies', path: '/', category: 'movies' },
    { icon: Lightbulb, label: 'Learning', path: '/', category: 'learning' },
    { icon: Shirt, label: 'Fashion & Beauty', path: '/', category: 'fashion' },
  ];

  const settingsItems = [
    { icon: Settings, label: 'Settings', path: '/settings' },
    { icon: HelpCircle, label: 'Help', path: '/help' },
  ];

  const isActive = (path) => location.pathname === path;

  const handleNavigation = (path, category = null) => {
    if (category) {
      // Navigate to home with category filter
      navigate(`/?category=${category}`);
    } else {
      navigate(path);
    }
  };

  if (!isOpen && isMobile) return null;

  return (
    <aside className={`fixed left-0 top-14 h-[calc(100vh-56px)] bg-white border-r border-purple-100 z-40 transition-all duration-300 overflow-y-auto ${
      isOpen ? 'w-60' : 'w-16'
    } ${isMobile ? 'shadow-lg' : ''}`}>
      <div className="py-2">
        {/* Main Menu */}
        <div className="px-2">
          {mainMenuItems.map((item) => (
            <Button
              key={item.path}
              variant="ghost"
              className={`w-full justify-start px-3 py-2 mb-1 h-10 transition-all duration-200 ${
                isActive(item.path) 
                  ? 'bg-gradient-to-r from-purple-100 to-blue-100 text-purple-700 font-medium border-r-2 border-purple-500' 
                  : 'hover:bg-purple-50 text-gray-700'
              } ${!isOpen ? 'px-4 justify-center' : ''}`}
              onClick={() => handleNavigation(item.path)}
            >
              <item.icon className={`w-5 h-5 flex-shrink-0 ${isActive(item.path) ? 'text-purple-600' : ''}`} />
              {isOpen && <span className="ml-6 text-sm">{item.label}</span>}
            </Button>
          ))}
        </div>

        {isOpen && (
          <>
            {/* Subscriptions */}
            {currentUser && subscriptionItems.length > 0 && (
              <>
                <Separator className="my-3 bg-purple-100" />
                <div className="px-2">
                  {subscriptionItems.map((item) => (
                    <Button
                      key={item.path}
                      variant="ghost"
                      className={`w-full justify-start px-3 py-2 mb-1 h-10 transition-all duration-200 ${
                        isActive(item.path) 
                          ? 'bg-gradient-to-r from-purple-100 to-blue-100 text-purple-700 font-medium border-r-2 border-purple-500' 
                          : 'hover:bg-purple-50 text-gray-700'
                      }`}
                      onClick={() => handleNavigation(item.path)}
                    >
                      <item.icon className={`w-5 h-5 flex-shrink-0 ${isActive(item.path) ? 'text-purple-600' : ''}`} />
                      <span className="ml-6 text-sm">{item.label}</span>
                    </Button>
                  ))}
                </div>
              </>
            )}
            
            {/* Library */}
            {currentUser && libraryItems.length > 0 && (
              <>
                <Separator className="my-3 bg-purple-100" />
                <div className="px-2">
                  <div className="px-3 py-2 text-sm font-medium text-purple-700">Library</div>
                  {libraryItems.map((item) => (
                    <Button
                      key={item.path}
                      variant="ghost"
                      className={`w-full justify-start px-3 py-2 mb-1 h-10 transition-all duration-200 ${
                        isActive(item.path) 
                          ? 'bg-gradient-to-r from-purple-100 to-blue-100 text-purple-700 font-medium border-r-2 border-purple-500' 
                          : 'hover:bg-purple-50 text-gray-700'
                      }`}
                      onClick={() => handleNavigation(item.path)}
                    >
                      <item.icon className={`w-5 h-5 flex-shrink-0 ${isActive(item.path) ? 'text-purple-600' : ''}`} />
                      <span className="ml-6 text-sm">{item.label}</span>
                    </Button>
                  ))}
                </div>
              </>
            )}

            <Separator className="my-3 bg-purple-100" />

            {/* Explore */}
            <div className="px-2">
              <div className="px-3 py-2 text-sm font-medium text-purple-700">Explore</div>
              {exploreItems.map((item) => (
                <Button
                  key={item.path}
                  variant="ghost"
                  className={`w-full justify-start px-3 py-2 mb-1 h-10 transition-all duration-200 ${
                    isActive(item.path) 
                      ? 'bg-gradient-to-r from-purple-100 to-blue-100 text-purple-700 font-medium border-r-2 border-purple-500' 
                      : 'hover:bg-purple-50 text-gray-700'
                  }`}
                  onClick={() => handleNavigation(item.path)}
                >
                  <item.icon className={`w-5 h-5 flex-shrink-0 ${isActive(item.path) ? 'text-purple-600' : ''}`} />
                  <span className="ml-6 text-sm">{item.label}</span>
                </Button>
              ))}
            </div>

            <Separator className="my-3 bg-purple-100" />

            {/* Settings */}
            <div className="px-2">
              {settingsItems.map((item) => (
                <Button
                  key={item.path}
                  variant="ghost"
                  className={`w-full justify-start px-3 py-2 mb-1 h-10 transition-all duration-200 ${
                    isActive(item.path) 
                      ? 'bg-gradient-to-r from-purple-100 to-blue-100 text-purple-700 font-medium border-r-2 border-purple-500' 
                      : 'hover:bg-purple-50 text-gray-700'
                  }`}
                  onClick={() => handleNavigation(item.path)}
                >
                  <item.icon className={`w-5 h-5 flex-shrink-0 ${isActive(item.path) ? 'text-purple-600' : ''}`} />
                  <span className="ml-6 text-sm">{item.label}</span>
                </Button>
              ))}
            </div>

            {/* Footer */}
            <div className="px-5 py-4">
              <div className="text-xs text-gray-500 leading-relaxed">
                <div className="mb-2">
                  <a href="#" className="hover:text-purple-600 transition-colors">About</a> • <a href="#" className="hover:text-purple-600 transition-colors">Press</a> • <a href="#" className="hover:text-purple-600 transition-colors">Copyright</a>
                </div>
                <div className="mb-2">
                  <a href="#" className="hover:text-purple-600 transition-colors">Contact us</a> • <a href="#" className="hover:text-purple-600 transition-colors">Creators</a> • <a href="#" className="hover:text-purple-600 transition-colors">Advertise</a>
                </div>
                <div className="mb-2">
                  <a href="#" className="hover:text-purple-600 transition-colors">Developers</a> • <a href="#" className="hover:text-purple-600 transition-colors">Terms</a> • <a href="#" className="hover:text-purple-600 transition-colors">Privacy</a>
                </div>
                <div className="text-purple-400 mt-4 font-medium">
                  © 2025 SAYPEX
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;