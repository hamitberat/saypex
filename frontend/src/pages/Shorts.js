import React, { useState, useEffect, useRef } from 'react';
import { Heart, MessageCircle, Share, Play, User } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useNavigate } from 'react-router-dom';

const Shorts = () => {
  const navigate = useNavigate();
  const [shorts, setShorts] = useState([]);
  const [currentShort, setCurrentShort] = useState(0);

  // Mock shorts data with preview statistics
  const mockShorts = [
    {
      id: 'short1',
      videoUrl: 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
      title: 'Amazing cooking tips!',
      description: 'Learn how to make the perfect pasta in just 60 seconds! 🍝',
      hashtags: ['#cooking', '#pasta', '#quickrecipes', '#foodhacks'],
      channelName: 'ChefMaster',
      channelAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=40&h=40&fit=crop&crop=face',
      likes: 1250,
      dislikes: 47,
      comments: 89,
      hasPreview: true,
      previewVideoId: 'demo_video_4',
      previewStats: {
        totalTaps: 2876,
        swipeToWatch: 1934,
        tapToWatch: 942,
        conversionRate: 68.2
      }
    },
    {
      id: 'short2', 
      videoUrl: 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_2mb.mp4',
      title: 'Gaming pro tips',
      description: 'Master this combo to win every match! 🎮✨',
      hashtags: ['#gaming', '#protips', '#combo'],
      channelName: 'GamePro',
      channelAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=40&h=40&fit=crop&crop=face',
      likes: 2340,
      dislikes: 78,
      comments: 156,
      hasPreview: false
    },
    {
      id: 'short3',
      videoUrl: 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
      title: 'Daily motivation',
      description: 'Start your day with this powerful mindset! 💪 Remember, every expert was once a beginner.',
      hashtags: ['#motivation', '#daily', '#mindset', '#success'],
      channelName: 'MotivateDaily',
      channelAvatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b1c5?w=40&h=40&fit=crop&crop=face',
      likes: 3450,
      dislikes: 123,
      comments: 234,
      hasPreview: true,
      previewVideoId: 'demo_video_6',
      previewStats: {
        totalTaps: 4567,
        swipeToWatch: 2890,
        tapToWatch: 1677,
        conversionRate: 74.8
      }
    }
  ];

  useEffect(() => {
    setShorts(mockShorts);
  }, []);

  const handlePreviewClick = (short) => {
    if (short.hasPreview && short.previewVideoId) {
      // Simulate tracking preview button clicks
      console.log(`Preview clicked for ${short.title}`);
      console.log(`Previous stats: ${short.previewStats?.totalTaps || 0} total taps`);
      
      // In a real app, you would send this data to your analytics service
      // analytics.track('preview_button_clicked', {
      //   shortId: short.id,
      //   videoId: short.previewVideoId,
      //   method: 'tap' // could be 'tap' or 'swipe'
      // });
      
      navigate(`/watch?v=${short.previewVideoId}`);
    }
  };

  const handleChannelClick = (channelName) => {
    navigate(`/channel/${channelName}`);
  };

  const formatCount = (count) => {
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K`;
    }
    return count.toString();
  };

  if (shorts.length === 0) {
    return (
      <div className="pt-14 ml-16 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Play className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No Shorts Available</h3>
          <p className="text-gray-500">Check back later for new short videos!</p>
        </div>
      </div>
    );
  }

  const current = shorts[currentShort];

  return (
    <div className="pt-14 ml-16 min-h-screen bg-black flex items-center justify-center">
      {/* Shorts Container */}
      <div className="relative w-full max-w-md h-[calc(100vh-56px)] bg-black overflow-hidden">
        {/* Video Container */}
        <div className="relative w-full h-full flex items-center justify-center">
          {/* Placeholder for video */}
          <div className="w-full h-full bg-gray-900 flex items-center justify-center">
            <div className="text-center text-white">
              <Play className="w-16 h-16 mx-auto mb-4 opacity-70" />
              <p className="text-lg font-medium">{current.title}</p>
              <p className="text-sm opacity-70 mt-2">Video would play here</p>
            </div>
          </div>

          {/* Bottom Left - Channel Info & Description */}
          <div className="absolute bottom-4 left-4 right-20 text-white">
            {/* Channel Name (Hyperlink) */}
            <button
              onClick={() => handleChannelClick(current.channelName)}
              className="flex items-center space-x-2 mb-3 hover:opacity-80 transition-opacity"
            >
              <img
                src={current.channelAvatar}
                alt={current.channelName}
                className="w-8 h-8 rounded-full"
              />
              <span className="font-semibold text-sm">@{current.channelName}</span>
            </button>

            {/* Description */}
            <p className="text-sm mb-2 leading-relaxed">{current.description}</p>

            {/* Hashtags */}
            {current.hashtags && current.hashtags.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {current.hashtags.map((hashtag, index) => (
                  <span
                    key={index}
                    className="text-xs text-blue-300 hover:text-blue-200 cursor-pointer"
                  >
                    {hashtag}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Bottom Right - Action Buttons */}
          <div className="absolute bottom-4 right-4 flex flex-col items-center space-y-4">
            {/* Like Button with Heart Emoji */}
            <div className="flex flex-col items-center">
              <Button
                variant="ghost"
                size="sm"
                className="w-12 h-12 rounded-full bg-white/20 hover:bg-red-100/30 text-white p-0"
              >
                <span className="text-2xl">❤️</span>
              </Button>
              <span className="text-xs text-white mt-1">{formatCount(current.likes)}</span>
            </div>

            {/* Dislike Button with Broken Heart Emoji */}
            <div className="flex flex-col items-center">
              <Button
                variant="ghost"
                size="sm"
                className="w-12 h-12 rounded-full bg-white/20 hover:bg-white/30 text-white p-0"
              >
                <span className="text-2xl">💔</span>
              </Button>
              <span className="text-xs text-white mt-1">{formatCount(current.dislikes)}</span>
            </div>

            {/* Comment Button */}
            <div className="flex flex-col items-center">
              <Button
                variant="ghost"
                size="sm"
                className="w-12 h-12 rounded-full bg-white/20 hover:bg-white/30 text-white p-0"
              >
                <MessageCircle className="w-6 h-6" />
              </Button>
              <span className="text-xs text-white mt-1">{formatCount(current.comments)}</span>
            </div>

            {/* Preview Button with Statistics */}
            {current.hasPreview && (
              <div className="flex flex-col items-center">
                <Button
                  onClick={() => handlePreviewClick(current)}
                  variant="ghost"
                  size="sm"
                  className="w-12 h-12 rounded-full bg-transparent hover:bg-white/10 text-white p-0 relative group transition-all"
                >
                  {/* Your Exact Preview Icon Design */}
                  <div className="flex items-center justify-center">
                    <svg width="32" height="20" viewBox="0 0 32 20" fill="none" className="text-white">
                      {/* First play button (rounded square) */}
                      <rect x="0" y="2" width="12" height="12" rx="2" fill="currentColor"/>
                      <path d="M4 5L9 8L4 11V5Z" fill="white"/>
                      
                      {/* Arrow pointing right */}
                      <path d="M14 8L17 10L14 12V8Z" fill="currentColor"/>
                      
                      {/* Second play button (rounded square) */}
                      <rect x="20" y="0" width="16" height="16" rx="3" fill="currentColor"/>
                      <path d="M25 4L31 8L25 12V4Z" fill="white"/>
                    </svg>
                  </div>
                  
                  {/* Statistics Tooltip */}
                  {current.previewStats && (
                    <div className="absolute right-14 top-1/2 transform -translate-y-1/2 bg-black/90 text-white text-xs px-3 py-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                      <div className="text-center">
                        <div className="font-semibold text-purple-300">Preview Stats</div>
                        <div className="mt-1">👆 {formatCount(current.previewStats.totalTaps)} taps</div>
                        <div>📺 {formatCount(current.previewStats.swipeToWatch + current.previewStats.tapToWatch)} watched</div>
                        <div className="text-green-300">📊 {current.previewStats.conversionRate}% rate</div>
                      </div>
                      {/* Arrow */}
                      <div className="absolute top-1/2 transform -translate-y-1/2 -right-1 w-2 h-2 bg-black/90 rotate-45"></div>
                    </div>
                  )}
                </Button>
                {/* Only show the count, no "Preview" text */}
                {current.previewStats && (
                  <span className="text-xs text-purple-300 mt-1">
                    {formatCount(current.previewStats.totalTaps)}
                  </span>
                )}
              </div>
            )}

            {/* Share Button */}
            <div className="flex flex-col items-center">
              <Button
                variant="ghost"
                size="sm"
                className="w-12 h-12 rounded-full bg-white/20 hover:bg-white/30 text-white p-0"
              >
                <Share className="w-6 h-6" />
              </Button>
            </div>
          </div>

          {/* Navigation indicators */}
          {shorts.length > 1 && (
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
              <div className="flex flex-col space-y-2">
                {shorts.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentShort(index)}
                    className={`w-2 h-8 rounded-full transition-colors ${
                      index === currentShort ? 'bg-white' : 'bg-white/40'
                    }`}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Shorts;