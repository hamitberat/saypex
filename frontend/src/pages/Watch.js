import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { ThumbsUp, ThumbsDown, Share, Download, MoreHorizontal, Bell } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Separator } from '../components/ui/separator';
import VideoCard from '../components/VideoCard';
import CommentSection from '../components/CommentSection';
import { mockVideos, mockComments } from '../mock/mockData';

const Watch = ({ sidebarOpen }) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const videoId = searchParams.get('v');
  const [video, setVideo] = useState(null);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [isDisliked, setIsDisliked] = useState(false);
  const [showDescription, setShowDescription] = useState(false);
  const [recommendedVideos, setRecommendedVideos] = useState([]);

  useEffect(() => {
    if (videoId) {
      const foundVideo = mockVideos.find(v => v.id === videoId);
      setVideo(foundVideo);
      
      // Get recommended videos (excluding current video)
      const recommended = mockVideos.filter(v => v.id !== videoId).slice(0, 8);
      setRecommendedVideos(recommended);
    }
  }, [videoId]);

  const handleLike = () => {
    setIsLiked(!isLiked);
    if (isDisliked) setIsDisliked(false);
  };

  const handleDislike = () => {
    setIsDisliked(!isDisliked);
    if (isLiked) setIsLiked(false);
  };

  const handleSubscribe = () => {
    setIsSubscribed(!isSubscribed);
  };

  const formatNumber = (num) => {
    if (typeof num === 'string') return num;
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  if (!video) {
    return (
      <div className={`pt-14 transition-all duration-300 ${sidebarOpen ? 'ml-60' : 'ml-16'}`}>
        <div className="flex justify-center items-center h-96">
          <div className="text-lg text-gray-500">Video not found</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`pt-14 transition-all duration-300 ${sidebarOpen ? 'ml-60' : 'ml-16'}`}>
      <div className="flex flex-col lg:flex-row gap-6 p-6">
        {/* Main Content */}
        <div className="flex-1">
          {/* Video Player */}
          <div className="relative aspect-video bg-black rounded-xl overflow-hidden mb-4">
            <iframe
              src={video.youtubeUrl}
              title={video.title}
              className="w-full h-full"
              allowFullScreen
              frameBorder="0"
            />
          </div>

          {/* Video Info */}
          <div className="mb-4">
            <h1 className="text-xl font-bold mb-3 leading-tight">{video.title}</h1>
            
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="flex items-center space-x-4">
                <img
                  src={video.channelAvatar}
                  alt={video.channelName}
                  className="w-10 h-10 rounded-full object-cover"
                />
                <div>
                  <div className="font-medium text-base">{video.channelName}</div>
                  <div className="text-sm text-gray-600">{video.subscribers} subscribers</div>
                </div>
                <Button
                  onClick={handleSubscribe}
                  className={`rounded-full px-6 py-2 font-medium transition-all duration-200 ${
                    isSubscribed
                      ? 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      : 'bg-black text-white hover:bg-gray-800'
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
                    className={`rounded-l-full px-4 py-2 hover:bg-gray-200 ${
                      isLiked ? 'bg-gray-200' : ''
                    }`}
                  >
                    <ThumbsUp className={`w-4 h-4 mr-2 ${isLiked ? 'fill-current' : ''}`} />
                    {formatNumber(video.likes)}
                  </Button>
                  <Separator orientation="vertical" className="h-6" />
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleDislike}
                    className={`rounded-r-full px-4 py-2 hover:bg-gray-200 ${
                      isDisliked ? 'bg-gray-200' : ''
                    }`}
                  >
                    <ThumbsDown className={`w-4 h-4 ${isDisliked ? 'fill-current' : ''}`} />
                  </Button>
                </div>

                <Button
                  variant="ghost"
                  size="sm"
                  className="bg-gray-100 hover:bg-gray-200 rounded-full px-4 py-2"
                >
                  <Share className="w-4 h-4 mr-2" />
                  Share
                </Button>

                <Button
                  variant="ghost"
                  size="sm"
                  className="bg-gray-100 hover:bg-gray-200 rounded-full px-4 py-2"
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
          <div className="bg-gray-100 rounded-xl p-4 mb-6">
            <div className="flex items-center space-x-4 text-sm font-medium mb-2">
              <div>{formatNumber(video.views)} views</div>
              <div>{video.uploadTime}</div>
            </div>
            <div className={`text-sm leading-relaxed ${showDescription ? '' : 'line-clamp-2'}`}>
              {video.description}
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowDescription(!showDescription)}
              className="mt-2 p-0 h-auto font-medium text-sm hover:bg-transparent hover:underline"
            >
              {showDescription ? 'Show less' : 'Show more'}
            </Button>
          </div>

          {/* Comments */}
          <CommentSection videoId={videoId} comments={mockComments} />
        </div>

        {/* Sidebar - Recommended Videos */}
        <div className="lg:w-80 xl:w-96">
          <div className="space-y-3">
            {recommendedVideos.map((recommendedVideo) => (
              <VideoCard
                key={recommendedVideo.id}
                video={recommendedVideo}
                layout="list"
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Watch;