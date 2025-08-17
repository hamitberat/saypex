#!/usr/bin/env python3
"""
Script to populate the database with mock data for YouTube clone
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
import random

from ..core.database import init_database, get_database
from ..models.video import Video, VideoCategory, VideoStatus, VideoMetrics, VideoThumbnail, VideoQuality
from ..models.user import User, UserRole, UserStatus, UserStats, UserPreferences
from ..models.comment import Comment, CommentStatus, CommentMetrics
from ..repositories.video_repository import video_repository
from ..repositories.user_repository import user_repository
from ..repositories.comment_repository import comment_repository
from ..services.user_service import user_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock data from frontend
MOCK_VIDEOS = [
    {
        'title': 'Learn JavaScript in 2025 - Complete Course',
        'thumbnail': 'https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwzfHx0ZWNobm9sb2d5fGVufDB8fHx8MTc1NTQyOTYxNXww&ixlib=rb-4.1.0&q=85',
        'channelName': 'CodeMaster',
        'channelAvatar': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
        'views': 2500000,
        'uploadTime': '2 days ago',
        'duration': '3:45:23',
        'duration_seconds': 13523,
        'description': 'Complete JavaScript course covering all fundamentals and advanced concepts.',
        'youtubeUrl': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        'likes': 125000,
        'dislikes': 2300,
        'subscribers': '1.2M',
        'category': VideoCategory.EDUCATION,
        'tags': ['javascript', 'programming', 'web development', 'tutorial']
    },
    {
        'title': 'React Advanced Patterns and Best Practices',
        'thumbnail': 'https://images.unsplash.com/photo-1531297484001-80022131f5a1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwyfHx0ZWNobm9sb2d5fGVufDB8fHx8MTc1NTQyOTYxNXww&ixlib=rb-4.1.0&q=85',
        'channelName': 'React Pro',
        'channelAvatar': 'https://images.unsplash.com/photo-1494790108755-2616b332011c?w=100&h=100&fit=crop&crop=face',
        'views': 890000,
        'uploadTime': '5 days ago',
        'duration': '2:15:41',
        'duration_seconds': 8141,
        'description': 'Advanced React patterns, performance optimization, and production-ready techniques.',
        'youtubeUrl': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        'likes': 45000,
        'dislikes': 800,
        'subscribers': '750K',
        'category': VideoCategory.EDUCATION,
        'tags': ['react', 'javascript', 'frontend', 'patterns', 'optimization']
    },
    {
        'title': 'AI and Machine Learning Fundamentals',
        'thumbnail': 'https://images.unsplash.com/photo-1649972904349-6e44c42644a7?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MXwxfHNlYXJjaHwxfHx0ZWNobm9sb2d5fGVufDB8fHx8MTc1NTQyOTYxNXww&ixlib=rb-4.1.0&q=85',
        'channelName': 'AI Academy',
        'channelAvatar': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face',
        'views': 1800000,
        'uploadTime': '1 week ago',
        'duration': '4:22:15',
        'duration_seconds': 15735,
        'description': 'Comprehensive introduction to artificial intelligence and machine learning concepts.',
        'youtubeUrl': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        'likes': 95000,
        'dislikes': 1200,
        'subscribers': '2.1M',
        'category': VideoCategory.TECHNOLOGY,
        'tags': ['ai', 'machine learning', 'python', 'data science', 'algorithms']
    },
    {
        'title': 'Web Development Project - Build a Full Stack App',
        'thumbnail': 'https://images.pexels.com/photos/5077064/pexels-photo-5077064.jpeg',
        'channelName': 'FullStack Dev',
        'channelAvatar': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
        'views': 567000,
        'uploadTime': '3 days ago',
        'duration': '5:33:12',
        'duration_seconds': 19992,
        'description': 'Build a complete full-stack application from scratch using modern technologies.',
        'youtubeUrl': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        'likes': 38000,
        'dislikes': 950,
        'subscribers': '425K',
        'category': VideoCategory.EDUCATION,
        'tags': ['fullstack', 'web development', 'javascript', 'node.js', 'react']
    },
    {
        'title': 'Hardware Design Principles and Circuit Analysis',
        'thumbnail': 'https://images.unsplash.com/photo-1518770660439-4636190af475?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHw0fHx0ZWNobm9sb2d5fGVufDB8fHx8MTc1NTQyOTYxNXww&ixlib=rb-4.1.0&q=85',
        'channelName': 'TechHardware',
        'channelAvatar': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop&crop=face',
        'views': 324000,
        'uploadTime': '4 days ago',
        'duration': '1:45:30',
        'duration_seconds': 6330,
        'description': 'Deep dive into hardware design, circuit analysis, and electronic components.',
        'youtubeUrl': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        'likes': 15500,
        'dislikes': 320,
        'subscribers': '198K',
        'category': VideoCategory.TECHNOLOGY,
        'tags': ['hardware', 'electronics', 'circuits', 'engineering']
    },
    {
        'title': 'Python Data Science and Analytics',
        'thumbnail': 'https://images.unsplash.com/photo-1694878982378-4fc7fb9ca415?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzh8MHwxfHNlYXJjaHwxfHx2aWRlbyUyMHRodW1ibmFpbHN8ZW58MHx8fHwxNzU1NDI5NjExfDA&ixlib=rb-4.1.0&q=85',
        'channelName': 'DataScience Pro',
        'channelAvatar': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop&crop=face',
        'views': 1100000,
        'uploadTime': '6 days ago',
        'duration': '3:12:45',
        'duration_seconds': 11565,
        'description': 'Master Python for data science, analytics, and statistical analysis.',
        'youtubeUrl': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        'likes': 67000,
        'dislikes': 1100,
        'subscribers': '890K',
        'category': VideoCategory.TECHNOLOGY,
        'tags': ['python', 'data science', 'analytics', 'pandas', 'numpy']
    }
]

MOCK_USERS = [
    {
        'username': 'codemaster',
        'email': 'codemaster@example.com',
        'full_name': 'Alex Johnson',
        'channel_name': 'CodeMaster',
        'avatar_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
        'bio': 'Teaching programming and software development',
        'subscribers': 1200000,
        'role': UserRole.CREATOR
    },
    {
        'username': 'reactpro',
        'email': 'reactpro@example.com',
        'full_name': 'Sarah Chen',
        'channel_name': 'React Pro',
        'avatar_url': 'https://images.unsplash.com/photo-1494790108755-2616b332011c?w=100&h=100&fit=crop&crop=face',
        'bio': 'Advanced React tutorials and tips',
        'subscribers': 750000,
        'role': UserRole.CREATOR
    },
    {
        'username': 'aiacademy',
        'email': 'aiacademy@example.com',
        'full_name': 'Dr. Michael Roberts',
        'channel_name': 'AI Academy',
        'avatar_url': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face',
        'bio': 'Making AI and ML accessible to everyone',
        'subscribers': 2100000,
        'role': UserRole.CREATOR
    },
    {
        'username': 'fullstackdev',
        'email': 'fullstackdev@example.com',
        'full_name': 'David Kim',
        'channel_name': 'FullStack Dev',
        'avatar_url': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
        'bio': 'Full-stack development tutorials and projects',
        'subscribers': 425000,
        'role': UserRole.CREATOR
    },
    {
        'username': 'techhardware',
        'email': 'techhardware@example.com',
        'full_name': 'Emma Wilson',
        'channel_name': 'TechHardware',
        'avatar_url': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop&crop=face',
        'bio': 'Hardware engineering and electronics',
        'subscribers': 198000,
        'role': UserRole.CREATOR
    },
    {
        'username': 'datasciencepro',
        'email': 'datasciencepro@example.com',
        'full_name': 'Lisa Martinez',
        'channel_name': 'DataScience Pro',
        'avatar_url': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop&crop=face',
        'bio': 'Data science and analytics expert',
        'subscribers': 890000,
        'role': UserRole.CREATOR
    }
]

MOCK_COMMENTS = [
    {
        'content': 'Excellent tutorial! This really helped me understand JavaScript concepts better.',
        'author_username': 'TechEnthusiast',
        'author_avatar': 'https://images.unsplash.com/photo-1633332755192-727a05c4013d?w=50&h=50&fit=crop&crop=face',
        'likes': 145,
        'replies': [
            {
                'content': 'Thank you! Glad it was helpful!',
                'author_username': 'codemaster',
                'author_avatar': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=50&h=50&fit=crop&crop=face',
                'likes': 23
            }
        ]
    },
    {
        'content': 'Great explanation of closures and async programming!',
        'author_username': 'WebDeveloper2025',
        'author_avatar': 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=50&h=50&fit=crop&crop=face',
        'likes': 89,
        'replies': []
    }
]


async def create_users() -> List[User]:
    """Create mock users"""
    logger.info("Creating mock users...")
    users = []
    
    for user_data in MOCK_USERS:
        # Hash password
        password_hash = user_service.hash_password("password123")
        
        # Create user stats
        stats = UserStats(
            subscribers_count=user_data['subscribers'],
            videos_uploaded=random.randint(50, 200),
            total_video_views=user_data['subscribers'] * random.randint(10, 50)
        )
        
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            full_name=user_data['full_name'],
            password_hash=password_hash,
            avatar_url=user_data['avatar_url'],
            bio=user_data['bio'],
            role=user_data['role'],
            status=UserStatus.ACTIVE,
            is_email_verified=True,
            channel_name=user_data['channel_name'],
            stats=stats,
            preferences=UserPreferences()
        )
        
        created_user = await user_repository.create(user)
        # Set channel_id to user's own ID for simplicity
        await user_repository.update_by_id(str(created_user.id), {
            "channel_id": created_user.id
        })
        
        users.append(created_user)
        logger.info(f"Created user: {user_data['username']}")
    
    return users


async def create_videos(users: List[User]) -> List[Video]:
    """Create mock videos"""
    logger.info("Creating mock videos...")
    videos = []
    
    for i, video_data in enumerate(MOCK_VIDEOS):
        user = users[i]  # Match video to user
        
        # Create thumbnail
        thumbnail = VideoThumbnail(
            url=video_data['thumbnail'],
            width=1280,
            height=720
        )
        
        # Create metrics
        metrics = VideoMetrics(
            views=video_data['views'],
            likes=video_data['likes'],
            dislikes=video_data['dislikes'],
            comments_count=random.randint(100, 1000),
            shares=random.randint(500, 5000)
        )
        metrics.engagement_rate = metrics.calculate_engagement_rate()
        
        # Create video quality
        quality = VideoQuality(
            resolution="1080p",
            bitrate=5000,
            fps=30,
            codec="h264"
        )
        
        # Calculate upload time
        days_ago = int(video_data['uploadTime'].split()[0])
        upload_date = datetime.utcnow() - timedelta(days=days_ago)
        
        video = Video(
            title=video_data['title'],
            description=video_data['description'],
            channel_id=user.channel_id,
            channel_name=user.channel_name,
            channel_avatar=user.avatar_url,
            video_url=video_data['youtubeUrl'],
            youtube_embed_url=video_data['youtubeUrl'],
            duration_seconds=video_data['duration_seconds'],
            thumbnails=[thumbnail],
            category=video_data['category'],
            tags=video_data['tags'],
            status=VideoStatus.PUBLISHED,
            metrics=metrics,
            quality=quality,
            created_at=upload_date,
            updated_at=upload_date
        )
        
        # Calculate trending score
        video.update_trending_score()
        
        created_video = await video_repository.create(video)
        videos.append(created_video)
        logger.info(f"Created video: {video_data['title']}")
    
    return videos


async def create_comments(videos: List[Video], users: List[User]):
    """Create mock comments"""
    logger.info("Creating mock comments...")
    
    # Create some regular users for comments
    regular_users = []
    for i in range(5):
        username = f"user{i+1}"
        password_hash = user_service.hash_password("password123")
        
        user = User(
            username=username,
            email=f"{username}@example.com",
            full_name=f"User {i+1}",
            password_hash=password_hash,
            role=UserRole.VIEWER,
            status=UserStatus.ACTIVE,
            is_email_verified=True
        )
        
        created_user = await user_repository.create(user)
        regular_users.append(created_user)
    
    # Create comments for the first video
    video = videos[0]
    
    for comment_data in MOCK_COMMENTS:
        # Find or create comment author
        author = None
        if comment_data['author_username'] == 'codemaster':
            author = users[0]  # CodeMaster
        else:
            author = regular_users[0]  # Use first regular user
        
        # Create main comment
        comment = await comment_repository.create_comment(
            content=comment_data['content'],
            video_id=str(video.id),
            author_id=str(author.id),
            author_username=author.username,
            author_avatar=author.avatar_url
        )
        
        # Update comment likes
        await comment_repository.update_comment_metrics(
            str(comment.id),
            {"likes": comment_data['likes']}
        )
        
        # Create replies
        for reply_data in comment_data['replies']:
            reply_author = users[0] if reply_data['author_username'] == 'codemaster' else regular_users[1]
            
            reply = await comment_repository.create_comment(
                content=reply_data['content'],
                video_id=str(video.id),
                author_id=str(reply_author.id),
                author_username=reply_author.username,
                author_avatar=reply_author.avatar_url,
                parent_id=str(comment.id)
            )
            
            await comment_repository.update_comment_metrics(
                str(reply.id),
                {"likes": reply_data['likes']}
            )
        
        logger.info(f"Created comment with {len(comment_data['replies'])} replies")


async def populate_database():
    """Main function to populate database with mock data"""
    try:
        # Initialize database
        await init_database()
        logger.info("Database initialized")
        
        # Clear existing data (optional)
        db = await get_database()
        await db.users.delete_many({})
        await db.videos.delete_many({})
        await db.comments.delete_many({})
        await db.user_video_interactions.delete_many({})
        logger.info("Cleared existing data")
        
        # Create mock data
        users = await create_users()
        videos = await create_videos(users)
        await create_comments(videos, users)
        
        logger.info("✅ Database populated successfully!")
        logger.info(f"Created {len(users)} users, {len(videos)} videos, and comments")
        
    except Exception as e:
        logger.error(f"❌ Error populating database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(populate_database())