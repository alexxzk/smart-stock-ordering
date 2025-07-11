"""
Redis-based caching system for production deployment
"""

import time
import logging
import json
import os
from typing import Dict, Any, Optional
from functools import wraps
import redis

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize Redis cache with connection"""
        # Check if we're in dev mode
        if os.getenv("DEV_MODE", "false").lower() == "true":
            logger.info("✅ Redis cache initialized in dev mode (mock)")
            self.redis = None
            return
            
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        try:
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis.ping()
            logger.info("✅ Redis cache connected successfully")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.redis = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        if not self.redis:
            return None
        
        try:
            value = self.redis.get(key)
            if value:
                logger.info(f"[CACHE] Hit for key: {key}")
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in Redis cache with TTL"""
        if not self.redis:
            return
        
        try:
            ttl = ttl or 300  # 5 minutes default
            serialized_value = json.dumps(value)
            self.redis.setex(key, ttl, serialized_value)
            logger.info(f"[CACHE] Set for key: {key}, TTL: {ttl}s")
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    def delete(self, key: str) -> None:
        """Delete key from Redis cache"""
        if not self.redis:
            return
        
        try:
            self.redis.delete(key)
            logger.info(f"[CACHE] Deleted key: {key}")
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
    
    def clear(self) -> None:
        """Clear all cache (use with caution in production)"""
        if not self.redis:
            return
        
        try:
            self.redis.flushdb()
            logger.info("[CACHE] Cleared all cache")
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.redis:
            return {"error": "Redis not connected"}
        
        try:
            info = self.redis.info()
            return {
                "connected": True,
                "keys": info.get('db0', {}).get('keys', 0),
                "memory_usage": info.get('used_memory_human', 'N/A'),
                "uptime": info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            return {"error": f"Failed to get stats: {e}"}

# Global Redis cache instance
redis_cache = RedisCache()

def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator to cache function results in Redis"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            start_time = time.time()
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Cache the result
            redis_cache.set(cache_key, result, ttl)
            
            logger.info(f"[CACHE] Cached {func.__name__} result in {duration:.3f}s")
            return result
        
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """Invalidate cache entries matching pattern"""
    if not redis_cache.redis:
        return
    
    try:
        keys = redis_cache.redis.keys(f"*{pattern}*")
        if keys:
            redis_cache.redis.delete(*keys)
            logger.info(f"[CACHE] Invalidated {len(keys)} cache entries matching: {pattern}")
    except Exception as e:
        logger.error(f"Cache invalidation error: {e}") 