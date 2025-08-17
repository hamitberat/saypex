// Mock data for YouTube clone
export const mockVideos = [
  {
    id: '1',
    title: 'Learn JavaScript in 2025 - Complete Course',
    thumbnail: 'https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwzfHx0ZWNobm9sb2d5fGVufDB8fHx8MTc1NTQyOTYxNXww&ixlib=rb-4.1.0&q=85',
    channelName: 'CodeMaster',
    channelAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
    views: '2.5M',
    uploadTime: '2 days ago',
    duration: '3:45:23',
    description: 'Complete JavaScript course covering all fundamentals and advanced concepts.',
    youtubeUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
    likes: 125000,
    dislikes: 2300,
    subscribers: '1.2M'
  },
  {
    id: '2',
    title: 'React Advanced Patterns and Best Practices',
    thumbnail: 'https://images.unsplash.com/photo-1531297484001-80022131f5a1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwyfHx0ZWNobm9sb2d5fGVufDB8fHx8MTc1NTQyOTYxNXww&ixlib=rb-4.1.0&q=85',
    channelName: 'React Pro',
    channelAvatar: 'https://images.unsplash.com/photo-1494790108755-2616b332011c?w=100&h=100&fit=crop&crop=face',
    views: '890K',
    uploadTime: '5 days ago',
    duration: '2:15:41',
    description: 'Advanced React patterns, performance optimization, and production-ready techniques.',
    youtubeUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
    likes: 45000,
    dislikes: 800,
    subscribers: '750K'
  },
  {
    id: '3',
    title: 'AI and Machine Learning Fundamentals',
    thumbnail: 'https://images.unsplash.com/photo-1649972904349-6e44c42644a7?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MXwxfHNlYXJjaHwxfHx0ZWNobm9sb2d5fGVufDB8fHx8MTc1NTQyOTYxNXww&ixlib=rb-4.1.0&q=85',
    channelName: 'AI Academy',
    channelAvatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face',
    views: '1.8M',
    uploadTime: '1 week ago',
    duration: '4:22:15',
    description: 'Comprehensive introduction to artificial intelligence and machine learning concepts.',
    youtubeUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
    likes: 95000,
    dislikes: 1200,
    subscribers: '2.1M'
  },
  {
    id: '4',
    title: 'Web Development Project - Build a Full Stack App',
    thumbnail: 'https://images.pexels.com/photos/5077064/pexels-photo-5077064.jpeg',
    channelName: 'FullStack Dev',
    channelAvatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
    views: '567K',
    uploadTime: '3 days ago',
    duration: '5:33:12',
    description: 'Build a complete full-stack application from scratch using modern technologies.',
    youtubeUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
    likes: 38000,
    dislikes: 950,
    subscribers: '425K'
  },
  {
    id: '5',
    title: 'Hardware Design Principles and Circuit Analysis',
    thumbnail: 'https://images.unsplash.com/photo-1518770660439-4636190af475?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHw0fHx0ZWNobm9sb2d5fGVufDB8fHx8MTc1NTQyOTYxNXww&ixlib=rb-4.1.0&q=85',
    channelName: 'TechHardware',
    channelAvatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop&crop=face',
    views: '324K',
    uploadTime: '4 days ago',
    duration: '1:45:30',
    description: 'Deep dive into hardware design, circuit analysis, and electronic components.',
    youtubeUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
    likes: 15500,
    dislikes: 320,
    subscribers: '198K'
  },
  {
    id: '6',
    title: 'Python Data Science and Analytics',
    thumbnail: 'https://images.unsplash.com/photo-1694878982378-4fc7fb9ca415?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwxfHx2aWRlbyUyMHRodW1ibmFpbHN8ZW58MHx8fHwxNzU1NDI5NjExfDA&ixlib=rb-4.1.0&q=85',
    channelName: 'DataScience Pro',
    channelAvatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop&crop=face',
    views: '1.1M',
    uploadTime: '6 days ago',
    duration: '3:12:45',
    description: 'Master Python for data science, analytics, and statistical analysis.',
    youtubeUrl: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
    likes: 67000,
    dislikes: 1100,
    subscribers: '890K'
  }
];

export const mockChannels = [
  {
    id: '1',
    name: 'CodeMaster',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
    subscribers: '1.2M',
    verified: true,
    description: 'Teaching programming and software development'
  },
  {
    id: '2',
    name: 'React Pro',
    avatar: 'https://images.unsplash.com/photo-1494790108755-2616b332011c?w=100&h=100&fit=crop&crop=face',
    subscribers: '750K',
    verified: true,
    description: 'Advanced React tutorials and tips'
  }
];

export const mockComments = [
  {
    id: '1',
    videoId: '1',
    author: 'TechEnthusiast',
    authorAvatar: 'https://images.unsplash.com/photo-1633332755192-727a05c4013d?w=50&h=50&fit=crop&crop=face',
    content: 'Excellent tutorial! This really helped me understand JavaScript concepts better.',
    likes: 145,
    timestamp: '2 hours ago',
    replies: [
      {
        id: '1-1',
        author: 'CodeMaster',
        authorAvatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=50&h=50&fit=crop&crop=face',
        content: 'Thank you! Glad it was helpful!',
        likes: 23,
        timestamp: '1 hour ago'
      }
    ]
  },
  {
    id: '2',
    videoId: '1',
    author: 'WebDeveloper2025',
    authorAvatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=50&h=50&fit=crop&crop=face',
    content: 'Great explanation of closures and async programming!',
    likes: 89,
    timestamp: '4 hours ago',
    replies: []
  }
];

export const mockPlaylists = [
  {
    id: '1',
    title: 'JavaScript Complete Course',
    videoCount: 45,
    thumbnail: 'https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwzfHx0ZWNobm9sb2d5fGVufDB8fHx8MTc1NTQyOTYxNXww&ixlib=rb-4.1.0&q=85',
    channelName: 'CodeMaster',
    updated: '2 days ago'
  },
  {
    id: '2',
    title: 'React Mastery',
    videoCount: 32,
    thumbnail: 'https://images.unsplash.com/photo-1531297484001-80022131f5a1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwyfHx0ZWNobm9sb2d5fGVufDb8fHx8MTc1NTQyOTYxNXww&ixlib=rb-4.1.0&q=85',
    channelName: 'React Pro',
    updated: '5 days ago'
  }
];

export const mockTrendingVideos = mockVideos.slice(0, 4);

export const mockSearchResults = (query) => {
  return mockVideos.filter(video => 
    video.title.toLowerCase().includes(query.toLowerCase()) ||
    video.channelName.toLowerCase().includes(query.toLowerCase())
  );
};