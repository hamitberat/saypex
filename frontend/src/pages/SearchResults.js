import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import VideoCard from '../components/VideoCard';
import { Button } from '../components/ui/button';
import { Filter, Search, SlidersHorizontal } from 'lucide-react';
import { videoApi, handleApiError } from '../services/api';

const SearchResults = ({ sidebarOpen }) => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('search_query') || '';
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('relevance');
  const [filterOpen, setFilterOpen] = useState(false);

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

  const sortOptions = [
    { value: 'relevance', label: 'Relevance' },
    { value: 'date', label: 'Upload date' },
    { value: 'views', label: 'View count' },
    { value: 'likes', label: 'Rating' },
  ];

  const filterOptions = [
    { label: 'Upload date', options: ['Hour', 'Today', 'Week', 'Month', 'Year'] },
    { label: 'Type', options: ['Video', 'Channel', 'Playlist', 'Movie'] },
    { label: 'Duration', options: ['Under 4 minutes', '4-20 minutes', 'Over 20 minutes'] },
    { label: 'Features', options: ['Live', '4K', 'HD', 'Subtitles/CC', 'Creative Commons', '360°', 'VR180', '3D', 'HDR'] },
  ];

  useEffect(() => {
    const performSearch = async () => {
      if (query) {
        setLoading(true);
        try {
          const params = {
            q: query,
            sort_by: sortBy,
            limit: 20,
            offset: 0
          };
          
          const searchResults = await videoApi.searchVideos(params);
          setResults(searchResults || []);
        } catch (error) {
          console.error('Search error:', handleApiError(error));
          setResults([]);
        } finally {
          setLoading(false);
        }
      }
    };

    performSearch();
  }, [query, sortBy]);

  if (loading) {
    return (
      <div className={`pt-14 transition-all duration-300 ${sidebarOpen ? 'ml-60' : 'ml-16'}`}>
        <div className="p-6">
          <div className="space-y-4">
            {[...Array(8)].map((_, index) => (
              <div key={index} className="animate-pulse flex space-x-4">
                <div className="w-80 h-48 bg-gradient-to-br from-purple-100 to-blue-100 rounded-lg flex-shrink-0"></div>
                <div className="flex-1">
                  <div className="h-6 bg-purple-200 rounded mb-3"></div>
                  <div className="h-4 bg-purple-200 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-purple-200 rounded w-1/2 mb-4"></div>
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-purple-200 rounded-full"></div>
                    <div className="h-4 bg-purple-200 rounded w-24"></div>
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
      <div className="p-6">
        {/* Search Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <h1 className="text-lg font-medium text-gray-800">
              About {results.length.toLocaleString()} results for 
              <span className="text-purple-600 font-semibold"> "{query}"</span>
            </h1>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setFilterOpen(!filterOpen)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-all duration-200 ${
                filterOpen 
                  ? 'bg-purple-100 text-purple-700' 
                  : 'hover:bg-purple-50 text-gray-700'
              }`}
            >
              <SlidersHorizontal className="w-4 h-4" />
              <span>Filters</span>
            </Button>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="border border-purple-200 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-200 focus:border-purple-400 bg-white"
            >
              {sortOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Filters Panel */}
        {filterOpen && (
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 mb-6 border border-purple-100">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {filterOptions.map((filter) => (
                <div key={filter.label}>
                  <h3 className="font-medium text-sm mb-3 text-purple-700">{filter.label}</h3>
                  <div className="space-y-2">
                    {filter.options.map((option) => (
                      <label key={option} className="flex items-center space-x-2 text-sm cursor-pointer hover:text-purple-600 transition-colors">
                        <input 
                          type="checkbox" 
                          className="rounded border-purple-300 text-purple-600 focus:ring-purple-200" 
                        />
                        <span>{option}</span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Search Results */}
        {results.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="w-24 h-24 bg-gradient-to-br from-purple-100 to-blue-100 rounded-full flex items-center justify-center mb-6">
              <Search className="w-12 h-12 text-purple-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No results found</h3>
            <p className="text-gray-500 text-center max-w-md mb-6">
              Try different keywords or remove search filters to find more videos
            </p>
            <Button 
              onClick={() => window.location.href = '/'}
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white rounded-full px-6 py-2"
            >
              Browse All Videos
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            {results.map((video) => (
              <div key={video.id} className="flex flex-col lg:flex-row space-y-4 lg:space-y-0 lg:space-x-4 p-4 hover:bg-gradient-to-r hover:from-purple-50 hover:to-blue-50 rounded-xl transition-all duration-200 group">
                <div className="flex-shrink-0">
                  <div className="relative w-full lg:w-80 aspect-video">
                    <img
                      src={video.thumbnails?.[0]?.url || video.thumbnail || '/placeholder-thumbnail.jpg'}
                      alt={video.title || 'Video thumbnail'}
                      className="w-full h-full object-cover rounded-lg group-hover:scale-105 transition-transform duration-200"
                    />
                    <div className="absolute bottom-2 right-2 bg-black/90 text-white text-xs px-2 py-1 rounded font-medium">
                      {formatDuration(video.duration_seconds) || video.duration || '0:00'}
                    </div>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-lg line-clamp-2 mb-2 cursor-pointer hover:text-purple-600 transition-colors text-gray-800">
                    {video.title || 'Untitled Video'}
                  </h3>
                  <div className="text-sm text-gray-600 mb-2">
                    {video.metrics?.views || video.views || 0} views • {video.upload_time || 'Recently'}
                  </div>
                  <div className="flex items-center space-x-3 mb-3">
                    <img
                      src={video.channel_avatar || 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=24&h=24&fit=crop&crop=face'}
                      alt={video.channel_name || 'Channel'}
                      className="w-6 h-6 rounded-full object-cover ring-1 ring-purple-200"
                    />
                    <span className="text-sm text-purple-600 hover:text-purple-700 cursor-pointer font-medium">
                      {video.channel_name || 'Unknown Channel'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed">
                    {video.description || 'No description available.'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchResults;