import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { ThumbsUp, ThumbsDown, Share, Download, MoreHorizontal, Bell, Play, Settings, Volume2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Separator } from '../components/ui/separator';
import VideoCard from '../components/VideoCard';
import CommentSection from '../components/CommentSection';
import { videoApi, handleApiError, authHelpers } from '../services/api';

const Watch = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const videoId = searchParams.get('v');
  const [video, setVideo] = useState(null);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [isDisliked, setIsDisliked] = useState(false);
  const [showDescription, setShowDescription] = useState(false);
  const [recommendedVideos, setRecommendedVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const currentUser = authHelpers.getCurrentUser();

  // Mock video data for demonstration
  const mockVideo = {
    id: "demo_video_1",
    title: "Building Modern Web Applications with React and FastAPI - Complete Tutorial",
    description: "Learn how to build a complete modern web application using React for the frontend and FastAPI for the backend. In this comprehensive tutorial, we'll cover:\n\n🚀 Setting up the development environment\n📱 Building responsive UI components\n⚡ Creating RESTful APIs\n🔐 Implementing authentication\n💾 Database integration with PostgreSQL\n🎨 Styling with Tailwind CSS\n\nThis tutorial is perfect for developers who want to learn full-stack development with modern tools and frameworks. We'll build a real-world application from scratch and deploy it to production.\n\n⏰ Timestamps:\n0:00 Introduction\n5:30 Project setup\n15:20 Frontend development\n45:10 Backend API creation\n1:20:15 Database integration\n1:55:30 Authentication system\n2:30:45 Deployment guide\n\n💻 Source code: https://github.com/example/react-fastapi-tutorial\n📚 Documentation: https://docs.example.com\n\n#React #FastAPI #WebDevelopment #Tutorial #Programming",
    channel_name: "TechLearning Pro",
    channel_avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=40&h=40&fit=crop&crop=face",
    video_url: "https://www.youtube.com/embed/dQw4w9WgXcQ",
    youtube_embed_url: "https://www.youtube.com/embed/dQw4w9WgXcQ",
    duration_seconds: 9847, // 2 hours 44 minutes 7 seconds
    metrics: {
      views: 1234567,
      likes: 45678,
      dislikes: 892,
      comments: 1245
    },
    subscribers: 856000,
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000), // 2 days ago
    category: "education",
    thumbnails: [{
      url: "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&h=450&fit=crop",
      width: 800,
      height: 450
    }]
  };

  // Mock recommended videos
  const mockRecommendedVideos = [
    {
      id: "rec_1",
      title: "JavaScript ES2024 New Features You Need to Know",
      channel_name: "JS Mastery",
      duration_seconds: 1234,
      views: 567890,
      thumbnails: [{
        url: "https://images.unsplash.com/photo-1593720219276-0b1eacd0aef4?w=300&h=200&fit=crop",
        width: 300,
        height: 200
      }],
      created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000)
    },
    {
      id: "rec_2", 
      title: "Advanced React Patterns and Best Practices",
      channel_name: "React Academy",
      duration_seconds: 2145,
      views: 234567,
      thumbnails: [{
        url: "https://images.unsplash.com/photo-1633356122102-3fe601e05bd2?w=300&h=200&fit=crop",
        width: 300,
        height: 200
      }],
      created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000)
    },
    {
      id: "rec_3",
      title: "PostgreSQL Performance Optimization Guide",
      channel_name: "Database Pro",
      duration_seconds: 1876,
      views: 189432,
      thumbnails: [{
        url: "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=300&h=200&fit=crop",
        width: 300,
        height: 200
      }],
      created_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000)
    },
    {
      id: "rec_4",
      title: "Building Scalable APIs with FastAPI and Python",
      channel_name: "Python Dev",
      duration_seconds: 3421,
      views: 445621,
      thumbnails: [{
        url: "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=300&h=200&fit=crop",
        width: 300,
        height: 200
      }],
      created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
    },
    {
      id: "rec_5",
      title: "Modern CSS Grid and Flexbox Layout Techniques",
      channel_name: "CSS Masters",
      duration_seconds: 1654,
      views: 323455,
      thumbnails: [{
        url: "https://images.unsplash.com/photo-1507721999472-8ed4421c4af2?w=300&h=200&fit=crop",
        width: 300,
        height: 200
      }],
      created_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000)
    }
  ];

  useEffect(() => {
    const loadVideoData = async () => {
      if (!videoId) {
        // For demo purposes, load mock data even without videoId
        setVideo(mockVideo);
        setRecommendedVideos(mockRecommendedVideos);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        
        // Try to get real video data first
        try {
          const videoData = await videoApi.getVideo(videoId);
          if (videoData) {
            setVideo(videoData);
            // Get recommended videos
            const recommendedData = await videoApi.getRecommendations(videoId, { limit: 8 });
            setRecommendedVideos(recommendedData || mockRecommendedVideos);
            setLoading(false);
            return;
          }
        } catch (apiError) {
          console.warn('API call failed, using mock data:', apiError);
        }
        
        // Fallback to mock data
        setVideo(mockVideo);
        setRecommendedVideos(mockRecommendedVideos);
        
      } catch (error) {
        console.error('Error loading video data:', handleApiError(error));
        setError('Failed to load video. Showing demo content.');
        setVideo(mockVideo);
        setRecommendedVideos(mockRecommendedVideos);
      } finally {
        setLoading(false);
      }
    };

    loadVideoData();
  }, [videoId]);

  const handleLike = async () => {
    if (!currentUser) {
      alert('Please sign in to like videos');
      return;
    }
    
    try {
      if (isLiked) {
        await videoApi.removeReaction(videoId);
        setIsLiked(false);
      } else {
        await videoApi.likeVideo(videoId);
        setIsLiked(true);
        if (isDisliked) setIsDisliked(false);
      }
    } catch (error) {
      console.error('Error liking video:', error);
    }
  };

  const handleDislike = async () => {
    if (!currentUser) {
      alert('Please sign in to dislike videos');
      return;
    }
    
    try {
      if (isDisliked) {
        await videoApi.removeReaction(videoId);
        setIsDisliked(false);
      } else {
        await videoApi.dislikeVideo(videoId);
        setIsDisliked(true);
        if (isLiked) setIsLiked(false);
      }
    } catch (error) {
      console.error('Error disliking video:', error);
    }
  };

  const handleSubscribe = () => {
    if (!currentUser) {
      alert('Please sign in to subscribe');
      return;
    }
    setIsSubscribed(!isSubscribed);
  };

  const formatNumber = (num) => {
    if (!num && num !== 0) return '0';
    if (typeof num === 'string') return num;
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '0:00';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="pt-14 ml-16 transition-all duration-300">
        <div className="flex flex-col lg:flex-row gap-6 p-6">
          <div className="flex-1">
            <div className="aspect-video bg-gradient-to-br from-purple-100 to-blue-100 rounded-xl mb-4 animate-pulse"></div>
            <div className="space-y-3 animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
          <div className="lg:w-80 xl:w-96 space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex space-x-3 animate-pulse">
                <div className="w-40 h-24 bg-gray-200 rounded-lg"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded"></div>
                  <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error && !video) {
    return (
      <div className="pt-14 ml-16 transition-all duration-300">
        <div className="flex justify-center items-center h-96">
          <div className="text-center">
            <div className="text-6xl text-purple-300 mb-4">📹</div>
            <div className="text-lg text-gray-600 mb-4">{error || 'Video not found'}</div>
            <Button 
              onClick={() => navigate('/')}
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-full px-6 py-2"
            >
              Return to Home
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="pt-14 ml-16 transition-all duration-300">
      <div className="flex flex-col xl:flex-row gap-6 p-6">
        {/* Main Content */}
        <div className="flex-1 max-w-5xl">
          {/* Video Player */}
          <div className="relative aspect-video bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl overflow-hidden mb-4 group">
            {video.youtube_embed_url || video.video_url ? (
              <iframe
                src={video.youtube_embed_url || video.video_url}
                title={video.title || 'Video Player'}
                className="w-full h-full"
                allowFullScreen
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              />
            ) : (
              <div className="flex items-center justify-center h-full bg-gradient-to-br from-purple-900 to-blue-900">
                <div className="text-center text-white">
                  <Play className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg">Video not available</p>
                </div>
              </div>
            )}
            
            {/* Player Controls Overlay */}
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <div className="flex items-center justify-between text-white">
                <div className="flex items-center space-x-4">
                  <Button size="sm" variant="ghost" className="text-white hover:bg-white/20">
                    <Play className="w-4 h-4" />
                  </Button>
                  <Button size="sm" variant="ghost" className="text-white hover:bg-white/20">
                    <Volume2 className="w-4 h-4" />
                  </Button>
                  <span className="text-sm">{formatDuration(video.duration_seconds)}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Button size="sm" variant="ghost" className="text-white hover:bg-white/20">
                    <Settings className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Video Info */}
          <div className="mb-4">
            <h1 className="text-xl font-bold mb-3 leading-tight text-gray-900">
              {video.title || 'Untitled Video'}
            </h1>
            
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="flex items-center space-x-4">
                <img
                  src={video.channel_avatar || 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=40&h=40&fit=crop&crop=face'}
                  alt={video.channel_name || 'Channel'}
                  className="w-10 h-10 rounded-full object-cover ring-2 ring-purple-200"
                />
                <div>
                  <div className="font-medium text-base text-gray-900">
                    {video.channel_name || 'Unknown Channel'}
                  </div>
                  <div className="text-sm text-gray-600">
                    {formatNumber(video.subscribers || 0)} subscribers
                  </div>
                </div>
                <Button
                  onClick={handleSubscribe}
                  className={`rounded-full px-6 py-2 font-medium transition-all duration-200 ${
                    isSubscribed
                      ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white'
                  }`}
                >
                  <Bell className={`w-4 h-4 mr-2 ${isSubscribed ? 'fill-current' : ''}`} />
                  {isSubscribed ? 'Subscribed' : 'Subscribe'}
                </Button>
              </div>

              <div className="flex items-center space-x-2">
                <div className="flex items-center bg-gray-100 rounded-full overflow-hidden">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleLike}
                    className={`rounded-l-full px-4 py-2 hover:bg-purple-100 transition-colors ${
                      isLiked ? 'bg-purple-100 text-purple-600' : ''
                    }`}
                  >
                    <ThumbsUp className={`w-4 h-4 mr-2 ${isLiked ? 'fill-current' : ''}`} />
                    {formatNumber(video.metrics?.likes || 0)}
                  </Button>
                  <Separator orientation="vertical" className="h-6" />
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleDislike}
                    className={`rounded-r-full px-4 py-2 hover:bg-red-100 transition-colors ${
                      isDisliked ? 'bg-red-100 text-red-600' : ''
                    }`}
                  >
                    <ThumbsDown className={`w-4 h-4 ${isDisliked ? 'fill-current' : ''}`} />
                  </Button>
                </div>

                <Button
                  variant="ghost"
                  size="sm"
                  className="bg-gray-100 hover:bg-blue-100 rounded-full px-4 py-2 transition-colors"
                >
                  <Share className="w-4 h-4 mr-2" />
                  Share
                </Button>

                <Button
                  variant="ghost"
                  size="sm"
                  className="bg-gray-100 hover:bg-green-100 rounded-full px-4 py-2 transition-colors"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>

                <Button
                  variant="ghost"
                  size="sm"
                  className="bg-gray-100 hover:bg-gray-200 rounded-full p-2"
                >
                  <MoreHorizontal className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* Description */}
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-4 mb-6 border border-purple-100">
            <div className="flex items-center space-x-4 text-sm font-medium mb-2 text-gray-700">
              <div>{formatNumber(video.metrics?.views || 0)} views</div>
              <div>{video.upload_time || formatTimestamp(video.created_at)}</div>
            </div>
            <div className={`text-sm leading-relaxed text-gray-700 ${showDescription ? '' : 'line-clamp-2'}`}>
              {video.description || 'No description available.'}
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowDescription(!showDescription)}
              className="mt-2 p-0 h-auto font-medium text-sm hover:bg-transparent hover:text-purple-600 transition-colors"
            >
              {showDescription ? 'Show less' : 'Show more'}
            </Button>
          </div>

          {/* Comments */}
          <CommentSection videoId={videoId} />
        </div>

        {/* Sidebar - Recommended Videos */}
        <div className="lg:w-80 xl:w-96">
          <div className="space-y-3">
            {recommendedVideos.length > 0 ? (
              recommendedVideos.map((recommendedVideo) => (
                <VideoCard
                  key={recommendedVideo.id}
                  video={recommendedVideo}
                  layout="list"
                />
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-2">🎬</div>
                <p>No recommendations available</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function for timestamp formatting
const formatTimestamp = (timestamp) => {
  if (!timestamp) return 'Unknown time';
  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;
    
    return date.toLocaleDateString();
  } catch {
    return 'recently';
  }
};

export default Watch;