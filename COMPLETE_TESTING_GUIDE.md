# 🧪 Complete Testing Guide - Smart Stock Ordering App

## 🚀 **Current Setup**
- **Backend API**: http://localhost:8000/docs
- **Frontend App**: http://localhost:5173/
- **Health Check**: http://localhost:8000/health

---

## 📋 **Testing Checklist**

### **1. 🔐 Authentication Testing**

#### **Login Page** (`/login`)
- [ ] **Test Login Form**
  - Enter valid email: `test@example.com`
  - Enter password: `password123`
  - Click "Sign In"
  - Should redirect to dashboard

- [ ] **Test Invalid Login**
  - Enter invalid credentials
  - Should show error message
  - Form should not submit

- [ ] **Test "Remember Me"**
  - Check the checkbox
  - Login should persist after browser refresh

#### **Registration** (if available)
- [ ] **Test Registration Form**
  - Fill all required fields
  - Submit registration
  - Should create new user account

---

### **2. 📊 Dashboard Testing**

#### **Dashboard Overview** (`/dashboard`)
- [ ] **Check Dashboard Loads**
  - Should display after successful login
  - Should show user information
  - Should show navigation sidebar

- [ ] **Test Dashboard Cards**
  - **Total Sales**: Should show current period sales
  - **Inventory Items**: Should show total inventory count
  - **Pending Orders**: Should show orders awaiting confirmation
  - **AI Recommendations**: Should show latest AI suggestions

- [ ] **Test Dashboard Charts**
  - **Sales Trend**: Should display sales over time
  - **Top Products**: Should show best-selling items
  - **Inventory Levels**: Should show stock levels

- [ ] **Test Quick Actions**
  - **Upload Sales Data**: Should open CSV upload
  - **View Orders**: Should navigate to orders page
  - **Check Inventory**: Should navigate to inventory page

---

### **3. 📈 Forecasting Testing**

#### **Forecasting Page** (`/forecasting`)
- [ ] **Test CSV Upload**
  - Click "Upload Sales Data"
  - Select sample CSV file: `sample_sales.csv`
  - Should show upload progress
  - Should display success message

- [ ] **Test Data Preview**
  - After upload, should show data preview
  - Should display columns: date, item_name, quantity
  - Should show first 10 rows

- [ ] **Test Forecasting Options**
  - **Forecast Period**: Select 30 days
  - **Forecasting Method**: Choose "Moving Average"
  - Click "Generate Forecast"

- [ ] **Test Forecast Results**
  - Should display forecast chart
  - Should show predicted quantities
  - Should show confidence intervals
  - Should display forecast summary

- [ ] **Test Export Forecast**
  - Click "Export Forecast"
  - Should download CSV file
  - File should contain forecast data

---

### **4. 📦 Inventory Testing**

#### **Inventory Page** (`/inventory`)
- [ ] **Test Inventory Upload**
  - Click "Upload Inventory Data"
  - Select sample file: `sample_inventory.csv`
  - Should show current inventory levels

- [ ] **Test Inventory Display**
  - Should show item names
  - Should show current stock levels
  - Should show reorder points
  - Should show last updated dates

- [ ] **Test Inventory Search**
  - Use search bar to find specific items
  - Should filter results in real-time

- [ ] **Test Inventory Filters**
  - Filter by low stock items
  - Filter by category
  - Filter by supplier

- [ ] **Test Manual Stock Update**
  - Click on an item
  - Update stock quantity
  - Save changes
  - Should reflect immediately

---

### **5. 🛒 Orders Testing**

#### **Orders Page** (`/orders`)
- [ ] **Test AI Recommendations**
  - Click "Get AI Recommendations"
  - Should show recommended order quantities
  - Should display reasoning for each recommendation
  - Should show confidence scores

- [ ] **Test Order Creation**
  - Select items from recommendations
  - Adjust quantities if needed
  - Click "Create Order"
  - Should create new order

- [ ] **Test Order History**
  - Should show all previous orders
  - Should display order dates
  - Should show order status
  - Should show total values

- [ ] **Test Order Details**
  - Click on any order
  - Should show detailed view
  - Should show items ordered
  - Should show supplier information

