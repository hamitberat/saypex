import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import VideoCard from '../components/VideoCard';
import { Button } from '../components/ui/button';
import { Filter, Search } from 'lucide-react';
import { videoApi, handleApiError } from '../services/api';

const SearchResults = ({ sidebarOpen }) => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('search_query') || '';
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('relevance');
  const [filterOpen, setFilterOpen] = useState(false);

  const sortOptions = [
    { value: 'relevance', label: 'Relevance' },
    { value: 'upload_date', label: 'Upload date' },
    { value: 'view_count', label: 'View count' },
    { value: 'rating', label: 'Rating' },
  ];

  const filterOptions = [
    { label: 'Upload date', options: ['Hour', 'Today', 'Week', 'Month', 'Year'] },
    { label: 'Type', options: ['Video', 'Channel', 'Playlist', 'Movie'] },
    { label: 'Duration', options: ['Under 4 minutes', '4-20 minutes', 'Over 20 minutes'] },
    { label: 'Features', options: ['Live', '4K', 'HD', 'Subtitles/CC', 'Creative Commons', '360°', 'VR180', '3D', 'HDR'] },
  ];

  useEffect(() => {
    if (query) {
      setLoading(true);
      // Simulate API call
      setTimeout(() => {
        const searchResults = mockSearchResults(query);
        setResults(searchResults);
        setLoading(false);
      }, 500);
    }
  }, [query]);

  if (loading) {
    return (
      <div className={`pt-14 transition-all duration-300 ${sidebarOpen ? 'ml-60' : 'ml-16'}`}>
        <div className="p-6">
          <div className="space-y-4">
            {[...Array(8)].map((_, index) => (
              <div key={index} className="animate-pulse flex space-x-4">
                <div className="w-80 h-48 bg-gray-200 rounded-lg flex-shrink-0"></div>
                <div className="flex-1">
                  <div className="h-6 bg-gray-200 rounded mb-3"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
                    <div className="h-4 bg-gray-200 rounded w-24"></div>
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
            <h1 className="text-lg font-medium">
              About {results.length.toLocaleString()} results for "{query}"
            </h1>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setFilterOpen(!filterOpen)}
              className="flex items-center space-x-2"
            >
              <Filter className="w-4 h-4" />
              <span>Filters</span>
            </Button>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
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
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {filterOptions.map((filter) => (
                <div key={filter.label}>
                  <h3 className="font-medium text-sm mb-2">{filter.label}</h3>
                  <div className="space-y-1">
                    {filter.options.map((option) => (
                      <label key={option} className="flex items-center space-x-2 text-sm">
                        <input type="checkbox" className="rounded" />
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
          <div className="flex flex-col items-center justify-center py-12">
            <Search className="w-12 h-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-700 mb-2">No results found</h3>
            <p className="text-gray-500 text-center max-w-md">
              Try different keywords or remove search filters
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {results.map((video) => (
              <div key={video.id} className="flex flex-col lg:flex-row space-y-4 lg:space-y-0 lg:space-x-4 p-2 hover:bg-gray-50 rounded-lg transition-colors duration-200">
                <div className="flex-shrink-0">
                  <div className="relative w-full lg:w-80 aspect-video">
                    <img
                      src={video.thumbnail}
                      alt={video.title}
                      className="w-full h-full object-cover rounded-lg"
                    />
                    <div className="absolute bottom-2 right-2 bg-black bg-opacity-90 text-white text-xs px-2 py-1 rounded font-medium">
                      {video.duration}
                    </div>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-lg line-clamp-2 mb-2 cursor-pointer hover:text-blue-600 transition-colors">
                    {video.title}
                  </h3>
                  <div className="text-sm text-gray-600 mb-2">
                    {video.views} views • {video.uploadTime}
                  </div>
                  <div className="flex items-center space-x-3 mb-3">
                    <img
                      src={video.channelAvatar}
                      alt={video.channelName}
                      className="w-6 h-6 rounded-full object-cover"
                    />
                    <span className="text-sm text-gray-700 hover:text-gray-900 cursor-pointer">
                      {video.channelName}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed">
                    {video.description}
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