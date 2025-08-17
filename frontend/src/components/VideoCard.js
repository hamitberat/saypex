import React, { useState } from 'react';
import { MoreVertical, Clock } from 'lucide-react';
import { Button } from './ui/button';
import { useNavigate } from 'react-router-dom';

const VideoCard = ({ video, layout = 'grid' }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const navigate = useNavigate();

  const handleVideoClick = () => {
    navigate(`/watch?v=${video.id}`);
  };

  const handleChannelClick = (e) => {
    e.stopPropagation();
    navigate(`/channel/${video.channelName}`);
  };

  const formatViews = (views) => {
    if (typeof views === 'string') return views;
    if (views >= 1000000) return `${(views / 1000000).toFixed(1)}M`;
    if (views >= 1000) return `${(views / 1000).toFixed(1)}K`;
    return views.toString();
  };

  if (layout === 'list') {
    return (
      <div className="flex space-x-3 p-2 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors duration-200" onClick={handleVideoClick}>
        <div className="relative flex-shrink-0">
          <img
            src={video.thumbnail}
            alt={video.title}
            className="w-40 h-24 object-cover rounded-lg"
            onLoad={() => setImageLoaded(true)}
          />
          <div className="absolute bottom-1 right-1 bg-black bg-opacity-80 text-white text-xs px-1 py-0.5 rounded">
            {video.duration}
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-sm line-clamp-2 mb-1 leading-tight">{video.title}</h3>
          <div className="text-xs text-gray-600 mb-1">{video.channelName}</div>
          <div className="text-xs text-gray-500">
            {formatViews(video.views)} views • {video.uploadTime}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="group cursor-pointer" onClick={handleVideoClick}>
      <div className="relative mb-3 overflow-hidden rounded-xl">
        <div className={`aspect-video bg-gray-200 rounded-xl overflow-hidden transition-all duration-200 group-hover:rounded-lg ${
          imageLoaded ? '' : 'animate-pulse'
        }`}>
          <img
            src={video.thumbnail}
            alt={video.title}
            className="w-full h-full object-cover transition-transform duration-200 group-hover:scale-105"
            onLoad={() => setImageLoaded(true)}
          />
        </div>
        <div className="absolute bottom-2 right-2 bg-black bg-opacity-90 text-white text-xs px-2 py-1 rounded font-medium">
          {video.duration}
        </div>
        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <Button 
            variant="ghost" 
            size="sm" 
            className="p-1 h-8 w-8 bg-black bg-opacity-70 hover:bg-opacity-90 rounded-full"
            onClick={(e) => e.stopPropagation()}
          >
            <MoreVertical className="w-4 h-4 text-white" />
          </Button>
        </div>
      </div>
      
      <div className="flex space-x-3">
        <div 
          className="flex-shrink-0 cursor-pointer"
          onClick={handleChannelClick}
        >
          <img
            src={video.channelAvatar}
            alt={video.channelName}
            className="w-9 h-9 rounded-full object-cover hover:scale-105 transition-transform duration-200"
          />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-base line-clamp-2 mb-1 leading-tight group-hover:text-blue-600 transition-colors duration-200">
            {video.title}
          </h3>
          <div 
            className="text-sm text-gray-600 hover:text-gray-800 cursor-pointer mb-1 transition-colors duration-200"
            onClick={handleChannelClick}
          >
            {video.channelName}
          </div>
          <div className="flex items-center text-sm text-gray-500 space-x-1">
            <span>{formatViews(video.views)} views</span>
            <span>•</span>
            <span>{video.uploadTime}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoCard;