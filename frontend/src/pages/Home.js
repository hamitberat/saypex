import React, { useState, useEffect } from 'react';
import VideoCard from '../components/VideoCard';
import { videoApi, handleApiError } from '../services/api';
import { Button } from '../components/ui/button';
import { Flame, Gamepad2, ChefHat, Coffee, Calendar, Sparkles } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

const Home = ({ sidebarOpen }) => {
  const [searchParams] = useSearchParams();
  const [videos, setVideos] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [loading, setLoading] = useState(true);

  const categories = [
    { name: 'All', icon: Sparkles },
    { name: 'Trending', icon: Flame },
    { name: 'Gaming', icon: Gamepad2 },
    { name: 'Cooking', icon: ChefHat },
    { name: 'Mukbang', icon: Coffee },
    { name: 'Daily', icon: Calendar },
  ];

  // Check for category parameter from URL (sidebar navigation)
  useEffect(() => {
    const categoryParam = searchParams.get('category');
    if (categoryParam) {
      // Capitalize first letter to match category names
      const categoryName = categoryParam.charAt(0).toUpperCase() + categoryParam.slice(1);
      const validCategory = categories.find(cat => cat.name.toLowerCase() === categoryParam.toLowerCase());
      if (validCategory) {
        setSelectedCategory(validCategory.name);
      }
    } else {
      // If no category parameter, set to All
      setSelectedCategory('All');
    }
  }, [searchParams]);

  useEffect(() => {
    // Load videos from API
    const loadVideos = async () => {
      setLoading(true);
      try {
        const params = {};
        if (selectedCategory !== 'All') {
          params.category = selectedCategory.toLowerCase();
        }
        
        const videosData = await videoApi.getVideos(params);
        setVideos(videosData || []);
      } catch (error) {
        console.error('Error loading videos:', handleApiError(error));
        setVideos([]);
      } finally {
        setLoading(false);
      }
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
          {/* Category skeleton */}
          <div className="flex items-center space-x-3 p-4 overflow-x-auto scrollbar-hide mb-6">
            {[...Array(7)].map((_, i) => (
              <div key={i} className="h-8 w-20 bg-gradient-to-r from-purple-100 to-blue-100 rounded-full animate-pulse"></div>
            ))}
          </div>
          
          {/* 3x3 Video grid skeleton */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(9)].map((_, index) => (
              <div key={index} className="animate-pulse">
                <div className="aspect-video bg-gradient-to-br from-purple-100 to-blue-100 rounded-xl mb-3"></div>
                <div className="flex space-x-3">
                  <div className="w-9 h-9 bg-purple-200 rounded-full flex-shrink-0"></div>
                  <div className="flex-1">
                    <div className="h-4 bg-purple-200 rounded mb-2"></div>
                    <div className="h-3 bg-purple-200 rounded w-3/4 mb-1"></div>
                    <div className="h-3 bg-purple-200 rounded w-1/2"></div>
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
      <div className="sticky top-14 bg-white/95 backdrop-blur-sm border-b border-purple-100 z-30">
        <div className="flex items-center space-x-3 p-4 overflow-x-auto scrollbar-hide">
          {categories.map((category) => (
            <Button
              key={category.name}
              variant={selectedCategory === category.name ? "default" : "secondary"}
              size="sm"
              className={`flex items-center space-x-2 whitespace-nowrap rounded-full px-4 py-2 font-medium transition-all duration-200 ${
                selectedCategory === category.name
                  ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700 shadow-lg'
                  : 'bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200'
              }`}
              onClick={() => handleCategoryClick(category.name)}
            >
              <category.icon className="w-4 h-4" />
              <span>{category.name}</span>
            </Button>
          ))}
        </div>
      </div>

      {/* Video Grid - 3x3 Layout */}
      <div className="p-6">
        {videos.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🎬</div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No videos found</h3>
            <p className="text-gray-500 mb-6">
              {selectedCategory === 'All' 
                ? 'No videos available at the moment. Check back later!' 
                : `No ${selectedCategory.toLowerCase()} videos available.`}
            </p>
            <Button 
              onClick={() => handleCategoryClick('All')}
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-full px-6 py-2"
            >
              View All Videos
            </Button>
          </div>
        ) : (
          <>
            {/* Hero Section */}
            <div className="mb-8">
              <div className="bg-gradient-to-br from-purple-600 via-purple-700 to-blue-800 rounded-2xl p-8 text-white relative overflow-hidden">
                <div className="absolute inset-0 bg-black/20"></div>
                <div className="relative z-10">
                  <h1 className="text-4xl font-bold mb-4">Welcome to SAYPEX</h1>
                  <p className="text-lg text-purple-100 mb-6 max-w-2xl">
                    Discover amazing videos from creators around the world. Share your stories, connect with others, and explore endless entertainment.
                  </p>
                  <div className="flex space-x-4">
                    <Button 
                      className="bg-white text-purple-700 hover:bg-purple-50 font-semibold px-6 py-2 rounded-full"
                      onClick={() => handleCategoryClick('Trending')}
                    >
                      Explore Trending
                    </Button>
                    <Button 
                      variant="outline" 
                      className="border-white text-white hover:bg-white/10 px-6 py-2 rounded-full"
                      onClick={() => window.open('/upload', '_blank')}
                    >
                      Upload Video
                    </Button>
                  </div>
                </div>
                <div className="absolute -right-20 -top-20 w-40 h-40 bg-white/10 rounded-full"></div>
                <div className="absolute -left-10 -bottom-10 w-32 h-32 bg-blue-400/20 rounded-full"></div>
              </div>
            </div>

            {/* 3x3 Video Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {videos.slice(0, 9).map((video) => (
                <VideoCard
                  key={video.id}
                  video={video}
                  layout="grid"
                />
              ))}
            </div>

            {/* Load More Section */}
            {videos.length >= 9 && (
              <div className="text-center">
                <Button 
                  variant="outline" 
                  size="lg"
                  className="rounded-full px-8 py-3 border-2 border-purple-200 text-purple-700 hover:bg-purple-50 hover:border-purple-300 transition-all duration-200"
                >
                  Load More Videos
                </Button>
              </div>
            )}

            {/* Call to Action Section */}
            <div className="mt-12 bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-8 text-center border border-purple-100">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Ready to Share Your Story?</h2>
              <p className="text-gray-600 mb-6 max-w-md mx-auto">
                Join thousands of creators who are sharing their passion and connecting with audiences worldwide.
              </p>
              <Button 
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-full px-8 py-3 font-semibold"
                onClick={() => window.open('/upload', '_blank')}
              >
                Start Creating
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Home;