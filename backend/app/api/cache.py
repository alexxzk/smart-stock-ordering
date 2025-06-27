"""
Cache management API endpoints - Production Redis version
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from app.cache_redis import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """Get Redis cache statistics"""
    try:
        stats = redis_cache.get_stats()
        return {
            "success": True,
            "cache_type": "Redis",
            "stats": stats,
            "message": f"Redis cache status: {stats.get('connected', False)}"
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")

@router.post("/clear")
async def clear_cache() -> Dict[str, Any]:
    """Clear all Redis cache"""
    try:
        redis_cache.clear()
        return {
            "success": True,
            "message": "Redis cache cleared successfully"
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

@router.post("/clear/{pattern}")
async def clear_cache_pattern(pattern: str) -> Dict[str, Any]:
    """Clear cache entries matching pattern"""
    try:
        from app.cache_redis import invalidate_cache
        invalidate_cache(pattern)
        return {
            "success": True,
            "pattern": pattern,
            "message": f"Cache entries matching '{pattern}' cleared successfully"
        }
    except Exception as e:
        logger.error(f"Error clearing cache pattern {pattern}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing cache pattern: {str(e)}")

@router.get("/health")
async def cache_health() -> Dict[str, Any]:
    """Check Redis cache health"""
    try:
        stats = redis_cache.get_stats()
        is_healthy = stats.get('connected', False)
        
        return {
            "healthy": is_healthy,
            "cache_type": "Redis",
            "details": stats
        }
    except Exception as e:
        return {
            "healthy": False,
            "cache_type": "Redis",
            "error": str(e)
        } 