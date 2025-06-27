# Smart Stock Ordering App - Testing Guide

## 🚀 Quick Start Testing

### 1. **Create Sample Data**
1. Navigate to the Debug Test page: `http://localhost:5174/debug-test`
2. Click **"Create Sample Data"** to populate your database with test data
3. Verify the console shows successful creation of inventory items and suppliers

### 2. **Test All Core Features**

#### **Dashboard** (`http://localhost:5174/`)
- ✅ Verify authentication status shows "dev@example.com"
- ✅ Check that dashboard loads with sample data
- ✅ Test navigation between all pages
- ✅ Verify responsive design on mobile/tablet

#### **Inventory Management** (`http://localhost:5174/inventory`)
- ✅ View all inventory items (should show 3 items after creating sample data)
- ✅ Test search functionality
- ✅ Test filtering by category
- ✅ Add a new inventory item
- ✅ Edit an existing item
- ✅ Delete an item
- ✅ Verify stock levels and alerts

#### **Suppliers** (`http://localhost:5174/suppliers`)
- ✅ View all suppliers (should show 3 suppliers)
- ✅ Test search functionality
- ✅ Add a new supplier
- ✅ Edit supplier details
- ✅ Delete a supplier
- ✅ Verify contact information display

#### **Forecasting** (`http://localhost:5174/forecasting`)
- ✅ Upload the sample CSV files:
  - `sample_data/sales_data.csv` (single item)
  - `sample_data/multi_item_sales.csv` (multiple items)
- ✅ Test different forecasting periods (7, 14, 30 days)
- ✅ Verify forecast charts display correctly
- ✅ Test ingredient conversion (if implemented)

#### **Orders** (`http://localhost:5174/orders`)
- ✅ Generate smart orders based on inventory levels
- ✅ Test order creation with different suppliers
- ✅ Verify pack size calculations
- ✅ Test order status updates
- ✅ Export orders to PDF/email (if implemented)

#### **Integrations** (`http://localhost:5174/integrations`)
- ✅ Test Gmail API connection (if configured)
- ✅ Verify email sending functionality
- ✅ Test notification settings

#### **User Management** (`http://localhost:5174/users`)
- ✅ View user list
- ✅ Test user role management
- ✅ Verify permissions

## 🔧 Advanced Testing

### **Backend API Testing**
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test inventory endpoint
curl http://localhost:8000/api/inventory

# Test suppliers endpoint
curl http://localhost:8000/api/suppliers

# Test forecasting endpoint
curl -X POST http://localhost:8000/api/forecast \
  -H "Content-Type: application/json" \
  -d '{"period": 7, "data": "sample_data"}'
```

### **Firebase Testing**
1. Check Firebase Console for data creation
2. Verify Firestore rules are working
3. Test real-time updates
4. Verify authentication flow

### **Performance Testing**
- ✅ Test with large datasets (1000+ items)
- ✅ Verify loading states work correctly
- ✅ Test error handling for network issues
- ✅ Check memory usage with long sessions

### **Cross-Browser Testing**
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge

### **Mobile Responsiveness**
- ✅ iPhone (375px width)
- ✅ iPad (768px width)
- ✅ Android (360px width)
- ✅ Test touch interactions

## 🐛 Common Issues & Solutions

### **Frontend Issues**
1. **Page not loading**: Check if backend is running on port 8000
2. **Authentication errors**: Verify Firebase config in `.env`
3. **Slow loading**: Check network tab for failed requests
4. **Styling issues**: Clear browser cache and reload

### **Backend Issues**
1. **Import errors**: Make sure you're in the `backend` directory
2. **Port conflicts**: Kill existing processes on port 8000
3. **Firebase errors**: Check service account JSON path
4. **ML module errors**: Verify all dependencies are installed

### **Database Issues**
1. **No data showing**: Run "Create Sample Data" in debug page
2. **Permission errors**: Check Firestore security rules
3. **Connection timeouts**: Verify Firebase project settings

## 📊 Sample Data Verification

After creating sample data, you should see:

### **Inventory Items (3)**
- Coffee Beans (50kg, Beverages category)
- Milk (20L, Dairy category)
- Sugar (15kg, Pantry category)

### **Suppliers (3)**
- Coffee Supplier Co. (John Smith)
- Dairy Farm Ltd. (Sarah Johnson)
- Sweet Supplies Inc. (Mike Brown)

## 🎯 Testing Checklist

- [ ] Authentication works
- [ ] Dashboard loads with data
- [ ] Inventory CRUD operations
- [ ] Suppliers CRUD operations
- [ ] CSV upload and forecasting
- [ ] Order generation
- [ ] Responsive design
- [ ] Error handling
- [ ] Loading states
- [ ] Navigation
- [ ] Search and filtering
- [ ] Data persistence
- [ ] Real-time updates

## 🚀 Deployment Testing

### **Local Production Build**
```bash
# Frontend
cd frontend
npm run build
npm run preview

# Backend
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### **Environment Variables**
Verify all required environment variables are set:
- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_PROJECT_ID`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_STORAGE_BUCKET`
- `VITE_FIREBASE_MESSAGING_SENDER_ID`
- `VITE_FIREBASE_APP_ID`

## 📝 Test Results Template

```
Test Date: _______________
Tester: _________________

✅ Working Features:
- [ ] Authentication
- [ ] Dashboard
- [ ] Inventory Management
- [ ] Suppliers
- [ ] Forecasting
- [ ] Orders
- [ ] Integrations
- [ ] User Management

❌ Issues Found:
- [ ] Issue 1: Description
- [ ] Issue 2: Description

🔧 Performance:
- [ ] Page load times < 3 seconds
- [ ] No memory leaks
- [ ] Responsive on all devices

📱 Browser Compatibility:
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

🎯 Overall Assessment: [Pass/Fail]
```

## 🆘 Getting Help

If you encounter issues:

1. **Check the browser console** for JavaScript errors
2. **Check the backend logs** for Python errors
3. **Verify environment variables** are set correctly
4. **Test with sample data** first
5. **Clear browser cache** and reload
6. **Restart both frontend and backend** servers

For persistent issues, check the logs and provide:
- Error messages
- Steps to reproduce
- Browser/OS information
- Screenshots if applicable 