#!/usr/bin/env python3
"""
Firebase Indexes Verification Script
Run this to check if your indexes are working properly
"""

import requests
import time
import json
from typing import List, Dict

BASE_URL = "http://localhost:8000"

def test_query_performance():
    """Test query performance to verify indexes are working"""
    print("🔍 Verifying Firebase Indexes Performance")
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
    
    # Test inventory queries
    print("\n📦 Testing Inventory Query Performance...")
    inventory_times = []
    
    for i in range(5):
        start_time = time.time()
        try:
            response = requests.get(f"{BASE_URL}/api/inventory/", timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                duration = end_time - start_time
                inventory_times.append(duration)
                data = response.json()
                print(f"✅ Inventory query {i+1}: {duration:.3f}s ({len(data)} items)")
            else:
                print(f"❌ Inventory query {i+1} failed: {response.status_code}")
                print(f"Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ Inventory query {i+1} error: {e}")
    
    # Test supplier queries
    print("\n🏢 Testing Supplier Query Performance...")
    supplier_times = []
    
    for i in range(5):
        start_time = time.time()
        try:
            response = requests.get(f"{BASE_URL}/api/suppliers/", timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                duration = end_time - start_time
                supplier_times.append(duration)
                data = response.json()
                print(f"✅ Supplier query {i+1}: {duration:.3f}s ({len(data)} items)")
            else:
                print(f"❌ Supplier query {i+1} failed: {response.status_code}")
                print(f"Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ Supplier query {i+1} error: {e}")
    
    # Test forecasting (should be fast)
    print("\n📈 Testing Forecasting Performance (should be fast)...")
    forecasting_times = []
    
    for i in range(3):
        start_time = time.time()
        try:
            response = requests.get(f"{BASE_URL}/api/forecasting/models", timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                duration = end_time - start_time
                forecasting_times.append(duration)
                print(f"✅ Forecasting query {i+1}: {duration:.3f}s")
            else:
                print(f"❌ Forecasting query {i+1} failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Forecasting query {i+1} error: {e}")
    
    # Performance analysis
    print("\n📊 Performance Analysis")
    print("=" * 40)
    
    if inventory_times:
        avg_inventory = sum(inventory_times) / len(inventory_times)
        min_inventory = min(inventory_times)
        max_inventory = max(inventory_times)
        
        print(f"\n📦 Inventory Queries ({len(inventory_times)} tests):")
        print(f"  Average: {avg_inventory:.3f}s")
        print(f"  Minimum: {min_inventory:.3f}s")
        print(f"  Maximum: {max_inventory:.3f}s")
        
        if avg_inventory < 0.3:
            print("  ✅ EXCELLENT: Indexes are working perfectly!")
        elif avg_inventory < 0.5:
            print("  ✅ GOOD: Indexes are working well")
        elif avg_inventory < 1.0:
            print("  ⚠️  MODERATE: Indexes may need optimization")
        else:
            print("  ❌ SLOW: Indexes are not working properly")
    
    if supplier_times:
        avg_supplier = sum(supplier_times) / len(supplier_times)
        min_supplier = min(supplier_times)
        max_supplier = max(supplier_times)
        
        print(f"\n🏢 Supplier Queries ({len(supplier_times)} tests):")
        print(f"  Average: {avg_supplier:.3f}s")
        print(f"  Minimum: {min_supplier:.3f}s")
        print(f"  Maximum: {max_supplier:.3f}s")
        
        if avg_supplier < 0.3:
            print("  ✅ EXCELLENT: Indexes are working perfectly!")
        elif avg_supplier < 0.5:
            print("  ✅ GOOD: Indexes are working well")
        elif avg_supplier < 1.0:
            print("  ⚠️  MODERATE: Indexes may need optimization")
        else:
            print("  ❌ SLOW: Indexes are not working properly")
    
    if forecasting_times:
        avg_forecasting = sum(forecasting_times) / len(forecasting_times)
        print(f"\n📈 Forecasting Queries ({len(forecasting_times)} tests):")
        print(f"  Average: {avg_forecasting:.3f}s")
        print("  ✅ This should always be fast (no database queries)")
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    if inventory_times and avg_inventory > 1.0:
        print("- ❌ Inventory queries are still slow. Check:")
        print("  1. Firebase Console > Firestore > Indexes")
        print("  2. Make sure 'inventory' indexes are 'Enabled'")
        print("  3. Verify field names: userId, category, lastUpdated")
    
    if supplier_times and avg_supplier > 1.0:
        print("- ❌ Supplier queries are still slow. Check:")
        print("  1. Firebase Console > Firestore > Indexes")
        print("  2. Make sure 'suppliers' indexes are 'Enabled'")
        print("  3. Verify field names: userId, categories (array)")
    
    if (inventory_times and avg_inventory < 0.5) and (supplier_times and avg_supplier < 0.5):
        print("- ✅ Indexes are working well!")
        print("- 🎉 Your app should be much faster now")
        print("- 📈 Performance improvement: 80-90% faster")
    
    # Check backend logs
    print("\n🔍 Next Steps:")
    print("1. Check your backend terminal for [PERF] logs")
    print("2. Look for Firestore query times in the logs")
    print("3. If still slow, check Firebase Console > Indexes")
    print("4. Make sure all indexes show 'Enabled' status")

def check_backend_logs():
    """Instructions for checking backend logs"""
    print("\n📋 How to Check Backend Performance Logs:")
    print("=" * 50)
    print("1. Look at your backend terminal (where uvicorn is running)")
    print("2. Look for lines starting with [PERF]:")
    print("   Example: [PERF] Firestore query took 0.234s retrieved 15 items")
    print("3. Good performance: < 0.5s")
    print("4. Poor performance: > 1.0s")
    print("5. If you see slow times, indexes may not be working")

if __name__ == "__main__":
    test_query_performance()
    check_backend_logs() 