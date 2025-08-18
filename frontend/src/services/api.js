import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create axios instance with default config
const api = axios.create({
  baseURL: API,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - clear token and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Video API
export const videoApi = {
  // Get videos for home page
  getVideos: async (params = {}) => {
    const response = await api.get('/videos/', { params });
    return response.data;
  },

  // Get video by ID
  getVideo: async (videoId) => {
    const response = await api.get(`/videos/${videoId}`);
    return response.data;
  },

  // Create new video
  createVideo: async (videoData) => {
    const response = await api.post('/videos', videoData);
    return response.data;
  },

  // Update video
  updateVideo: async (videoId, updateData) => {
    const response = await api.put(`/videos/${videoId}`, updateData);
    return response.data;
  },

  // Delete video
  deleteVideo: async (videoId) => {
    const response = await api.delete(`/videos/${videoId}`);
    return response.data;
  },

  // Search videos
  searchVideos: async (params = {}) => {
    const response = await api.get('/videos/search', { params });
    return response.data;
  },

  // Get trending videos
  getTrendingVideos: async (params = {}) => {
    const response = await api.get('/videos/trending', { params });
    return response.data;
  },

  // Get video recommendations
  getRecommendations: async (videoId, params = {}) => {
    const response = await api.get(`/videos/${videoId}/recommendations`, { params });
    return response.data;
  },

  // Like video
  likeVideo: async (videoId) => {
    const response = await api.post(`/videos/${videoId}/like`);
    return response.data;
  },

  // Dislike video
  dislikeVideo: async (videoId) => {
    const response = await api.post(`/videos/${videoId}/dislike`);
    return response.data;
  },

  // Remove reaction (like/dislike)
  removeReaction: async (videoId) => {
    const response = await api.delete(`/videos/${videoId}/reaction`);
    return response.data;
  },
};

// User API
export const userApi = {
  // Register new user
  register: async (userData) => {
    const response = await api.post('/users/register', userData);
    return response.data;
  },

  // Login user
  login: async (credentials) => {
    const response = await api.post('/users/login', credentials);
    return response.data;
  },

  // Get current user profile
  getCurrentUser: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },

  // Update current user profile
  updateCurrentUser: async (updateData) => {
    const response = await api.put('/users/me', updateData);
    return response.data;
  },

  // Get public user profile
  getUser: async (userId) => {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  },

  // Create channel
  createChannel: async (channelName, channelDescription = null) => {
    const response = await api.post('/users/create-channel', {
      channel_name: channelName,
      channel_description: channelDescription,
    });
    return response.data;
  },

  // Subscribe to channel
  subscribe: async (channelId) => {
    const response = await api.post(`/users/subscribe/${channelId}`);
    return response.data;
  },

  // Unsubscribe from channel
  unsubscribe: async (channelId) => {
    const response = await api.delete(`/users/subscribe/${channelId}`);
    return response.data;
  },

  // Get user subscriptions
  getSubscriptions: async () => {
    const response = await api.get('/users/me/subscriptions');
    return response.data;
  },

  // Search users
  searchUsers: async (query, limit = 20) => {
    const response = await api.get('/users/search', {
      params: { q: query, limit },
    });
    return response.data;
  },
};

// Comment API
export const commentApi = {
  // Get video comments
  getVideoComments: async (videoId, params = {}) => {
    const response = await api.get(`/comments/video/${videoId}`, { params });
    return response.data;
  },

  // Create comment
  createComment: async (commentData) => {
    const response = await api.post('/comments', commentData);
    return response.data;
  },

  // Get comment replies
  getReplies: async (commentId, params = {}) => {
    const response = await api.get(`/comments/${commentId}/replies`, { params });
    return response.data;
  },

  // Update comment
  updateComment: async (commentId, updateData) => {
    const response = await api.put(`/comments/${commentId}`, updateData);
    return response.data;
  },

  // Delete comment
  deleteComment: async (commentId) => {
    const response = await api.delete(`/comments/${commentId}`);
    return response.data;
  },

  // Like comment
  likeComment: async (commentId) => {
    const response = await api.post(`/comments/${commentId}/like`);
    return response.data;
  },

  // Unlike comment
  unlikeComment: async (commentId) => {
    const response = await api.delete(`/comments/${commentId}/like`);
    return response.data;
  },

  // Pin comment
  pinComment: async (commentId) => {
    const response = await api.post(`/comments/${commentId}/pin`);
    return response.data;
  },

  // Heart comment
  heartComment: async (commentId) => {
    const response = await api.post(`/comments/${commentId}/heart`);
    return response.data;
  },

  // Flag comment
  flagComment: async (commentId) => {
    const response = await api.post(`/comments/${commentId}/flag`);
    return response.data;
  },

  // Get user comments
  getUserComments: async (userId, params = {}) => {
    const response = await api.get(`/comments/user/${userId}`, { params });
    return response.data;
  },
};

// Auth helper functions
export const authHelpers = {
  // Save auth data to localStorage
  saveAuthData: (authData) => {
    localStorage.setItem('access_token', authData.access_token);
    localStorage.setItem('user', JSON.stringify(authData.user));
  },

  // Get current user from localStorage
  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  // Logout user
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },
};

// Error handling helper
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const message = error.response.data?.detail || error.response.data?.message || 'An error occurred';
    return { message, status: error.response.status };
  } else if (error.request) {
    // Request was made but no response received
    return { message: 'Network error. Please check your connection.', status: 0 };
  } else {
    // Something else happened
    return { message: error.message || 'An unexpected error occurred', status: -1 };
  }
};

export default api;