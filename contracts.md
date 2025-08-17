# YouTube Clone - API Contracts & Implementation Plan

## Current Frontend Implementation Status
✅ **Complete Frontend with Mock Data**
- Home page with video grid and category filters
- Video player page with recommended videos sidebar  
- Search functionality with results page
- Trending page with ranked video list
- Comments system with reply functionality
- Responsive design matching YouTube's interface

## API Contracts

### 1. Video Management APIs

#### GET /api/videos
- **Purpose**: Get videos for home page with optional filtering
- **Query Params**: `category`, `limit`, `offset`, `trending`
- **Response**: Array of video objects with metadata
- **Mock Data**: Currently using `mockVideos` array

#### GET /api/videos/:id
- **Purpose**: Get specific video details for video player page
- **Response**: Single video object with full details
- **Mock Data**: Finding video by ID from `mockVideos`

#### GET /api/videos/search
- **Purpose**: Search videos by query
- **Query Params**: `q` (search term), `limit`, `offset`, `sort`
- **Response**: Array of matching videos
- **Mock Data**: Using `mockSearchResults()` function

#### GET /api/videos/trending
- **Purpose**: Get trending videos
- **Query Params**: `category`, `limit`
- **Response**: Array of trending videos with ranking
- **Mock Data**: Using `mockTrendingVideos` array

### 2. User & Channel Management APIs

#### GET /api/channels/:name
- **Purpose**: Get channel information and videos
- **Response**: Channel object with videos array
- **Mock Data**: Using `mockChannels` array

#### POST /api/users/subscribe
- **Purpose**: Subscribe/unsubscribe to channel
- **Body**: `{ channelId, action: 'subscribe'|'unsubscribe' }`
- **Mock Data**: Currently stored in frontend state only

### 3. Interaction APIs

#### POST /api/videos/:id/like
- **Purpose**: Like/unlike video
- **Body**: `{ action: 'like'|'unlike'|'dislike' }`
- **Mock Data**: Currently stored in frontend state only

#### GET /api/videos/:id/comments
- **Purpose**: Get comments for video
- **Response**: Array of comment objects with nested replies
- **Mock Data**: Using `mockComments` array filtered by videoId

#### POST /api/videos/:id/comments
- **Purpose**: Add new comment
- **Body**: `{ content, parentId? }`
- **Mock Data**: Adding to local state in CommentSection component

### 4. Recommendation Engine APIs

#### GET /api/recommendations/:videoId
- **Purpose**: Get recommended videos for video player sidebar
- **Response**: Array of recommended videos
- **Mock Data**: Filtering `mockVideos` to exclude current video

#### GET /api/recommendations/personalized
- **Purpose**: Get personalized video recommendations for home page
- **Response**: Array of personalized video recommendations
- **Mock Data**: Currently using all `mockVideos`

## Data Models

### Video Object Structure
```javascript
{
  id: String,
  title: String,
  thumbnail: String,
  channelName: String,
  channelAvatar: String,
  views: String|Number,
  uploadTime: String,
  duration: String,
  description: String,
  youtubeUrl: String, // For embedded player
  likes: Number,
  dislikes: Number,
  subscribers: String,
  category?: String,
  tags?: Array<String>
}
```

### Comment Object Structure
```javascript
{
  id: String,
  videoId: String,
  author: String,
  authorAvatar: String,
  content: String,
  likes: Number,
  timestamp: String,
  replies: Array<Comment>,
  parentId?: String
}
```

## Backend Implementation Plan

### Phase 1: Core Video Management
1. **MongoDB Models**
   - Video model with all metadata fields
   - User model for basic user management
   - Channel model for channel information
   - Comment model with nested reply support

2. **Basic CRUD APIs**
   - Implement all video management endpoints
   - Replace mock data calls in frontend components
   - Add proper error handling and validation

### Phase 2: User Interactions
1. **Authentication & Authorization**
   - JWT-based authentication system
   - User registration and login
   - Protected routes for user actions

2. **Interaction Features**
   - Like/dislike functionality with database persistence
   - Subscribe/unsubscribe system
   - Comment system with reply threading
   - View count tracking

### Phase 3: Advanced Features
1. **Search & Filtering**
   - Full-text search implementation
   - Advanced filtering options
   - Search result ranking

2. **Recommendation Engine (ML)**
   - Basic collaborative filtering
   - Content-based recommendations
   - User behavior tracking
   - Trending algorithm implementation

### Phase 4: Performance & Scalability
1. **Optimization**
   - Video thumbnail optimization
   - Database indexing
   - API response caching
   - Pagination implementation

2. **Analytics**
   - View analytics
   - User engagement metrics
   - Popular content tracking

## Frontend Integration Points

### Files to Update for Backend Integration:
1. **mockData.js** - Remove and replace with API calls
2. **Home.js** - Replace `mockVideos` with API call to `/api/videos`
3. **Watch.js** - Replace mock data with API calls to `/api/videos/:id` and `/api/recommendations/:videoId`
4. **SearchResults.js** - Replace `mockSearchResults()` with API call to `/api/videos/search`
5. **Trending.js** - Replace `mockTrendingVideos` with API call to `/api/videos/trending`
6. **CommentSection.js** - Replace mock comments with API calls to comments endpoints

### API Service Layer
Create `src/services/api.js` to centralize all API calls and replace mock data usage throughout the frontend.

## Machine Learning Integration Plan

### Recommendation System
1. **User-Based Collaborative Filtering**
   - Track user viewing history
   - Find similar users based on viewing patterns
   - Recommend videos liked by similar users

2. **Content-Based Filtering**
   - Analyze video metadata (title, description, category)
   - Use NLP for content similarity
   - Recommend similar content

3. **Hybrid Approach**
   - Combine collaborative and content-based filtering
   - Weight recommendations based on user engagement
   - A/B testing for recommendation algorithms

### Implementation Strategy
- Start with basic recommendation logic
- Collect user interaction data
- Implement ML models using Python/scikit-learn
- Integrate with FastAPI backend
- Real-time recommendation updates

## Current Mock Data Status
- ✅ All frontend functionality working with comprehensive mock data
- ✅ 6 high-quality video thumbnails from vision expert
- ✅ Realistic user data with avatars and metadata
- ✅ Complete comment system with replies
- ✅ Search functionality filtering mock data
- ✅ Trending page with ranked content

**Next Step**: Implement backend APIs to replace mock data and add machine learning recommendations.