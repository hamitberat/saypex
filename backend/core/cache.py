import json
import pickle
import logging
from typing import Any, Optional, Union, Dict
from datetime import timedelta
import redis.asyncio as redis
import os
from functools import wraps

logger = logging.getLogger(__name__)


class CacheManager:
    """Enterprise-grade Redis cache manager"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        
    async def connect(self):
        """Connect to Redis with enterprise settings"""
        try:
            self.redis_client = redis.from_url(
                self._redis_url,
                encoding='utf-8',
                decode_responses=False,  # We'll handle encoding manually
                max_connections=50,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Connected to Redis cache")
            
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Cache will be disabled.")
            self.redis_client = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        if not self.redis_client:
            return default
        
        try:
            data = await self.redis_client.get(key)
            if data is None:
                return default
            
            # Try to unpickle first (for complex objects), then fall back to JSON
            try:
                return pickle.loads(data)
            except (pickle.PickleError, TypeError):
                return json.loads(data.decode('utf-8'))
                
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in cache"""
        if not self.redis_client:
            return False
        
        try:
            # Try to serialize as JSON first, then fall back to pickle
            try:
                serialized_data = json.dumps(value).encode('utf-8')
            except (TypeError, ValueError):
                serialized_data = pickle.dumps(value)
            
            if expire:
                if isinstance(expire, timedelta):
                    expire = int(expire.total_seconds())
                await self.redis_client.setex(key, expire, serialized_data)
            else:
                await self.redis_client.set(key, serialized_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for pattern {pattern}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis_client:
            return False
        
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter in cache"""
        if not self.redis_client:
            return None
        
        try:
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None
    
    async def set_hash(self, key: str, mapping: Dict[str, Any], expire: Optional[int] = None) -> bool:
        """Set hash in cache"""
        if not self.redis_client:
            return False
        
        try:
            # Serialize values in the mapping
            serialized_mapping = {}
            for k, v in mapping.items():
                try:
                    serialized_mapping[k] = json.dumps(v)
                except (TypeError, ValueError):
                    serialized_mapping[k] = pickle.dumps(v).hex()
            
            await self.redis_client.hset(key, mapping=serialized_mapping)
            
            if expire:
                await self.redis_client.expire(key, expire)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set hash error for key {key}: {e}")
            return False
    
    async def get_hash(self, key: str, field: str) -> Any:
        """Get field from hash"""
        if not self.redis_client:
            return None
        
        try:
            data = await self.redis_client.hget(key, field)
            if data is None:
                return None
            
            # Try JSON first, then pickle
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return pickle.loads(bytes.fromhex(data))
                
        except Exception as e:
            logger.error(f"Cache get hash error for key {key}, field {field}: {e}")
            return None


# Global cache manager instance
cache_manager = CacheManager()


async def get_cache() -> CacheManager:
    """Get cache manager instance"""
    if not cache_manager.redis_client:
        await cache_manager.connect()
    return cache_manager


async def init_cache():
    """Initialize cache connection"""
    await cache_manager.connect()


async def close_cache():
    """Close cache connection"""
    await cache_manager.disconnect()


def cache_result(
    key_prefix: str, 
    expire: Union[int, timedelta] = timedelta(minutes=15),
    vary_on: Optional[list] = None
):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            cache_key_parts = [key_prefix]
            
            if vary_on:
                for param in vary_on:
                    if param in kwargs:
                        cache_key_parts.append(f"{param}:{kwargs[param]}")
            else:
                # Include all arguments in cache key
                cache_key_parts.extend([str(arg) for arg in args])
                cache_key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            
            cache_key = ":".join(cache_key_parts)
            
            # Try to get from cache first
            cache = await get_cache()
            cached_result = await cache.get(cache_key)
            
            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, expire)
            logger.debug(f"Cache miss - stored result for key: {cache_key}")
            
            return result
        
        return wrapper
    return decorator