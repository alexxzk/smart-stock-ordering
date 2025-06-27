#!/usr/bin/env python3
"""
Quick Inventory Speed Test
Test inventory addition performance specifically
"""

import requests
import time
import json
from typing import List, Dict

BASE_URL = "http://localhost:8000"

# Sample inventory items for testing
SAMPLE_ITEMS = [
    {
        "name": "Coffee Beans Premium",
        "category": "Beverages",
        "currentStock": 25.0,
        "minStock": 10.0,
        "maxStock": 100.0,
        "unit": "kg",
        "costPerUnit": 18.50,
        "supplierId": "supplier-1"
    },
    {
        "name": "Organic Milk",
        "category": "Dairy",
        "currentStock": 15.0,
        "minStock": 5.0,
        "maxStock": 50.0,
        "unit": "liters",
        "costPerUnit": 3.25,
        "supplierId": "supplier-2"
    },
    {
        "name": "Artisan Bread",
        "category": "Bakery",
        "currentStock": 30.0,
        "minStock": 15.0,
        "maxStock": 80.0,
        "unit": "pieces",
        "costPerUnit": 4.50,
        "supplierId": "supplier-3"
    }
]

def test_inventory_addition():
    """Test inventory addition performance"""
    print("🚀 Testing Inventory Addition Performance")
    print("=" * 50)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("Make sure backend is running on http://localhost:8000")
        return
    
    print("✅ Backend is running")
    
    # Test single inventory addition
    print("\n📦 Testing Single Inventory Addition...")
    times = []
    errors = 0
    
    for i, item in enumerate(SAMPLE_ITEMS):
        item_name = f"{item['name']} Test {i+1}"
        test_item = {**item, "name": item_name}
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/inventory/",
                json=test_item,
                timeout=10
            )
            end_time = time.time()
            
            if response.status_code == 200:
                duration = end_time - start_time
                times.append(duration)
                print(f"✅ Added '{item_name}' in {duration:.3f}s")
            else:
                errors += 1
                print(f"❌ Failed to add '{item_name}': {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            errors += 1
            print(f"❌ Error adding '{item_name}': {e}")
    
    # Test bulk addition (simulate multiple rapid requests)
    print("\n⚡ Testing Rapid Successive Additions...")
    rapid_times = []
    
    for i in range(5):
        item_name = f"Rapid Test Item {i+1}"
        test_item = {
            "name": item_name,
            "category": "Test",
            "currentStock": 10.0,
            "minStock": 5.0,
            "maxStock": 20.0,
            "unit": "units",
            "costPerUnit": 1.0,
            "supplierId": "test-supplier"
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/inventory/",
                json=test_item,
                timeout=5
            )
            end_time = time.time()
            
            if response.status_code == 200:
                duration = end_time - start_time
                rapid_times.append(duration)
                print(f"✅ Rapid add '{item_name}' in {duration:.3f}s")
            else:
                print(f"❌ Rapid add failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Rapid add error: {e}")
    
    # Test inventory retrieval
    print("\n📋 Testing Inventory Retrieval...")
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/inventory/", timeout=10)
        end_time = time.time()
        
        if response.status_code == 200:
            duration = end_time - start_time
            data = response.json()
            print(f"✅ Retrieved {len(data)} items in {duration:.3f}s")
        else:
            print(f"❌ Failed to retrieve inventory: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error retrieving inventory: {e}")
    
    # Performance analysis
    print("\n📊 Performance Analysis")
    print("=" * 30)
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"Single Additions ({len(times)} tests):")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Minimum: {min_time:.3f}s")
        print(f"  Maximum: {max_time:.3f}s")
        
        if avg_time > 1.0:
            print("  ⚠️  SLOW: Average time > 1s")
        elif avg_time > 0.5:
            print("  ⚠️  MODERATE: Average time > 0.5s")
        else:
            print("  ✅ FAST: Good performance")
    
    if rapid_times:
        avg_rapid = sum(rapid_times) / len(rapid_times)
        print(f"\nRapid Additions ({len(rapid_times)} tests):")
        print(f"  Average: {avg_rapid:.3f}s")
        
        if avg_rapid > 0.5:
            print("  ⚠️  SLOW: Rapid additions taking too long")
        else:
            print("  ✅ FAST: Good rapid addition performance")
    
    if errors > 0:
        print(f"\n❌ Errors: {errors} out of {len(SAMPLE_ITEMS)} tests failed")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if times and avg_time > 1.0:
        print("- ⚠️  Inventory addition is slow. Check:")
        print("  1. Firebase indexes (most common cause)")
        print("  2. Network latency to Firestore")
        print("  3. Backend processing time")
    elif times and avg_time > 0.5:
        print("- ⚠️  Moderate performance. Consider:")
        print("  1. Adding Firebase indexes")
        print("  2. Implementing caching")
    else:
        print("- ✅ Performance looks good!")
    
    print("\n🔧 Next steps:")
    print("1. Check backend logs for [PERF] entries")
    print("2. Create Firebase indexes if needed")
    print("3. Monitor Firestore usage in Firebase Console")

if __name__ == "__main__":
    test_inventory_addition() 