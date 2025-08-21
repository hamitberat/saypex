#!/usr/bin/env python3
"""
Simple script to populate the database with mock data
"""
import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, '/app')

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import bcrypt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'youtube_clone')

# Mock data
MOCK_DATA = {
    'users': [
        {
            '_id': ObjectId(),
            'username': 'codemaster',
            'email': 'codemaster@example.com',
            'full_name': 'Alex Johnson',
            'password_hash': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'avatar_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
            'bio': 'Teaching programming and software development',
            'role': 'creator',
            'status': 'active',
            'is_email_verified': True,
            'channel_name': 'CodeMaster',
            'stats': {
                'subscribers_count': 1200000,
                'videos_uploaded': 150,
                'total_video_views': 50000000
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'version': 1
        },
        {
            '_id': ObjectId(),
            'username': 'reactpro',
            'email': 'reactpro@example.com',
            'full_name': 'Sarah Chen',
            'password_hash': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'avatar_url': 'https://images.unsplash.com/photo-1494790108755-2616b332011c?w=100&h=100&fit=crop&crop=face',
            'bio': 'Advanced React tutorials and tips',
            'role': 'creator',
            'status': 'active',
            'is_email_verified': True,
            'channel_name': 'React Pro',
            'stats': {
                'subscribers_count': 750000,
                'videos_uploaded': 100,
                'total_video_views': 30000000
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'version': 1
        }
    ]
}

# Add channel_id to users (same as user _id for simplicity)
for user in MOCK_DATA['users']:
    user['channel_id'] = user['_id']

# Videos data
MOCK_DATA['videos'] = [
    {
        '_id': ObjectId(),
        'title': 'Learn JavaScript in 2025 - Complete Course',
        'description': 'Complete JavaScript course covering all fundamentals and advanced concepts.',
        'channel_id': MOCK_DATA['users'][0]['_id'],
        'channel_name': 'CodeMaster',
        'channel_avatar': MOCK_DATA['users'][0]['avatar_url'],
        'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        'youtube_embed_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        'duration_seconds': 13523,
        'thumbnails': [
            {
                'url': 'https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwzfHx0ZWNobm9sb2d5fGVufDB8fHx8MTc1NTQyOTYxNXww&ixlib=rb-4.1.0&q=85',
                'width': 1280,
                'height': 720
            }
        ],
        'category': 'education',
        'tags': ['javascript', 'programming', 'web development', 'tutorial'],
        'status': 'published',
        'metrics': {
            'views': 2500000,
            'likes': 125000,
            'dislikes': 2300,
            'comments_count': 1500,
            'shares': 8500,
            'engagement_rate': 0.054
        },
        'trending_score': 95.5,
        'created_at': datetime.utcnow() - timedelta(hours=2),
        'updated_at': datetime.utcnow() - timedelta(hours=2),
        'version': 1
    },
    {
        '_id': ObjectId(),
        'title': 'React Advanced Patterns and Best Practices',
        'description': 'Advanced React patterns, performance optimization, and production-ready techniques.',
        'channel_id': MOCK_DATA['users'][1]['_id'],
        'channel_name': 'React Pro',
        'channel_avatar': MOCK_DATA['users'][1]['avatar_url'],
        'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        'youtube_embed_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        'duration_seconds': 8141,
        'thumbnails': [
            {
                'url': 'https://images.unsplash.com/photo-1531297484001-80022131f5a1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MHwxfHNlYXJjaHwyfHx0ZWNobm9sb2d5fGVufDB8fHx8MTc1NTQyOTYxNXww&ixlib=rb-4.1.0&q=85',
                'width': 1280,
                'height': 720
            }
        ],
        'category': 'education',
        'tags': ['react', 'javascript', 'frontend', 'patterns', 'optimization'],
        'status': 'published',
        'metrics': {
            'views': 890000,
            'likes': 45000,
            'dislikes': 800,
            'comments_count': 750,
            'shares': 3200,
            'engagement_rate': 0.055
        },
        'trending_score': 82.3,
        'created_at': datetime.utcnow() - timedelta(hours=5),
        'updated_at': datetime.utcnow() - timedelta(hours=5),
        'version': 1
    }
]

# Add more videos with different categories
additional_videos = [
    {
        'title': 'AI and Machine Learning Fundamentals',
        'description': 'Comprehensive introduction to artificial intelligence and machine learning concepts.',
        'channel_id': MOCK_DATA['users'][0]['_id'],
        'channel_name': 'CodeMaster',
        'thumbnail': 'https://images.unsplash.com/photo-1649972904349-6e44c42644a7?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2MzR8MXwxfHNlYXJjaHwxfHx0ZWNobm9sb2d5fGVufDB8fHx8MTc1NTQyOTYxNXww&ixlib=rb-4.1.0&q=85',
        'category': 'technology',
        'tags': ['ai', 'machine learning', 'python', 'data science'],
        'duration_seconds': 15735,
        'views': 1800000,
        'likes': 95000,
        'days_ago': 7
    },
    {
        'title': 'Web Development Project - Build a Full Stack App',
        'description': 'Build a complete full-stack application from scratch using modern technologies.',
        'channel_id': MOCK_DATA['users'][1]['_id'],
        'channel_name': 'React Pro',
        'thumbnail': 'https://images.pexels.com/photos/5077064/pexels-photo-5077064.jpeg',
        'category': 'education',
        'tags': ['fullstack', 'web development', 'javascript', 'node.js'],
        'duration_seconds': 19992,
        'views': 567000,
        'likes': 38000,
        'days_ago': 3
    }
]

for video_data in additional_videos:
    video = {
        '_id': ObjectId(),
        'title': video_data['title'],
        'description': video_data['description'],
        'channel_id': video_data['channel_id'],
        'channel_name': video_data['channel_name'],
        'channel_avatar': MOCK_DATA['users'][0]['avatar_url'] if video_data['channel_name'] == 'CodeMaster' else MOCK_DATA['users'][1]['avatar_url'],
        'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        'youtube_embed_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        'duration_seconds': video_data['duration_seconds'],
        'thumbnails': [
            {
                'url': video_data['thumbnail'],
                'width': 1280,
                'height': 720
            }
        ],
        'category': video_data['category'],
        'tags': video_data['tags'],
        'status': 'published',
        'metrics': {
            'views': video_data['views'],
            'likes': video_data['likes'],
            'dislikes': video_data['likes'] // 50,  # Simple ratio
            'comments_count': video_data['likes'] // 100,
            'shares': video_data['likes'] // 20,
            'engagement_rate': 0.05
        },
        'trending_score': 75.0,
        'created_at': datetime.utcnow() - timedelta(hours=video_data['days_ago']),
        'updated_at': datetime.utcnow() - timedelta(hours=video_data['days_ago']),
        'version': 1
    }
    MOCK_DATA['videos'].append(video)


async def populate_database():
    """Populate database with mock data"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        logger.info("Connected to MongoDB")
        
        # Clear existing data
        await db.users.delete_many({})
        await db.videos.delete_many({})
        await db.comments.delete_many({})
        logger.info("Cleared existing data")
        
        # Insert users
        await db.users.insert_many(MOCK_DATA['users'])
        logger.info(f"Inserted {len(MOCK_DATA['users'])} users")
        
        # Insert videos
        await db.videos.insert_many(MOCK_DATA['videos'])
        logger.info(f"Inserted {len(MOCK_DATA['videos'])} videos")
        
        # Create indexes
        await db.users.create_index([('email', 1)], unique=True)
        await db.users.create_index([('username', 1)], unique=True)
        await db.videos.create_index([('channel_id', 1)])
        await db.videos.create_index([('category', 1), ('created_at', -1)])
        await db.videos.create_index([('trending_score', -1)])
        
        logger.info("✅ Database populated successfully!")
        
        # Close connection
        client.close()
        
    except Exception as e:
        logger.error(f"❌ Error populating database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(populate_database())