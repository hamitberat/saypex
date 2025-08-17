import React from 'react';
import { Home, Compass, PlaySquare, Clock, ThumbsUp, Video, User, TrendingUp, Music, Gamepad2, Trophy, Film, Lightbulb, Shirt } from 'lucide-react';
import { Button } from './ui/button';
import { Separator } from './ui/separator';
import { useNavigate, useLocation } from 'react-router-dom';

const Sidebar = ({ isOpen, isMobile }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const mainMenuItems = [
    { icon: Home, label: 'Home', path: '/' },
    { icon: Compass, label: 'Explore', path: '/explore' },
    { icon: PlaySquare, label: 'Shorts', path: '/shorts' },
    { icon: Video, label: 'Subscriptions', path: '/subscriptions' },
  ];

  const libraryItems = [
    { icon: Video, label: 'Your videos', path: '/channel' },
    { icon: Clock, label: 'History', path: '/history' },
    { icon: ThumbsUp, label: 'Liked videos', path: '/liked' },
  ];

  const exploreItems = [
    { icon: TrendingUp, label: 'Trending', path: '/trending' },
    { icon: Music, label: 'Music', path: '/music' },
    { icon: Gamepad2, label: 'Gaming', path: '/gaming' },
    { icon: Trophy, label: 'Sports', path: '/sports' },
    { icon: Film, label: 'Movies', path: '/movies' },
    { icon: Lightbulb, label: 'Learning', path: '/learning' },
    { icon: Shirt, label: 'Fashion & Beauty', path: '/fashion' },
  ];

  const isActive = (path) => location.pathname === path;

  const handleNavigation = (path) => {
    navigate(path);
  };

  if (!isOpen && isMobile) return null;

  return (
    <aside className={`fixed left-0 top-14 h-[calc(100vh-56px)] bg-white border-r border-gray-200 z-40 transition-all duration-300 overflow-y-auto ${
      isOpen ? 'w-60' : 'w-16'
    } ${isMobile ? 'shadow-lg' : ''}`}>
      <div className="py-2">
        {/* Main Menu */}
        <div className="px-2">
          {mainMenuItems.map((item) => (
            <Button
              key={item.path}
              variant="ghost"
              className={`w-full justify-start px-3 py-2 mb-1 h-10 hover:bg-gray-100 ${
                isActive(item.path) ? 'bg-gray-100 font-medium' : ''
              } ${!isOpen ? 'px-4' : ''}`}
              onClick={() => handleNavigation(item.path)}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {isOpen && <span className="ml-6 text-sm">{item.label}</span>}
            </Button>
          ))}
        </div>

        {isOpen && (
          <>
            <Separator className="my-3" />
            
            {/* Library */}
            <div className="px-2">
              <div className="px-3 py-2 text-sm font-medium text-gray-700">Library</div>
              {libraryItems.map((item) => (
                <Button
                  key={item.path}
                  variant="ghost"
                  className={`w-full justify-start px-3 py-2 mb-1 h-10 hover:bg-gray-100 ${
                    isActive(item.path) ? 'bg-gray-100 font-medium' : ''
                  }`}
                  onClick={() => handleNavigation(item.path)}
                >
                  <item.icon className="w-5 h-5 flex-shrink-0" />
                  <span className="ml-6 text-sm">{item.label}</span>
                </Button>
              ))}
            </div>

            <Separator className="my-3" />

            {/* Explore */}
            <div className="px-2">
              <div className="px-3 py-2 text-sm font-medium text-gray-700">Explore</div>
              {exploreItems.map((item) => (
                <Button
                  key={item.path}
                  variant="ghost"
                  className={`w-full justify-start px-3 py-2 mb-1 h-10 hover:bg-gray-100 ${
                    isActive(item.path) ? 'bg-gray-100 font-medium' : ''
                  }`}
                  onClick={() => handleNavigation(item.path)}
                >
                  <item.icon className="w-5 h-5 flex-shrink-0" />
                  <span className="ml-6 text-sm">{item.label}</span>
                </Button>
              ))}
            </div>

            <Separator className="my-3" />

            {/* Footer */}
            <div className="px-5 py-4">
              <div className="text-xs text-gray-500 leading-relaxed">
                <div className="mb-2">
                  <a href="#" className="hover:text-gray-700">About</a> • <a href="#" className="hover:text-gray-700">Press</a> • <a href="#" className="hover:text-gray-700">Copyright</a>
                </div>
                <div className="mb-2">
                  <a href="#" className="hover:text-gray-700">Contact us</a> • <a href="#" className="hover:text-gray-700">Creators</a> • <a href="#" className="hover:text-gray-700">Advertise</a>
                </div>
                <div className="mb-2">
                  <a href="#" className="hover:text-gray-700">Developers</a> • <a href="#" className="hover:text-gray-700">Terms</a> • <a href="#" className="hover:text-gray-700">Privacy</a>
                </div>
                <div className="text-gray-400 mt-4">
                  © 2025 YouTube Clone
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