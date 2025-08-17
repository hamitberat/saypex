import React, { useState, useEffect } from 'react';
import VideoCard from '../components/VideoCard';
import { videoApi, handleApiError } from '../services/api';
import { Button } from '../components/ui/button';
import { Flame, Music, Gamepad2, Trophy, Lightbulb, Film } from 'lucide-react';

const Home = ({ sidebarOpen }) => {
  const [videos, setVideos] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [loading, setLoading] = useState(true);

  const categories = [
    { name: 'All', icon: null },
    { name: 'Trending', icon: Flame },
    { name: 'Music', icon: Music },
    { name: 'Gaming', icon: Gamepad2 },
    { name: 'Sports', icon: Trophy },
    { name: 'Learning', icon: Lightbulb },
    { name: 'Movies', icon: Film },
  ];

  useEffect(() => {
    // Simulate API call
    const loadVideos = async () => {
      setLoading(true);
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
      setVideos(mockVideos);
      setLoading(false);
    };

    loadVideos();
  }, [selectedCategory]);

  const handleCategoryClick = (category) => {
    setSelectedCategory(category);
  };

  if (loading) {
    return (
      <div className={`pt-14 transition-all duration-300 ${sidebarOpen ? 'ml-60' : 'ml-16'}`}>
        <div className="p-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[...Array(12)].map((_, index) => (
              <div key={index} className="animate-pulse">
                <div className="aspect-video bg-gray-200 rounded-xl mb-3"></div>
                <div className="flex space-x-3">
                  <div className="w-9 h-9 bg-gray-200 rounded-full flex-shrink-0"></div>
                  <div className="flex-1">
                    <div className="h-4 bg-gray-200 rounded mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-3/4 mb-1"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
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
      {/* Category Filter */}
      <div className="sticky top-14 bg-white border-b border-gray-200 z-30">
        <div className="flex items-center space-x-3 p-4 overflow-x-auto scrollbar-hide">
          {categories.map((category) => (
            <Button
              key={category.name}
              variant={selectedCategory === category.name ? "default" : "secondary"}
              size="sm"
              className={`flex items-center space-x-2 whitespace-nowrap rounded-full px-4 py-2 font-medium transition-all duration-200 ${
                selectedCategory === category.name
                  ? 'bg-black text-white hover:bg-gray-800'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              onClick={() => handleCategoryClick(category.name)}
            >
              {category.icon && <category.icon className="w-4 h-4" />}
              <span>{category.name}</span>
            </Button>
          ))}
        </div>
      </div>

      {/* Video Grid */}
      <div className="p-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-6">
          {videos.map((video) => (
            <VideoCard
              key={video.id}
              video={video}
              layout="grid"
            />
          ))}
        </div>

        {/* Load more section */}
        <div className="flex justify-center mt-12">
          <Button 
            variant="outline" 
            size="lg"
            className="rounded-full px-8 py-3 border-2 hover:bg-gray-50 transition-all duration-200"
          >
            Load more videos
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Home;