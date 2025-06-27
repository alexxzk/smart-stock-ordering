#!/usr/bin/env python3
"""
Performance test script to measure speed improvements
"""

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any

BASE_URL = "http://localhost:8000"

async def test_endpoint(session: aiohttp.ClientSession, endpoint: str, iterations: int = 5) -> Dict[str, Any]:
    """Test an endpoint multiple times and return performance stats"""
    times = []
    errors = 0
    
    print(f"Testing {endpoint}...")
    
    for i in range(iterations):
        start_time = time.time()
        try:
            async with session.get(f"{BASE_URL}{endpoint}") as response:
                if response.status == 200:
                    duration = time.time() - start_time
                    times.append(duration)
                    print(f"  Request {i+1}: {duration:.3f}s")
                else:
                    errors += 1
                    print(f"  Request {i+1}: Error {response.status}")
        except Exception as e:
            errors += 1
            print(f"  Request {i+1}: Exception {str(e)}")
    
    if times:
        return {
            "endpoint": endpoint,
            "iterations": iterations,
            "successful_requests": len(times),
            "errors": errors,
            "min_time": min(times),
            "max_time": max(times),
            "avg_time": statistics.mean(times),
            "median_time": statistics.median(times),
            "times": times
        }
    else:
        return {
            "endpoint": endpoint,
            "iterations": iterations,
            "successful_requests": 0,
            "errors": errors,
            "min_time": None,
            "max_time": None,
            "avg_time": None,
            "median_time": None,
            "times": []
        }

async def test_cache_effect():
    """Test the effect of caching on performance"""
    async with aiohttp.ClientSession() as session:
        endpoints = [
            "/api/inventory/",
            "/api/suppliers/",
            "/api/forecasting/models"
        ]
        
        print("🚀 PERFORMANCE TEST - CACHE EFFECT")
        print("=" * 50)
        
        # Test without cache (first run)
        print("\n📊 FIRST RUN (No Cache):")
        print("-" * 30)
        first_run_results = []
        for endpoint in endpoints:
            result = await test_endpoint(session, endpoint, 3)
            first_run_results.append(result)
        
        # Test with cache (subsequent runs)
        print("\n📊 SUBSEQUENT RUNS (With Cache):")
        print("-" * 30)
        cached_results = []
        for endpoint in endpoints:
            result = await test_endpoint(session, endpoint, 5)
            cached_results.append(result)
        
        # Compare results
        print("\n📈 PERFORMANCE COMPARISON:")
        print("=" * 50)
        
        for i, endpoint in enumerate(endpoints):
            first = first_run_results[i]
            cached = cached_results[i]
            
            if first["avg_time"] and cached["avg_time"]:
                improvement = ((first["avg_time"] - cached["avg_time"]) / first["avg_time"]) * 100
                print(f"\n{endpoint}:")
                print(f"  First run avg: {first['avg_time']:.3f}s")
                print(f"  Cached avg:    {cached['avg_time']:.3f}s")
                print(f"  Improvement:   {improvement:.1f}%")
            else:
                print(f"\n{endpoint}: Error in testing")

async def test_cache_management():
    """Test cache management endpoints"""
    async with aiohttp.ClientSession() as session:
        print("\n🔧 CACHE MANAGEMENT TEST:")
        print("=" * 50)
        
        # Get cache stats
        print("\nGetting cache stats...")
        try:
            async with session.get(f"{BASE_URL}/api/cache/stats") as response:
                if response.status == 200:
                    stats = await response.json()
                    print(f"Cache size: {stats.get('cache_size', 'N/A')}")
                    print(f"Cached keys: {stats.get('cached_keys', [])}")
                else:
                    print(f"Error getting cache stats: {response.status}")
        except Exception as e:
            print(f"Exception getting cache stats: {str(e)}")
        
        # Clear cache
        print("\nClearing cache...")
        try:
            async with session.post(f"{BASE_URL}/api/cache/clear") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"Cache cleared: {result.get('message', 'N/A')}")
                else:
                    print(f"Error clearing cache: {response.status}")
        except Exception as e:
            print(f"Exception clearing cache: {str(e)}")

async def main():
    """Run all performance tests"""
    print("🧪 SMART STOCK ORDERING - PERFORMANCE TEST")
    print("=" * 60)
    
    # Test basic connectivity
    print("\n🔍 Testing connectivity...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    print("✅ Backend is running and healthy")
                else:
                    print(f"❌ Backend health check failed: {response.status}")
                    return
        except Exception as e:
            print(f"❌ Cannot connect to backend: {str(e)}")
            return
    
    # Run performance tests
    await test_cache_effect()
    await test_cache_management()
    
    print("\n✅ Performance test completed!")

if __name__ == "__main__":
    asyncio.run(main()) 