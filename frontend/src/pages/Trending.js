import React, { useState, useEffect } from 'react';
import VideoCard from '../components/VideoCard';
import { Button } from '../components/ui/button';
import { Flame, Music, Gamepad2, Film, TrendingUp } from 'lucide-react';
import { mockTrendingVideos } from '../mock/mockData';

const Trending = ({ sidebarOpen }) => {
  const [videos, setVideos] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('Now');
  const [loading, setLoading] = useState(true);

  const categories = [
    { name: 'Now', icon: Flame },
    { name: 'Music', icon: Music },
    { name: 'Gaming', icon: Gamepad2 },
    { name: 'Movies', icon: Film },
  ];

  useEffect(() => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setVideos(mockTrendingVideos);
      setLoading(false);
    }, 500);
  }, [selectedCategory]);

  if (loading) {
    return (
      <div className={`pt-14 transition-all duration-300 ${sidebarOpen ? 'ml-60' : 'ml-16'}`}>
        <div className="p-6">
          <div className="space-y-4">
            {[...Array(10)].map((_, index) => (
              <div key={index} className="animate-pulse flex space-x-4">
                <div className="w-40 h-24 bg-gray-200 rounded-lg flex-shrink-0"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-3/4 mb-1"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`pt-14 transition-all duration-300 ${sidebarOpen ? 'ml-60' : 'ml-16'}`}>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center space-x-3 mb-6">
          <TrendingUp className="w-8 h-8 text-red-600" />
          <h1 className="text-2xl font-bold">Trending</h1>
        </div>

        {/* Category Tabs */}
        <div className="flex items-center space-x-1 mb-8 border-b border-gray-200">
          {categories.map((category) => (
            <Button
              key={category.name}
              variant="ghost"
              className={`flex items-center space-x-2 px-6 py-3 border-b-2 transition-all duration-200 ${
                selectedCategory === category.name
                  ? 'border-black text-black font-medium'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
              onClick={() => setSelectedCategory(category.name)}
            >
              <category.icon className="w-4 h-4" />
              <span>{category.name}</span>
            </Button>
          ))}
        </div>

        {/* Trending Videos List */}
        <div className="space-y-4">
          {videos.map((video, index) => (
            <div key={video.id} className="flex items-start space-x-4 p-3 hover:bg-gray-50 rounded-lg transition-colors duration-200">
              <div className="flex-shrink-0 text-lg font-bold text-gray-400 w-8 text-center">
                {index + 1}
              </div>
              <div className="relative flex-shrink-0">
                <img
                  src={video.thumbnail}
                  alt={video.title}
                  className="w-40 h-24 object-cover rounded-lg"
                />
                <div className="absolute bottom-1 right-1 bg-black bg-opacity-80 text-white text-xs px-1 py-0.5 rounded">
                  {video.duration}
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-base line-clamp-2 mb-2 cursor-pointer hover:text-blue-600 transition-colors leading-tight">
                  {video.title}
                </h3>
                <div className="flex items-center space-x-3 mb-1">
                  <img
                    src={video.channelAvatar}
                    alt={video.channelName}
                    className="w-6 h-6 rounded-full object-cover"
                  />
                  <span className="text-sm text-gray-700 hover:text-gray-900 cursor-pointer">
                    {video.channelName}
                  </span>
                </div>
                <div className="text-sm text-gray-600">
                  {video.views} views • {video.uploadTime}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Load more */}
        <div className="flex justify-center mt-8">
          <Button 
            variant="outline" 
            size="lg"
            className="rounded-full px-8 py-3 border-2 hover:bg-gray-50 transition-all duration-200"
          >
            Show more
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Trending;