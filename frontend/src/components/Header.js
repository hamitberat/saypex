import React, { useState } from 'react';
import { Search, Upload, Bell, User, Menu, Video } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from './ui/button';
import { authHelpers } from '../services/api';

const Header = ({ onToggleSidebar, sidebarOpen }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const currentUser = authHelpers.getCurrentUser();
  const isAuthenticated = authHelpers.isAuthenticated();

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?search_query=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleUploadClick = () => {
    if (isAuthenticated) {
      navigate('/upload');
    } else {
      navigate('/login');
    }
  };

  const handleProfileClick = () => {
    // For now, navigate to user's channel or profile
    if (currentUser) {
      navigate(`/channel/${currentUser.username}`);
    }
  };

  const handleLogout = () => {
    authHelpers.logout();
    navigate('/');
    window.location.reload(); // Refresh to update UI state
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-purple-100 shadow-sm">
      <div className="flex items-center justify-between px-4 py-3">
        {/* Left Section - Logo and Menu */}
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggleSidebar}
            className="p-2 hover:bg-purple-50 rounded-lg"
          >
            <Menu className="w-6 h-6 text-purple-700" />
          </Button>
          
          <Link to="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl flex items-center justify-center">
              <Video className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent hidden sm:block">
              SAYPEX
            </span>
          </Link>
        </div>

        {/* Center Section - Search */}
        <div className="flex-1 max-w-2xl mx-4">
          <form onSubmit={handleSearch} className="relative">
            <div className="flex items-center">
              <div className="relative flex-1">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search videos, channels..."
                  className="w-full px-4 py-2 pr-12 border border-purple-200 rounded-l-full focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-200 bg-white"
                />
                <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-purple-400" />
              </div>
              <Button
                type="submit"
                className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-r-full border-l-0 h-10"
              >
                <Search className="w-4 h-4" />
              </Button>
            </div>
          </form>
        </div>

        {/* Right Section - Actions and User */}
        <div className="flex items-center space-x-3">
          {/* Upload Button */}
          <Button
            onClick={handleUploadClick}
            variant="ghost"
            size="sm"
            className="hidden sm:flex items-center space-x-2 px-3 py-2 text-purple-700 hover:bg-purple-50 rounded-lg transition-colors"
          >
            <Upload className="w-5 h-5" />
            <span className="hidden md:block">Upload</span>
          </Button>

          {/* Mobile Upload Button */}
          <Button
            onClick={handleUploadClick}
            variant="ghost"
            size="sm"
            className="sm:hidden p-2 text-purple-700 hover:bg-purple-50 rounded-lg"
          >
            <Upload className="w-5 h-5" />
          </Button>

          {isAuthenticated ? (
            <>
              {/* Notifications */}
              <Button
                variant="ghost"
                size="sm"
                className="p-2 text-purple-700 hover:bg-purple-50 rounded-lg relative"
              >
                <Bell className="w-5 h-5" />
                {/* Notification badge placeholder */}
                <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full text-xs text-white flex items-center justify-center">
                  3
                </span>
              </Button>

              {/* User Menu */}
              <div className="relative group">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleProfileClick}
                  className="flex items-center space-x-2 p-1 hover:bg-purple-50 rounded-lg"
                >
                  <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                  <span className="hidden md:block text-sm font-medium text-gray-700">
                    {currentUser?.username || 'User'}
                  </span>
                </Button>

                {/* Dropdown Menu */}
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                  <div className="py-2">
                    <button
                      onClick={handleProfileClick}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-purple-50 transition-colors"
                    >
                      <User className="w-4 h-4 inline mr-2" />
                      Your Channel
                    </button>
                    <button
                      onClick={() => navigate('/settings')}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-purple-50 transition-colors"
                    >
                      ⚙️ Settings
                    </button>
                    <button
                      onClick={() => navigate('/settings/2fa')}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-purple-50 transition-colors"
                    >
                      🔐 Security (2FA)
                    </button>
                    <hr className="my-2" />
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                    >
                      🚪 Sign Out
                    </button>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="flex items-center space-x-2">
              <Link to="/login">
                <Button
                  variant="outline"
                  size="sm"
                  className="px-4 py-2 border-purple-200 text-purple-700 hover:bg-purple-50 rounded-full"
                >
                  Sign In
                </Button>
              </Link>
              <Link to="/signup">
                <Button
                  size="sm"
                  className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-full"
                >
                  Sign Up
                </Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;