- [ ] **Test Order Confirmation**
  - Select an order
  - Click "Confirm Order"
  - Should update order status
  - Should send confirmation

- [ ] **Test Order Override**
  - Modify AI recommendations
  - Enter custom quantities
  - Save overridden order
  - Should learn from override

---

### **6. 🏢 Suppliers Testing**

#### **Suppliers Page** (`/suppliers`)
- [ ] **Test Supplier List**
  - Should display all suppliers
  - Should show contact information
  - Should show delivery times

- [ ] **Test Add Supplier**
  - Click "Add New Supplier"
  - Fill supplier details
  - Save supplier
  - Should appear in list

- [ ] **Test Edit Supplier**
  - Click on existing supplier
  - Modify details
  - Save changes
  - Should update immediately

- [ ] **Test Supplier Assignments**
  - Assign items to suppliers
  - Set minimum order quantities
  - Set pack sizes
  - Save assignments

---

### **7. 🔗 Supplier Integrations Testing**

#### **Integrations Page** (`/supplier-integrations`)
- [ ] **Test Gmail Integration** (if configured)
  - Connect Gmail account
  - Test invoice extraction
  - Should parse supplier invoices

- [ ] **Test CSV Import**
  - Upload supplier data
  - Should import supplier information
  - Should update database

---

### **8. 👥 Users Testing**

#### **Users Page** (`/users`)
- [ ] **Test User Management**
  - View current user profile
  - Update user information
  - Change password
  - Update preferences

---

### **9. 📱 Responsive Testing**

#### **Mobile/Tablet Testing**
- [ ] **Test Mobile Layout**
  - Open app on mobile browser
  - Check all pages load properly
  - Test touch interactions
  - Verify navigation works

- [ ] **Test Tablet Layout**
  - Open app on tablet
  - Check responsive design
  - Test all functionality

---

### **10. 🔧 Error Handling Testing**

#### **Error Scenarios**
- [ ] **Test Network Errors**
  - Disconnect internet
  - Try to upload file
  - Should show error message
  - Should offer retry option

- [ ] **Test Invalid Data**
  - Upload malformed CSV
  - Should show validation errors
  - Should guide user to fix

- [ ] **Test Server Errors**
  - Try to access when backend is down
  - Should show appropriate error
  - Should offer refresh option

---

## 🎯 **Sample Data Files**

### **Sample Sales Data** (`sample_sales.csv`)
```csv
date,item_name,quantity
2024-01-01,Coffee,50
2024-01-01,Milk,30
2024-01-02,Coffee,45
2024-01-02,Milk,35
```

### **Sample Inventory Data** (`sample_inventory.csv`)
```csv
item_name,current_stock,reorder_point,unit_cost
Coffee,100,50,2.50
Milk,80,40,1.20
Sugar,200,100,0.80
```

---

## 🚨 **Common Issues & Solutions**

### **If Frontend Won't Load:**
1. Check if Vite server is running: `cd frontend && npm run dev`
2. Check browser console for errors
3. Clear browser cache

### **If Backend Won't Load:**
1. Check if uvicorn is running: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Check terminal for error messages
3. Verify Firebase credentials

### **If Uploads Fail:**
1. Check file format (must be CSV)
2. Check file size (should be < 10MB)
3. Check required columns are present

### **If AI Recommendations Don't Work:**
1. Ensure you have sales data uploaded
2. Check if forecasting was completed
3. Verify inventory data is current

---

## 📊 **Testing Results Template**

```
Date: _______________
Tester: _______________

✅ Working Features:
- [ ] Authentication
- [ ] Dashboard
- [ ] Forecasting
- [ ] Inventory
- [ ] Orders
- [ ] Suppliers
- [ ] Mobile Responsive

❌ Issues Found:
1. ________________
2. ________________
3. ________________

🔧 Recommendations:
1. ________________
2. ________________
3. ________________
```

---

## 🎉 **Success Criteria**

Your app is ready for production when:
- [ ] All features work without errors
- [ ] Data uploads and processes correctly
- [ ] AI recommendations are generated
- [ ] Orders can be created and confirmed
- [ ] Mobile experience is smooth
- [ ] Error handling works properly

**Happy Testing! 🚀** 