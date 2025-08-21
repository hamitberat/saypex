import React, { useState } from 'react';
import { MoreVertical, Clock, Play } from 'lucide-react';
import { Button } from './ui/button';
import { useNavigate } from 'react-router-dom';

const VideoCard = ({ video, layout = 'grid' }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageHovered, setImageHovered] = useState(false);
  const navigate = useNavigate();

  // Safety check for video object
  if (!video) {
    return null;
  }

  const handleVideoClick = () => {
    navigate(`/watch?v=${video.id}`);
  };

  const handleChannelClick = (e) => {
    e.stopPropagation();
    navigate(`/channel/${video.channel_name || 'unknown'}`);
  };

  const formatViews = (views) => {
    if (!views && views !== 0) return '0';
    if (typeof views === 'string') return views;
    if (views >= 1000000) return `${(views / 1000000).toFixed(1)}M`;
    if (views >= 1000) return `${(views / 1000).toFixed(1)}K`;
    return views.toString();
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '0:00';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
      return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
  };

  const getThumbnailUrl = () => {
    if (video.thumbnails && video.thumbnails.length > 0) {
      return video.thumbnails[0].url;
    }
    return video.thumbnail || '/placeholder-thumbnail.jpg';
  };

  const getUploadTime = () => {
    if (video.upload_time) return video.upload_time;
    if (video.created_at) {
      try {
        const date = new Date(video.created_at);
        const now = new Date();
        const diffInDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
        
        if (diffInDays === 0) return 'today';
        if (diffInDays === 1) return '1 day ago';
        if (diffInDays < 7) return `${diffInDays} days ago`;
        if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`;
        if (diffInDays < 365) return `${Math.floor(diffInDays / 30)} months ago`;
        return `${Math.floor(diffInDays / 365)} years ago`;
      } catch {
        return 'recently';
      }
    }
    return 'recently';
  };

  if (layout === 'list') {
    return (
      <div className="flex space-x-3 p-2 hover:bg-gradient-to-r hover:from-purple-50 hover:to-blue-50 rounded-lg cursor-pointer transition-all duration-200 group" onClick={handleVideoClick}>
        <div className="relative flex-shrink-0">
          <img
            src={getThumbnailUrl()}
            alt={video.title || 'Video thumbnail'}
            className="w-40 h-24 object-cover rounded-lg group-hover:scale-105 transition-transform duration-200"
            onLoad={() => setImageLoaded(true)}
          />
          <div className="absolute bottom-1 right-1 bg-black/80 text-white text-xs px-2 py-1 rounded font-medium">
            {formatDuration(video.duration_seconds)}
          </div>
          <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-200 rounded-lg flex items-center justify-center">
            <Play className="w-6 h-6 text-white" />
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-sm line-clamp-2 mb-1 leading-tight text-gray-800 group-hover:text-purple-700 transition-colors">
            {video.title || 'Untitled Video'}
          </h3>
          <div className="text-xs text-purple-600 mb-1 hover:text-purple-700 cursor-pointer transition-colors" onClick={handleChannelClick}>
            {video.channel_name || 'Unknown Channel'}
          </div>
          <div className="text-xs text-gray-500">
            {formatViews(video.metrics?.views || video.views || 0)} views • {getUploadTime()}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="group cursor-pointer" onClick={handleVideoClick}>
      <div 
        className="relative mb-3 overflow-hidden rounded-xl"
        onMouseEnter={() => setImageHovered(true)}
        onMouseLeave={() => setImageHovered(false)}
      >
        <div className={`aspect-video bg-gradient-to-br from-purple-100 to-blue-100 rounded-xl overflow-hidden transition-all duration-200 group-hover:rounded-lg ${
          imageLoaded ? '' : 'animate-pulse'
        }`}>
          <img
            src={getThumbnailUrl()}
            alt={video.title || 'Video thumbnail'}
            className="w-full h-full object-cover transition-all duration-300 group-hover:scale-110"
            onLoad={() => setImageLoaded(true)}
          />
        </div>
        
        {/* Duration Badge */}
        <div className="absolute bottom-2 right-2 bg-black/90 text-white text-xs px-2 py-1 rounded font-medium shadow-lg">
          {formatDuration(video.duration_seconds)}
        </div>
        
        {/* Play Button Overlay */}
        <div className={`absolute inset-0 bg-black/30 flex items-center justify-center transition-all duration-200 ${
          imageHovered ? 'opacity-100' : 'opacity-0'
        }`}>
          <div className="w-14 h-14 bg-white/90 rounded-full flex items-center justify-center shadow-lg">
            <Play className="w-6 h-6 text-purple-600 ml-1" />
          </div>
        </div>
        
        {/* More Options Button */}
        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <Button 
            variant="ghost" 
            size="sm" 
            className="p-1 h-8 w-8 bg-black/70 hover:bg-black/80 rounded-full text-white"
            onClick={(e) => e.stopPropagation()}
          >
            <MoreVertical className="w-4 h-4" />
          </Button>
        </div>
      </div>
      
      <div className="flex space-x-3">
        <div 
          className="flex-shrink-0 cursor-pointer"
          onClick={handleChannelClick}
        >
          <img
            src={video.channel_avatar || 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=36&h=36&fit=crop&crop=face'}
            alt={video.channel_name || 'Channel avatar'}
            className="w-9 h-9 rounded-full object-cover hover:scale-105 transition-transform duration-200 ring-2 ring-purple-100"
          />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-base line-clamp-2 mb-1 leading-tight group-hover:text-purple-700 transition-colors duration-200 text-gray-800">
            {video.title || 'Untitled Video'}
          </h3>
          <div 
            className="text-sm text-purple-600 hover:text-purple-700 cursor-pointer mb-1 transition-colors duration-200 font-medium"
            onClick={handleChannelClick}
          >
            {video.channel_name || 'Unknown Channel'}
          </div>
          <div className="flex items-center text-sm text-gray-500 space-x-1">
            <span>{formatViews(video.metrics?.views || video.views || 0)} views</span>
            <span>•</span>
            <span>{getUploadTime()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoCard;