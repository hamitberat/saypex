import React, { useState } from 'react';
import { Search, Upload, Bell, User, Video, ChevronDown } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from './ui/button';
import { authHelpers } from '../services/api';

const Header = ({ sidebarOpen }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const navigate = useNavigate();
  const currentUser = authHelpers.getCurrentUser();
  const isAuthenticated = authHelpers.isAuthenticated();

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?search_query=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  // Close profile menu when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileMenuOpen && !event.target.closest('.profile-dropdown')) {
        setProfileMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [profileMenuOpen]);

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
        {/* Left Section - Logo Only */}
        <div className="flex items-center">
          <Link to="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
            <div className="w-10 h-10 bg-gradient-to-r from-pink-500 to-blue-500 rounded-xl flex items-center justify-center">
              <div className="w-0 h-0 border-l-[12px] border-l-white border-y-[6px] border-y-transparent ml-1"></div>
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-pink-600 to-blue-600 bg-clip-text text-transparent hidden sm:block">
              Lotic
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
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleSearch(e);
                    }
                  }}
                  placeholder="Search videos, channels..."
                  className="w-full px-4 py-2 pr-4 border border-pink-200 rounded-l-full focus:outline-none focus:border-pink-400 focus:ring-1 focus:ring-pink-200 bg-white"
                />
              </div>
              <Button
                type="submit"
                className="px-6 py-2 bg-gradient-to-r from-pink-600 to-blue-600 hover:from-pink-700 hover:to-blue-700 text-white rounded-r-full border-l-0 h-10"
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

              {/* Profile Dropdown */}
              <div className="relative profile-dropdown">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setProfileMenuOpen(!profileMenuOpen)}
                  className="flex items-center space-x-2 p-1 hover:bg-purple-50 rounded-lg"
                >
                  <div className="w-8 h-8 bg-gradient-to-br from-pink-500 to-blue-500 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-white" />
                  </div>
                  <span className="hidden md:block text-sm font-medium text-gray-700">
                    {currentUser?.username || 'User'}
                  </span>
                  <ChevronDown className="w-4 h-4 text-gray-500" />
                </Button>

                {/* Profile Dropdown Menu */}
                {profileMenuOpen && (
                  <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                    <div className="py-2">
                      {/* User Info Section */}
                      <div className="px-4 py-3 border-b border-gray-100">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-pink-500 to-blue-500 rounded-full flex items-center justify-center">
                            <User className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">{currentUser?.username || 'User'}</div>
                            <div className="text-sm text-gray-500">{currentUser?.email}</div>
                          </div>
                        </div>
                      </div>

                      {/* Menu Options */}
                      <button
                        onClick={() => {
                          navigate(`/channel/${currentUser?.username}`);
                          setProfileMenuOpen(false);
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-pink-50 transition-colors flex items-center"
                      >
                        <User className="w-4 h-4 mr-3" />
                        Your Channel
                      </button>
                      <button
                        onClick={() => {
                          navigate('/settings');
                          setProfileMenuOpen(false);
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-purple-50 transition-colors"
                      >
                        ⚙️ Settings
                      </button>
                      <button
                        onClick={() => {
                          navigate('/settings/2fa');
                          setProfileMenuOpen(false);
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-purple-50 transition-colors"
                      >
                        🔐 Security (2FA)
                      </button>
                      <hr className="my-2" />
                      <button
                        onClick={() => {
                          handleLogout();
                          setProfileMenuOpen(false);
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                      >
                        🚪 Sign Out
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </>
          ) : (
            /* Profile Dropdown for Non-Authenticated Users */
            <div className="relative profile-dropdown">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setProfileMenuOpen(!profileMenuOpen)}
                className="flex items-center space-x-2 p-2 hover:bg-purple-50 rounded-lg"
              >
                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-gray-600" />
                </div>
                <ChevronDown className="w-4 h-4 text-gray-500" />
              </Button>

              {/* Non-Auth Dropdown Menu */}
              {profileMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                  <div className="py-2">
                    <Link to="/login" onClick={() => setProfileMenuOpen(false)}>
                      <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-purple-50 transition-colors">
                        🔑 Sign In
                      </button>
                    </Link>
                    <Link to="/signup" onClick={() => setProfileMenuOpen(false)}>
                      <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-purple-50 transition-colors">
                        ✨ Sign Up
                      </button>
                    </Link>
                    <hr className="my-2" />
                    <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-purple-50 transition-colors">
                      ❓ Help
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;