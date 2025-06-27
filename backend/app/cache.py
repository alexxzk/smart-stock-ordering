"""
Caching system for improved performance
"""

import time
import logging
from typing import Dict, Any, Optional
from functools import wraps
import threading

logger = logging.getLogger(__name__)

class Cache:
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        with self._lock:
            if key in self._cache:
                item = self._cache[key]
                if time.time() < item['expires']:
                    logger.info(f"[CACHE] Hit for key: {key}")
                    return item['value']
                else:
                    # Expired, remove it
                    del self._cache[key]
                    logger.info(f"[CACHE] Expired for key: {key}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        with self._lock:
            ttl = ttl or self.default_ttl
            self._cache[key] = {
                'value': value,
                'expires': time.time() + ttl
            }
            logger.info(f"[CACHE] Set for key: {key}, TTL: {ttl}s")
    
    def delete(self, key: str) -> None:
        """Delete key from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.info(f"[CACHE] Deleted key: {key}")
    
    def clear(self) -> None:
        """Clear all cache"""
        with self._lock:
            self._cache.clear()
            logger.info("[CACHE] Cleared all cache")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            return {
                'size': len(self._cache),
                'keys': list(self._cache.keys())
            }

# Global cache instance
cache = Cache()

def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            start_time = time.time()
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Cache the result
            cache.set(cache_key, result, ttl)
            
            logger.info(f"[CACHE] Cached {func.__name__} result in {duration:.3f}s")
            return result
        
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """Invalidate cache entries matching pattern"""
    stats = cache.get_stats()
    for key in stats['keys']:
        if pattern in key:
            cache.delete(key)
    logger.info(f"[CACHE] Invalidated cache entries matching: {pattern}") 