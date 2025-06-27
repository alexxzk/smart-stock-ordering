# Performance Optimization Guide

## Current Performance Issues

Based on the profiling we've added, here are the main performance bottlenecks and solutions:

### 1. Firestore Query Performance

**Issues:**
- Slow reads when fetching inventory/suppliers
- Multiple round trips to Firestore
- No caching of frequently accessed data

**Solutions:**

#### A. Add Database Indexes
```bash
# Create composite indexes for common queries
# In Firebase Console > Firestore > Indexes
Collection: inventory
Fields: userId (Ascending), category (Ascending)

Collection: suppliers  
Fields: userId (Ascending), categories (Array contains)
```

#### B. Implement Caching
```python
# Add Redis or in-memory caching for frequently accessed data
import redis
from functools import lru_cache

# Cache inventory items for 5 minutes
@lru_cache(maxsize=128)
def get_cached_inventory(user_id: str, ttl: int = 300):
    # Implementation
    pass
```

#### C. Batch Operations
```python
# Use batch writes for multiple operations
def batch_create_inventory(items: List[InventoryItem]):
    batch = db.batch()
    for item in items:
        doc_ref = db.collection("inventory").document()
        batch.set(doc_ref, item.dict())
    batch.commit()
```

### 2. Frontend Performance

**Issues:**
- Full page reloads on data changes
- No optimistic updates
- Large bundle size

**Solutions:**

#### A. Optimistic UI Updates
```typescript
// Update UI immediately, then sync with backend
const addInventoryItem = async (item: InventoryItem) => {
  // Optimistic update
  setInventory(prev => [...prev, { ...item, id: 'temp-id' }]);
  
  try {
    const result = await api.createInventoryItem(item);
    // Replace temp item with real one
    setInventory(prev => prev.map(i => 
      i.id === 'temp-id' ? result : i
    ));
  } catch (error) {
    // Revert on error
    setInventory(prev => prev.filter(i => i.id !== 'temp-id'));
  }
};
```

#### B. Implement Virtual Scrolling
```typescript
// For large lists, use virtual scrolling
import { FixedSizeList as List } from 'react-window';

const VirtualizedInventoryList = ({ items }) => (
  <List
    height={400}
    itemCount={items.length}
    itemSize={50}
    itemData={items}
  >
    {({ index, style, data }) => (
      <div style={style}>
        <InventoryItem item={data[index]} />
      </div>
    )}
  </List>
);
```

### 3. Backend Optimizations

**Issues:**
- Slow response times
- No connection pooling
- Inefficient data processing

**Solutions:**

#### A. Add Connection Pooling
```python
# Use connection pooling for database connections
from firebase_admin import firestore
import asyncio

# Pool Firestore connections
class FirestorePool:
    def __init__(self, max_connections=10):
        self.pool = asyncio.Queue(maxsize=max_connections)
        self._init_pool()
    
    def _init_pool(self):
        for _ in range(self.pool.maxsize):
            self.pool.put_nowait(firestore.client())
```

#### B. Implement Pagination
```python
# Add pagination to large queries
@router.get("/", response_model=List[InventoryItemResponse])
async def get_inventory_items(
    user: dict = Depends(lambda: {"uid": "test-user"}),
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None
):
    """Get paginated inventory items"""
    try:
        db = get_firestore_client()
        query = db.collection("inventory").where("userId", "==", user["uid"])
        
        if category:
            query = query.where("category", "==", category)
        
        # Add pagination
        query = query.limit(page_size).offset((page - 1) * page_size)
        
        docs = query.stream()
        items = [{"id": doc.id, **doc.to_dict()} for doc in docs]
        
        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": len(items)  # In production, get total count separately
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### C. Add Response Compression
```python
# Enable gzip compression
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 4. Database Optimizations

**Issues:**
- Unindexed queries
- Large document sizes
- Inefficient data structure

**Solutions:**

#### A. Optimize Document Structure
```python
# Use subcollections for large datasets
# Instead of storing all stock history in main document:
{
  "id": "item123",
  "name": "Coffee Beans",
  "currentStock": 15.5,
  "stockHistory": [...]  # This can get very large
}

# Use subcollections:
# inventory/item123/stock_history/{history_id}
{
  "previousStock": 20.0,
  "newStock": 15.5,
  "reason": "Daily usage",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### B. Add Composite Indexes
```bash
# Create indexes for common query patterns
Collection: inventory
Indexes:
- userId + category + currentStock
- userId + lastUpdated (for sorting)
- userId + minStock (for low stock alerts)
```

### 5. Monitoring and Alerting

**Add Performance Monitoring:**
```python
# Add metrics collection
import time
from prometheus_client import Counter, Histogram

# Metrics
request_duration = Histogram('http_request_duration_seconds', 'Request duration')
firestore_operations = Counter('firestore_operations_total', 'Firestore operations')

# Middleware to collect metrics
@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    request_duration.observe(duration)
    return response
```

## Immediate Actions to Take

### 1. Quick Wins (Implement Today)
- [ ] Add database indexes in Firebase Console
- [ ] Implement optimistic UI updates in frontend
- [ ] Add response compression
- [ ] Enable connection pooling

### 2. Medium-term (This Week)
- [ ] Implement caching layer (Redis)
- [ ] Add pagination to large queries
- [ ] Optimize document structure
- [ ] Add performance monitoring

### 3. Long-term (Next Sprint)
- [ ] Implement virtual scrolling for large lists
- [ ] Add batch operations for bulk updates
- [ ] Optimize bundle size with code splitting
- [ ] Add comprehensive error handling and retry logic

## Performance Testing

### Test Scenarios
1. **Load Testing**: Test with 1000+ inventory items
2. **Concurrent Users**: Test with 10+ simultaneous users
3. **Network Latency**: Test with slow network conditions
4. **Memory Usage**: Monitor memory consumption during operations

### Tools
- **Backend**: Use `locust` for load testing
- **Frontend**: Use Chrome DevTools Performance tab
- **Database**: Monitor Firestore usage in Firebase Console

## Expected Performance Improvements

After implementing these optimizations:

- **Firestore Reads**: 50-80% faster with proper indexing
- **UI Responsiveness**: 70% improvement with optimistic updates
- **Bundle Size**: 30-40% reduction with code splitting
- **Memory Usage**: 40% reduction with virtual scrolling
- **Overall App Speed**: 60-80% improvement

## Monitoring Commands

```bash
# Monitor backend performance
cd backend && python -m cProfile -o profile.stats -m uvicorn app.main:app

# Analyze profile results
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"

# Monitor memory usage
ps aux | grep uvicorn

# Monitor network requests
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/inventory/"
```

## Emergency Performance Fixes

If the app is extremely slow right now:

1. **Disable non-essential features** temporarily
2. **Add request timeouts** to prevent hanging requests
3. **Implement circuit breakers** for external services
4. **Add retry logic** with exponential backoff
5. **Use CDN** for static assets
6. **Enable HTTP/2** for better multiplexing 