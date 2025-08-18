import React, { useState, useEffect } from 'react';
import VideoCard from '../components/VideoCard';
import { Button } from '../components/ui/button';
import { Flame, Music, Gamepad2, Film, TrendingUp, Crown, Award, Star } from 'lucide-react';
import { videoApi, handleApiError } from '../services/api';

const Trending = ({ sidebarOpen }) => {
  const [videos, setVideos] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('Now');
  const [loading, setLoading] = useState(true);

  const categories = [
    { name: 'Now', icon: Flame, color: 'from-red-500 to-orange-500' },
    { name: 'Music', icon: Music, color: 'from-purple-500 to-pink-500' },
    { name: 'Gaming', icon: Gamepad2, color: 'from-blue-500 to-cyan-500' },
    { name: 'Movies', icon: Film, color: 'from-green-500 to-emerald-500' },
  ];

  useEffect(() => {
    const loadTrendingVideos = async () => {
      setLoading(true);
      try {
        const params = { limit: 50 };
        if (selectedCategory !== 'Now') {
          params.category = selectedCategory.toLowerCase();
        }
        
        const trendingData = await videoApi.getTrendingVideos(params);
        setVideos(trendingData || []);
      } catch (error) {
        console.error('Error loading trending videos:', handleApiError(error));
        setVideos([]);
      } finally {
        setLoading(false);
      }
    };

    loadTrendingVideos();
  }, [selectedCategory]);

  const getTrendingIcon = (index) => {
    if (index === 0) return <Crown className="w-5 h-5 text-yellow-500" />;
    if (index === 1) return <Award className="w-5 h-5 text-gray-400" />;
    if (index === 2) return <Star className="w-5 h-5 text-amber-600" />;
    return <span className="text-lg font-bold text-purple-400">#{index + 1}</span>;
  };

  if (loading) {
    return (
      <div className={`pt-14 transition-all duration-300 ${sidebarOpen ? 'ml-60' : 'ml-16'}`}>
        <div className="p-6">
          <div className="space-y-4">
            {[...Array(10)].map((_, index) => (
              <div key={index} className="animate-pulse flex space-x-4">
                <div className="w-8 h-8 bg-purple-200 rounded-full flex-shrink-0"></div>
                <div className="w-40 h-24 bg-gradient-to-br from-purple-100 to-blue-100 rounded-lg flex-shrink-0"></div>
                <div className="flex-1">
                  <div className="h-4 bg-purple-200 rounded mb-2"></div>
                  <div className="h-3 bg-purple-200 rounded w-3/4 mb-1"></div>
                  <div className="h-3 bg-purple-200 rounded w-1/2"></div>
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
        <div className="flex items-center space-x-3 mb-8">
          <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-orange-500 rounded-xl flex items-center justify-center">
            <TrendingUp className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Trending</h1>
            <p className="text-gray-600">What's popular on SAYPEX right now</p>
          </div>
        </div>

        {/* Category Tabs */}
        <div className="flex items-center space-x-1 mb-8 border-b border-purple-100">
          {categories.map((category) => (
            <Button
              key={category.name}
              variant="ghost"
              className={`flex items-center space-x-2 px-6 py-3 border-b-2 transition-all duration-200 rounded-none ${
                selectedCategory === category.name
                  ? 'border-purple-500 text-purple-700 bg-purple-50 font-medium'
                  : 'border-transparent text-gray-600 hover:text-purple-600 hover:bg-purple-50'
              }`}
              onClick={() => setSelectedCategory(category.name)}
            >
              <category.icon className="w-4 h-4" />
              <span>{category.name}</span>
            </Button>
          ))}
        </div>

        {/* Trending Videos List */}
        {videos.length === 0 ? (
          <div className="text-center py-16">
            <div className="w-24 h-24 bg-gradient-to-br from-purple-100 to-blue-100 rounded-full flex items-center justify-center mb-6">
              <TrendingUp className="w-12 h-12 text-purple-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No trending videos</h3>
            <p className="text-gray-500 mb-6">
              {selectedCategory === 'Now' 
                ? 'No trending videos available at the moment.' 
                : `No trending ${selectedCategory.toLowerCase()} videos available.`}
            </p>
            <Button 
              onClick={() => setSelectedCategory('Now')}
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-full px-6 py-2"
            >
              View All Trending
            </Button>
          </div>
        ) : (
          <>
            <div className="space-y-4">
              {videos.map((video, index) => (
                <div key={video.id} className="flex items-start space-x-4 p-4 hover:bg-gradient-to-r hover:from-purple-50 hover:to-blue-50 rounded-xl transition-all duration-200 group">
                  <div className="flex-shrink-0 w-8 text-center flex items-center justify-center">
                    {getTrendingIcon(index)}
                  </div>
                  <div className="relative flex-shrink-0">
                    <img
                      src={video.thumbnails?.[0]?.url || video.thumbnail || '/placeholder-thumbnail.jpg'}
                      alt={video.title || 'Video thumbnail'}
                      className="w-40 h-24 object-cover rounded-lg group-hover:scale-105 transition-transform duration-200"
                    />
                    <div className="absolute bottom-1 right-1 bg-black/80 text-white text-xs px-2 py-1 rounded font-medium">
                      {video.duration || '0:00'}
                    </div>
                    {index < 3 && (
                      <div className="absolute top-1 left-1 bg-gradient-to-r from-yellow-400 to-orange-500 text-white text-xs px-2 py-1 rounded-full font-bold shadow-lg">
                        TOP {index + 1}
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-base line-clamp-2 mb-2 cursor-pointer hover:text-purple-600 transition-colors leading-tight text-gray-800">
                      {video.title || 'Untitled Video'}
                    </h3>
                    <div className="flex items-center space-x-3 mb-2">
                      <img
                        src={video.channel_avatar || 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=24&h=24&fit=crop&crop=face'}
                        alt={video.channel_name || 'Channel'}
                        className="w-6 h-6 rounded-full object-cover ring-1 ring-purple-200"
                      />
                      <span className="text-sm text-purple-600 hover:text-purple-700 cursor-pointer font-medium">
                        {video.channel_name || 'Unknown Channel'}
                      </span>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>{video.metrics?.views || video.views || 0} views</span>
                      <span>•</span>
                      <span>{video.upload_time || 'Recently'}</span>
                      {video.trending_score && (
                        <>
                          <span>•</span>
                          <span className="text-purple-600 font-medium">
                            🔥 {Math.round(video.trending_score)} trending score
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Load more */}
            <div className="flex justify-center mt-12">
              <Button 
                variant="outline" 
                size="lg"
                className="rounded-full px-8 py-3 border-2 border-purple-200 text-purple-700 hover:bg-purple-50 hover:border-purple-300 transition-all duration-200"
              >
                Show More Trending
              </Button>
            </div>
          </>
        )}

        {/* Trending Categories Grid */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Explore by Category</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {categories.map((category) => (
              <div 
                key={category.name}
                className={`bg-gradient-to-br ${category.color} p-6 rounded-xl text-white cursor-pointer hover:scale-105 transition-all duration-200 shadow-lg`}
                onClick={() => setSelectedCategory(category.name)}
              >
                <category.icon className="w-8 h-8 mb-3" />
                <h3 className="text-lg font-semibold mb-2">{category.name}</h3>
                <p className="text-sm opacity-90">
                  {category.name === 'Now' && 'Latest trending videos'}
                  {category.name === 'Music' && 'Hot music videos'}
                  {category.name === 'Gaming' && 'Gaming highlights'}
                  {category.name === 'Movies' && 'Movie trailers & clips'}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Trending;