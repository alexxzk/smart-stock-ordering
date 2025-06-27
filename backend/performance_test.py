#!/usr/bin/env python3
"""
Performance Testing Script for Smart Stock Ordering API
Run this to identify performance bottlenecks
"""

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict
import json

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = "test-user"

# Test data
SAMPLE_INVENTORY_ITEM = {
    "name": "Test Coffee Beans",
    "category": "Beverages",
    "currentStock": 10.0,
    "minStock": 5.0,
    "maxStock": 50.0,
    "unit": "kg",
    "costPerUnit": 15.0,
    "supplierId": "test-supplier"
}

SAMPLE_SUPPLIER = {
    "name": "Test Supplier",
    "contact_person": "John Doe",
    "email": "john@testsupplier.com",
    "phone": "+1234567890",
    "address": "123 Test St, Test City",
    "payment_terms": "Net 30",
    "delivery_lead_time": 3,
    "minimum_order": 100.0,
    "categories": ["Beverages", "Food"]
}

class PerformanceTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = {}
        
    async def test_endpoint(self, session: aiohttp.ClientSession, endpoint: str, method: str = "GET", data: Dict = None, iterations: int = 10) -> Dict:
        """Test a single endpoint multiple times and return performance stats"""
        times = []
        errors = 0
        
        for i in range(iterations):
            start_time = time.time()
            try:
                if method == "GET":
                    async with session.get(f"{self.base_url}{endpoint}") as response:
                        await response.text()
                elif method == "POST":
                    async with session.post(f"{self.base_url}{endpoint}", json=data) as response:
                        await response.text()
                elif method == "PUT":
                    async with session.put(f"{self.base_url}{endpoint}", json=data) as response:
                        await response.text()
                elif method == "DELETE":
                    async with session.delete(f"{self.base_url}{endpoint}") as response:
                        await response.text()
                
                if response.status >= 400:
                    errors += 1
                    print(f"Error {response.status} for {endpoint}")
                    
            except Exception as e:
                errors += 1
                print(f"Exception for {endpoint}: {e}")
                
            end_time = time.time()
            times.append(end_time - start_time)
            
            # Small delay between requests
            await asyncio.sleep(0.1)
        
        if times:
            return {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "errors": errors,
                "success_rate": ((iterations - errors) / iterations) * 100,
                "min_time": min(times),
                "max_time": max(times),
                "avg_time": statistics.mean(times),
                "median_time": statistics.median(times),
                "p95_time": statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times),
                "p99_time": statistics.quantiles(times, n=100)[98] if len(times) >= 100 else max(times),
                "all_times": times
            }
        else:
            return {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "errors": errors,
                "success_rate": 0,
                "error": "No successful requests"
            }
    
    async def run_all_tests(self):
        """Run comprehensive performance tests"""
        print("🚀 Starting Performance Tests...")
        print(f"Base URL: {self.base_url}")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            # Test basic endpoints
            basic_endpoints = [
                ("/health", "GET"),
                ("/inventory/", "GET"),
                ("/suppliers/", "GET"),
                ("/orders/", "GET"),
            ]
            
            print("📊 Testing Basic Endpoints...")
            for endpoint, method in basic_endpoints:
                result = await self.test_endpoint(session, endpoint, method)
                self.results[endpoint] = result
                self._print_result(result)
            
            # Test inventory operations
            print("\n📦 Testing Inventory Operations...")
            
            # Create inventory item
            create_result = await self.test_endpoint(
                session, "/inventory/", "POST", SAMPLE_INVENTORY_ITEM, iterations=5
            )
            self.results["inventory_create"] = create_result
            self._print_result(create_result)
            
            # Get inventory items
            get_result = await self.test_endpoint(session, "/inventory/", "GET", iterations=10)
            self.results["inventory_get"] = get_result
            self._print_result(get_result)
            
            # Test suppliers operations
            print("\n🏢 Testing Supplier Operations...")
            
            # Create supplier
            create_supplier_result = await self.test_endpoint(
                session, "/suppliers/", "POST", SAMPLE_SUPPLIER, iterations=5
            )
            self.results["supplier_create"] = create_supplier_result
            self._print_result(create_supplier_result)
            
            # Get suppliers
            get_suppliers_result = await self.test_endpoint(session, "/suppliers/", "GET", iterations=10)
            self.results["suppliers_get"] = get_suppliers_result
            self._print_result(get_suppliers_result)
            
            # Test concurrent load
            print("\n⚡ Testing Concurrent Load...")
            await self._test_concurrent_load(session)
    
    async def _test_concurrent_load(self, session: aiohttp.ClientSession):
        """Test concurrent requests to simulate multiple users"""
        endpoints = ["/inventory/", "/suppliers/", "/orders/"]
        concurrent_users = 5
        
        async def concurrent_request(endpoint: str):
            return await self.test_endpoint(session, endpoint, "GET", iterations=3)
        
        start_time = time.time()
        tasks = []
        for _ in range(concurrent_users):
            for endpoint in endpoints:
                tasks.append(concurrent_request(endpoint))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        total_time = end_time - start_time
        successful_results = [r for r in results if isinstance(r, dict)]
        
        if successful_results:
            avg_times = [r["avg_time"] for r in successful_results]
            print(f"Concurrent test completed in {total_time:.2f}s")
            print(f"Average response time across {len(successful_results)} requests: {statistics.mean(avg_times):.3f}s")
            print(f"Total requests: {len(successful_results) * 3}")
    
    def _print_result(self, result: Dict):
        """Print formatted test result"""
        if "error" in result:
            print(f"❌ {result['endpoint']}: {result['error']}")
            return
            
        status = "✅" if result["success_rate"] >= 95 else "⚠️" if result["success_rate"] >= 80 else "❌"
        
        print(f"{status} {result['method']} {result['endpoint']}")
        print(f"   Success Rate: {result['success_rate']:.1f}% ({result['iterations'] - result['errors']}/{result['iterations']})")
        print(f"   Avg Time: {result['avg_time']:.3f}s | Median: {result['median_time']:.3f}s")
        print(f"   P95: {result['p95_time']:.3f}s | P99: {result['p99_time']:.3f}s")
        
        # Highlight slow endpoints
        if result['avg_time'] > 1.0:
            print(f"   ⚠️  SLOW: Average time > 1s")
        elif result['avg_time'] > 0.5:
            print(f"   ⚠️  MODERATE: Average time > 0.5s")
    
    def generate_report(self):
        """Generate a comprehensive performance report"""
        print("\n" + "=" * 60)
        print("📋 PERFORMANCE REPORT")
        print("=" * 60)
        
        # Find slowest endpoints
        slow_endpoints = []
        for endpoint, result in self.results.items():
            if "avg_time" in result:
                slow_endpoints.append((endpoint, result["avg_time"]))
        
        slow_endpoints.sort(key=lambda x: x[1], reverse=True)
        
        print("\n🐌 SLOWEST ENDPOINTS:")
        for endpoint, avg_time in slow_endpoints[:5]:
            print(f"   {endpoint}: {avg_time:.3f}s")
        
        # Find endpoints with errors
        error_endpoints = []
        for endpoint, result in self.results.items():
            if result.get("errors", 0) > 0:
                error_endpoints.append((endpoint, result["errors"], result["iterations"]))
        
        if error_endpoints:
            print("\n❌ ENDPOINTS WITH ERRORS:")
            for endpoint, errors, total in error_endpoints:
                print(f"   {endpoint}: {errors}/{total} errors ({errors/total*100:.1f}%)")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        for endpoint, result in self.results.items():
            if "avg_time" in result:
                if result["avg_time"] > 1.0:
                    print(f"   • {endpoint}: Consider caching or database optimization")
                elif result["avg_time"] > 0.5:
                    print(f"   • {endpoint}: Monitor for performance degradation")
        
        # Save detailed results
        with open("performance_results.json", "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n📄 Detailed results saved to performance_results.json")

async def main():
    """Main function to run performance tests"""
    tester = PerformanceTester()
    await tester.run_all_tests()
    tester.generate_report()

if __name__ == "__main__":
    print("🔧 Smart Stock Ordering API Performance Tester")
    print("Make sure your backend is running on http://localhost:8000")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Performance testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during performance testing: {e}")
        print("Make sure your backend is running and accessible") 