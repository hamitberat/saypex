import React, { useState } from 'react';
import { Search, Mic, Menu, Video, Bell, User, LogIn, UserPlus } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { useNavigate } from 'react-router-dom';
import { authHelpers } from '../services/api';

const Header = ({ onMenuClick, onSearch, searchQuery, setSearchQuery }) => {
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const navigate = useNavigate();
  const currentUser = authHelpers.getCurrentUser();

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearch(searchQuery);
      navigate(`/results?search_query=${encodeURIComponent(searchQuery)}`);
    }
  };

  const handleLogin = () => {
    navigate('/login');
  };

  const handleSignup = () => {
    navigate('/signup');
  };

  const handleLogout = () => {
    authHelpers.logout();
    window.location.reload();
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-purple-100 shadow-sm">
      <div className="flex items-center justify-between px-4 py-2 h-14">
        {/* Left section */}
        <div className="flex items-center space-x-4">
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={onMenuClick}
            className="p-2 hover:bg-purple-50 rounded-full transition-colors"
          >
            <Menu className="w-5 h-5 text-gray-700" />
          </Button>
          <div 
            className="flex items-center space-x-2 cursor-pointer group"
            onClick={() => navigate('/')}
          >
            <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl flex items-center justify-center group-hover:scale-105 transition-transform duration-200">
              <Video className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              SAYPEX
            </span>
          </div>
        </div>

        {/* Center section - Search */}
        <div className="flex-1 max-w-2xl mx-4">
          <form onSubmit={handleSearch} className="flex items-center">
            <div className={`flex items-center flex-1 border-2 rounded-l-full overflow-hidden transition-all duration-200 ${
              isSearchFocused ? 'border-purple-400 shadow-sm ring-1 ring-purple-200' : 'border-gray-200'
            }`}>
              <Input
                type="text"
                placeholder="Search videos, channels..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setIsSearchFocused(true)}
                onBlur={() => setIsSearchFocused(false)}
                className="border-none focus:ring-0 px-4 py-2 text-base bg-white font-normal"
              />
            </div>
            <Button 
              type="submit"
              className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 border-2 border-l-0 border-purple-400 rounded-r-full px-6 py-2 h-10 text-white transition-all duration-200"
            >
              <Search className="w-5 h-5" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="ml-2 p-2 hover:bg-purple-50 rounded-full transition-colors"
            >
              <Mic className="w-5 h-5 text-gray-600" />
            </Button>
          </form>
        </div>

        {/* Right section */}
        <div className="flex items-center space-x-2">
          {currentUser ? (
            <>
              <Button 
                variant="ghost" 
                size="sm" 
                className="p-2 hover:bg-purple-50 rounded-full transition-colors"
                onClick={() => navigate('/upload')}
              >
                <Video className="w-5 h-5 text-gray-600" />
              </Button>
              <Button 
                variant="ghost" 
                size="sm" 
                className="p-2 hover:bg-purple-50 rounded-full transition-colors"
              >
                <Bell className="w-5 h-5 text-gray-600" />
              </Button>
              <div className="flex items-center space-x-3">
                <img
                  src={currentUser.avatar_url || 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=32&h=32&fit=crop&crop=face'}
                  alt={currentUser.username}
                  className="w-8 h-8 rounded-full object-cover ring-2 ring-purple-200"
                />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className="text-sm text-gray-600 hover:text-purple-600 transition-colors"
                >
                  Logout
                </Button>
              </div>
            </>
          ) : (
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogin}
                className="flex items-center space-x-2 px-4 py-2 hover:bg-purple-50 rounded-full transition-colors"
              >
                <LogIn className="w-4 h-4" />
                <span>Sign In</span>
              </Button>
              <Button
                onClick={handleSignup}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-full transition-all duration-200"
              >
                <UserPlus className="w-4 h-4" />
                <span>Sign Up</span>
              </Button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;