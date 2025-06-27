#!/usr/bin/env python3
"""
Quick Performance Setup Script
Run this to implement immediate performance improvements
"""

import os
import sys
import subprocess
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_backend_running():
    """Check if backend is running"""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🚀 Smart Stock Ordering - Performance Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app"):
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Check if backend is running
    print("🔍 Checking if backend is running...")
    if not check_backend_running():
        print("❌ Backend is not running. Please start it first:")
        print("   cd backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        sys.exit(1)
    else:
        print("✅ Backend is running")
    
    # Install new dependencies
    print("\n📦 Installing performance dependencies...")
    if not run_command("pip install aiohttp==3.9.1", "Installing aiohttp"):
        print("⚠️  Continuing without aiohttp (performance testing will not work)")
    
    # Create Firebase indexes guide
    print("\n📋 Creating Firebase indexes guide...")
    indexes_guide = """
# Firebase Indexes to Create

Go to Firebase Console > Firestore > Indexes and create these composite indexes:

## Inventory Collection
1. Collection: inventory
   - Fields: userId (Ascending), category (Ascending)
   - Query scope: Collection

2. Collection: inventory  
   - Fields: userId (Ascending), lastUpdated (Descending)
   - Query scope: Collection

3. Collection: inventory
   - Fields: userId (Ascending), currentStock (Ascending)
   - Query scope: Collection

## Suppliers Collection
1. Collection: suppliers
   - Fields: userId (Ascending), categories (Array contains)
   - Query scope: Collection

2. Collection: suppliers
   - Fields: userId (Ascending), name (Ascending)
   - Query scope: Collection

## Orders Collection
1. Collection: orders
   - Fields: userId (Ascending), createdAt (Descending)
   - Query scope: Collection

2. Collection: orders
   - Fields: userId (Ascending), status (Ascending)
   - Query scope: Collection

These indexes will significantly improve query performance!
"""
    
    with open("firebase_indexes_guide.md", "w") as f:
        f.write(indexes_guide)
    print("✅ Firebase indexes guide created")
    
    # Run performance test
    print("\n🧪 Running performance test...")
    if run_command("python performance_test.py", "Running performance test"):
        print("✅ Performance test completed")
    else:
        print("⚠️  Performance test failed, but optimizations are still active")
    
    # Create optimization checklist
    print("\n📝 Creating optimization checklist...")
    checklist = """
# Performance Optimization Checklist

## ✅ Completed
- [x] Added comprehensive profiling to all endpoints
- [x] Added response compression (Gzip)
- [x] Added performance middleware
- [x] Created performance testing script
- [x] Added detailed logging

## 🔄 Next Steps (Priority Order)

### 1. Database Indexes (CRITICAL - Do First)
- [ ] Create Firebase indexes (see firebase_indexes_guide.md)
- [ ] Test query performance after indexes

### 2. Frontend Optimizations (HIGH)
- [ ] Implement optimistic UI updates
- [ ] Add loading states for all operations
- [ ] Implement error boundaries
- [ ] Add retry logic for failed requests

### 3. Backend Optimizations (MEDIUM)
- [ ] Add Redis caching for frequently accessed data
- [ ] Implement pagination for large datasets
- [ ] Add connection pooling
- [ ] Optimize document structure

### 4. Monitoring (LOW)
- [ ] Set up performance monitoring
- [ ] Add alerting for slow endpoints
- [ ] Create performance dashboards

## 🚨 Emergency Fixes (If Still Slow)
1. Reduce page size to 10-20 items
2. Add request timeouts
3. Implement circuit breakers
4. Use CDN for static assets

## 📊 Performance Targets
- Inventory load: < 500ms
- Supplier load: < 500ms  
- Add operations: < 1s
- Update operations: < 800ms
- Delete operations: < 500ms

## 🔧 Testing Commands
```bash
# Run performance test
python performance_test.py

# Monitor backend logs
tail -f uvicorn.log

# Check memory usage
ps aux | grep uvicorn

# Test specific endpoint
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/inventory/"
```
"""
    
    with open("optimization_checklist.md", "w") as f:
        f.write(checklist)
    print("✅ Optimization checklist created")
    
    print("\n🎉 Performance setup completed!")
    print("\n📋 Next steps:")
    print("1. Create Firebase indexes (see firebase_indexes_guide.md)")
    print("2. Check performance_results.json for current bottlenecks")
    print("3. Follow optimization_checklist.md for improvements")
    print("4. Run performance_test.py again after each optimization")
    
    print("\n💡 Quick tips:")
    print("- Monitor backend logs for [PERF] entries")
    print("- Use Chrome DevTools Network tab to see response times")
    print("- Check Firebase Console for query performance")
    print("- Consider implementing caching if reads are slow")

if __name__ == "__main__":
    main() 