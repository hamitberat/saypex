import React, { useState, useEffect } from 'react';
import VideoCard from '../components/VideoCard';
import { videoApi, handleApiError } from '../services/api';
import { Button } from '../components/ui/button';
import { Flame, Gamepad2, ChefHat, Coffee, Calendar, Sparkles } from 'lucide-react';
import { useSearchParams, useNavigate } from 'react-router-dom';

const Home = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
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
        if (selectedCategory && selectedCategory !== 'All') {
          params.category = selectedCategory.toLowerCase();
        }
        
        // Try to fetch from API first
        let videosData = [];
        try {
          videosData = await videoApi.getVideos(params);
        } catch (apiError) {
          console.warn('API call failed, using mock data:', apiError);
        }
        
        // If no videos from API, use mock data
        if (!videosData || videosData.length === 0) {
          videosData = getMockVideos(selectedCategory);
        }
        
        setVideos(videosData);
      } catch (error) {
        console.error('Error loading videos:', handleApiError(error));
        // Fallback to mock data
        setVideos(getMockVideos(selectedCategory));
      } finally {
        setLoading(false);
      }
    };

    loadVideos();
  }, [selectedCategory]);

  // Mock video data function
  const getMockVideos = (category) => {
    const allMockVideos = [
      {
        id: "demo_video_1",
        title: "Building Modern Web Applications with React and FastAPI - Complete Tutorial",
        channel_name: "TechLearning Pro",
        channel_avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=40&h=40&fit=crop&crop=face",
        duration_seconds: 9847,
        views: 1234567,
        thumbnails: [{
          url: "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&h=450&fit=crop",
        }],
        created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
        category: "education"
      },
      {
        id: "demo_video_2",
        title: "Master JavaScript ES2024: New Features and Best Practices",
        channel_name: "JS Mastery",
        channel_avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=40&h=40&fit=crop&crop=face",
        duration_seconds: 1234,
        views: 567890,
        thumbnails: [{
          url: "https://images.unsplash.com/photo-1593720219276-0b1eacd0aef4?w=800&h=450&fit=crop",
        }],
        created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
        category: "education"
      },
      {
        id: "demo_video_3",
        title: "Epic Gaming Moments - Oultic Compilation 2024",
        channel_name: "GameMaster",
        channel_avatar: "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=40&h=40&fit=crop&crop=face",
        duration_seconds: 845,
        views: 892341,
        thumbnails: [{
          url: "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800&h=450&fit=crop",
        }],
        created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
        category: "gaming"
      },
      {
        id: "demo_video_4",
        title: "Quick & Easy Pasta Recipe - 15 Minutes to Perfection!",
        channel_name: "ChefMaster",
        channel_avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=40&h=40&fit=crop&crop=face",
        duration_seconds: 923,
        views: 445621,
        thumbnails: [{
          url: "https://images.unsplash.com/photo-1551782450-a2132b4ba21d?w=800&h=450&fit=crop",
        }],
        created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
        category: "cooking"
      },
      {
        id: "demo_video_5",
        title: "Korean Mukbang: Trying Viral Food Combinations",
        channel_name: "FoodieExplorer",
        channel_avatar: "https://images.unsplash.com/photo-1494790108755-2616b612b1c5?w=40&h=40&fit=crop&crop=face",
        duration_seconds: 2156,
        views: 723485,
        thumbnails: [{
          url: "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800&h=450&fit=crop",
        }],
        created_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000),
        category: "mukbang"
      },
      {
        id: "demo_video_6",
        title: "My Daily Morning Routine for Productivity",
        channel_name: "LifeHacks",
        channel_avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=40&h=40&fit=crop&crop=face",
        duration_seconds: 687,
        views: 334567,
        thumbnails: [{
          url: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=450&fit=crop",
        }],
        created_at: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000),
        category: "daily"
      },
      {
        id: "demo_video_7",
        title: "Latest Tech Trends 2024 - What's Hot in Technology",
        channel_name: "TechReview",
        channel_avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=40&h=40&fit=crop&crop=face",
        duration_seconds: 1456,
        views: 876543,
        thumbnails: [{
          url: "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=450&fit=crop",
        }],
        created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
        category: "trending"
      },
      {
        id: "demo_video_8",
        title: "Pro Gaming Tips: Advanced Strategies Revealed",
        channel_name: "GamePro",
        channel_avatar: "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=40&h=40&fit=crop&crop=face",
        duration_seconds: 1876,
        views: 654321,
        thumbnails: [{
          url: "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&h=450&fit=crop",
        }],
        created_at: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000),
        category: "gaming"
      },
      {
        id: "demo_video_9",
        title: "Ultimate Cooking Challenge: 5 Dishes in 30 Minutes",
        channel_name: "CookingChamp",
        channel_avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=40&h=40&fit=crop&crop=face",
        duration_seconds: 1834,
        views: 423789,
        thumbnails: [{
          url: "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&h=450&fit=crop",
        }],
        created_at: new Date(Date.now() - 9 * 24 * 60 * 60 * 1000),
        category: "cooking"
      }
    ];

    // Filter by category if specified
    if (category && category !== 'All') {
      return allMockVideos.filter(video => 
        video.category.toLowerCase() === category.toLowerCase()
      );
    }

    return allMockVideos;
  };

  const handleCategoryClick = (category) => {
    setSelectedCategory(category);
    
    // Update URL parameters
    if (category === 'All') {
      // Clear category parameter when "All" is selected
      navigate('/', { replace: true });
    } else {
      // Set category parameter for other categories
      navigate(`/?category=${category.toLowerCase()}`, { replace: true });
    }
  };

  if (loading) {
    return (
      <div className="pt-14 ml-16 transition-all duration-300">
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
    <div className="pt-14 ml-16 transition-all duration-300">
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
                  ? 'bg-gradient-to-r from-pink-600 to-blue-600 text-white hover:from-pink-700 hover:to-blue-700 shadow-lg'
                  : 'bg-pink-50 text-pink-700 hover:bg-pink-100 border border-pink-200'
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

          </>
        )}
      </div>
    </div>
  );
};

export default Home;