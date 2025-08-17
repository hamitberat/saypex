import React, { useState } from 'react';
import { Search, Mic, Menu, Video, Bell, User } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { useNavigate } from 'react-router-dom';

const Header = ({ onMenuClick, onSearch, searchQuery, setSearchQuery }) => {
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearch(searchQuery);
      navigate(`/results?search_query=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200">
      <div className="flex items-center justify-between px-4 py-2 h-14">
        {/* Left section */}
        <div className="flex items-center space-x-4">
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={onMenuClick}
            className="p-2 hover:bg-gray-100 rounded-full"
          >
            <Menu className="w-5 h-5" />
          </Button>
          <div 
            className="flex items-center space-x-1 cursor-pointer"
            onClick={() => navigate('/')}
          >
            <div className="w-8 h-8 bg-red-600 rounded flex items-center justify-center">
              <Video className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">
              You<span className="text-red-600">Tube</span>
            </span>
          </div>
        </div>

        {/* Center section - Search */}
        <div className="flex-1 max-w-2xl mx-4">
          <form onSubmit={handleSearch} className="flex items-center">
            <div className={`flex items-center flex-1 border rounded-l-full overflow-hidden transition-all duration-200 ${
              isSearchFocused ? 'border-blue-500 shadow-sm' : 'border-gray-300'
            }`}>
              <Input
                type="text"
                placeholder="Search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => setIsSearchFocused(true)}
                onBlur={() => setIsSearchFocused(false)}
                className="border-none focus:ring-0 px-4 py-2 text-base bg-white"
              />
            </div>
            <Button 
              type="submit"
              className="bg-gray-50 hover:bg-gray-100 border border-l-0 border-gray-300 rounded-r-full px-6 py-2 h-10"
              variant="ghost"
            >
              <Search className="w-5 h-5 text-gray-600" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="ml-2 p-2 hover:bg-gray-100 rounded-full"
            >
              <Mic className="w-5 h-5 text-gray-600" />
            </Button>
          </form>
        </div>

        {/* Right section */}
        <div className="flex items-center space-x-2">
          <Button 
            variant="ghost" 
            size="sm" 
            className="p-2 hover:bg-gray-100 rounded-full"
          >
            <Video className="w-5 h-5 text-gray-600" />
          </Button>
          <Button 
            variant="ghost" 
            size="sm" 
            className="p-2 hover:bg-gray-100 rounded-full"
          >
            <Bell className="w-5 h-5 text-gray-600" />
          </Button>
          <Button 
            variant="ghost" 
            size="sm" 
            className="p-2 hover:bg-gray-100 rounded-full"
          >
            <User className="w-6 h-6 text-gray-600" />
          </Button>
        </div>
      </div>
    </header>
  );
};

export default Header;