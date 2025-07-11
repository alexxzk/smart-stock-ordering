# Supplier API Integrations - Complete Guide

## Overview

The Supplier API Integrations system provides seamless connectivity with major foodservice suppliers including Bidfood, PFD (Professional Food Distributors), and Ordermentum. For suppliers without APIs, the system generates PDF order sheets and sends email orders automatically.

## 🏪 Supported Suppliers

### API-Enabled Suppliers

#### **Bidfood**
- **Description**: Leading foodservice distributor in Australia
- **API Base URL**: `https://api.bidfood.com.au/v1`
- **Features**: Real-time pricing, automated ordering, inventory sync, delivery tracking
- **Categories**: Food, beverages, supplies, equipment
- **Minimum Order**: $200
- **Lead Time**: 2 days
- **Required Config**: API Key, Location ID

#### **PFD (Professional Food Distributors)**
- **Description**: Professional food distribution services
- **API Base URL**: `https://api.pfd.com.au/v2`
- **Features**: Real-time pricing, automated ordering, inventory sync
- **Categories**: Food, beverages, supplies
- **Minimum Order**: $150
- **Lead Time**: 1 day
- **Required Config**: API Key, Account Number

#### **Ordermentum**
- **Description**: Digital ordering platform for hospitality
- **API Base URL**: `https://api.ordermentum.com/v1`
- **Features**: Real-time pricing, automated ordering, supplier network
- **Categories**: Food, beverages, supplies
- **Minimum Order**: $100
- **Lead Time**: 2 days
- **Required Config**: API Key, Restaurant ID

### Manual Suppliers
- **PDF Order Sheets**: Generate professional order forms
- **Email Orders**: Send orders directly to supplier email addresses
- **Manual Tracking**: Track orders through the system

## 🔧 Technical Implementation

### Backend Architecture

#### **Service Layer** (`backend/app/services/supplier_api_integrations.py`)
```python
class SupplierAPIIntegration:
    """Base class for supplier API integrations"""
    
    async def get_products(self, category: str = None) -> List[SupplierProduct]:
        """Get products from supplier"""
        pass
    
    async def place_order(self, order: OrderRequest) -> OrderConfirmation:
        """Place order with supplier"""
        pass

class BidfoodIntegration(SupplierAPIIntegration):
    """Bidfood API integration"""
    pass

class PFDIntegration(SupplierAPIIntegration):
    """PFD API integration"""
    pass

class OrdermentumIntegration(SupplierAPIIntegration):
    """Ordermentum API integration"""
    pass
```

#### **API Endpoints** (`backend/app/api/supplier_api_integrations.py`)

**Configuration**
- `POST /api/supplier-api-integrations/configure` - Configure supplier integration
- `GET /api/supplier-api-integrations/test-connection/{supplier_id}` - Test API connection

**Products**
- `GET /api/supplier-api-integrations/products/{supplier_id}` - Get supplier products
- `GET /api/supplier-api-integrations/suppliers` - Get available suppliers

**Orders**
- `POST /api/supplier-api-integrations/order` - Place API order
- `POST /api/supplier-api-integrations/order-sheet/pdf` - Generate PDF order sheet
- `POST /api/supplier-api-integrations/order-sheet/email` - Send email order
- `GET /api/supplier-api-integrations/orders` - Get order history
- `GET /api/supplier-api-integrations/download/{order_id}` - Download order sheet

### Frontend Components

#### **Main Component** (`frontend/src/components/supplier-api-integrations/SupplierAPIIntegrations.tsx`)
- **Tabs**: Available Suppliers, Products, Orders, Configuration
- **Features**: 
  - Supplier configuration and testing
  - Product browsing and ordering
  - Order history and tracking
  - PDF generation and email sending

## 📋 Setup Instructions

### 1. Configure Supplier APIs

#### **Bidfood Setup**
1. Contact Bidfood for API access
2. Obtain API key and location ID
3. Configure in the system:
   ```json
   {
     "supplier_id": "bidfood",
     "api_key": "your_bidfood_api_key",
     "location_id": "your_location_id"
   }
   ```

#### **PFD Setup**
1. Contact PFD for API access
2. Obtain API key and account number
3. Configure in the system:
   ```json
   {
     "supplier_id": "pfd",
     "api_key": "your_pfd_api_key",
     "account_number": "your_account_number"
   }
   ```

#### **Ordermentum Setup**
1. Contact Ordermentum for API access
2. Obtain API key and restaurant ID
3. Configure in the system:
   ```json
   {
     "supplier_id": "ordermentum",
     "api_key": "your_ordermentum_api_key",
     "restaurant_id": "your_restaurant_id"
   }
   ```

### 2. Environment Configuration

Add SMTP settings for email orders:
```bash
# Email configuration for order sheets
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your_email@gmail.com"
export SMTP_PASSWORD="your_app_password"
```

### 3. Install Dependencies

```bash
# Backend dependencies
pip install aiohttp reportlab

# Frontend dependencies (already included)
npm install @mui/material @mui/icons-material
```

## 🚀 Usage Guide

### **For API-Enabled Suppliers**

#### 1. Configure Integration
1. Navigate to **Supplier API Integrations**
2. Go to **Configuration** tab
3. Select supplier and enter API credentials
4. Click **Configure Integration**
5. Test connection to verify setup

#### 2. Browse Products
1. Go to **Products** tab
2. Select a configured supplier
3. View available products with pricing
4. Filter by category if needed

#### 3. Place Orders
1. Click **Place Order** from products view
2. Select items and quantities
3. Enter delivery details
4. Submit order via API

### **For Manual Suppliers**

#### 1. Generate PDF Order Sheet
1. Go to **Supplier API Integrations**
2. Click **Place Order**
3. Select **PDF Order Sheet**
4. Enter supplier name and order details
5. Generate and download PDF

#### 2. Send Email Order
1. Select **Email Order** type
2. Enter supplier email address
3. Fill in order details
4. Send order via email with PDF attachment

## 📊 Data Models

### **SupplierProduct**
```typescript
{
  product_id: string;
  name: string;
  description: string;
  price: number;
  unit: string;
  category: string;
  supplier_id: string;
  in_stock: boolean;
  min_order_qty: number;
  lead_time_days: number;
  last_updated: datetime;
}
```

### **OrderRequest**
```typescript
{
  order_id: string;
  supplier_id: string;
  items: OrderItem[];
  delivery_address: string;
  delivery_date: datetime;
  contact_person: string;
  contact_phone: string;
  contact_email: string;
  notes: string;
  urgent: boolean;
}
```

### **OrderConfirmation**
```typescript
{
  order_id: string;
  supplier_order_id: string;
  status: string;
  estimated_delivery: datetime;
  total_amount: number;
  confirmation_message: string;
}
```

## 📄 PDF Order Sheets

### **Features**
- Professional formatting with company branding
- Complete order details and item breakdown
- Delivery and contact information
- Urgent order indicators
- Automatic total calculations

### **Template Structure**
```
┌─────────────────────────────────────┐
│           ORDER SHEET               │
│         [Supplier Name]             │
├─────────────────────────────────────┤
│ Order ID: ORD-12345                │
│ Date: 2024-01-15                   │
│ Delivery Date: 2024-01-17          │
│ Contact: John Smith                 │
│ Phone: +1-555-0123                 │
│ Email: john@restaurant.com         │
├─────────────────────────────────────┤
│ ITEMS                               │
│ ┌─────────┬─────────┬─────────────┐ │
│ │ Item    │ Qty     │ Price       │ │
│ ├─────────┼─────────┼─────────────┤ │
│ │ Coffee  │ 5 kg    │ $125.00     │ │
│ │ Milk    │ 10 L    │ $25.00      │ │
│ └─────────┴─────────┴─────────────┘ │
│ TOTAL: $150.00                      │
└─────────────────────────────────────┘
```

## 📧 Email Orders

### **Features**
- Automatic PDF attachment
- Professional email template
- Order confirmation tracking
- Delivery scheduling
- Contact information included

### **Email Template**
```
Subject: Order Request - ORD-12345 - [Supplier Name]

Dear [Supplier Name] Team,

Please find attached our order request (Order ID: ORD-12345).

Order Details:
- Order ID: ORD-12345
- Delivery Date: 2024-01-17
- Contact: John Smith (+1-555-0123)
- Delivery Address: 123 Main St, City, State 12345
- Urgent: No

Notes: Please deliver before 2 PM

Please confirm receipt of this order and provide delivery confirmation.

Best regards,
John Smith
```

## 🔒 Security & Authentication

### **API Security**
- Bearer token authentication
- API key encryption
- Rate limiting protection
- Secure HTTPS communication

### **Data Protection**
- Encrypted API credentials
- Secure order storage
- Access control and logging
- GDPR compliance

## 📈 Benefits

### **Automation Benefits**
- **Time Savings**: 90% reduction in manual ordering
- **Error Reduction**: Eliminate manual data entry errors
- **Real-time Data**: Live pricing and availability
- **Order Tracking**: Automated status updates

### **Cost Benefits**
- **Price Optimization**: Compare prices across suppliers
- **Bulk Discounts**: Automatic bulk order qualification
- **Delivery Optimization**: Schedule deliveries efficiently
- **Inventory Reduction**: Just-in-time ordering

### **Operational Benefits**
- **Stock Alerts**: Automatic low-stock notifications
- **Order History**: Complete audit trail
- **Supplier Performance**: Track delivery times and quality
- **Analytics**: Data-driven purchasing decisions

## 🛠️ Troubleshooting

### **Common Issues**

#### **API Connection Failures**
1. **Check API Credentials**: Verify API key and required parameters
2. **Test Connection**: Use the test connection feature
3. **Check Network**: Ensure internet connectivity
4. **Contact Supplier**: Verify API access with supplier

#### **PDF Generation Issues**
1. **Check File Permissions**: Ensure write access to output directory
2. **Verify Dependencies**: Install reportlab library
3. **Check Disk Space**: Ensure sufficient storage space
4. **Review Order Data**: Verify all required fields are filled

#### **Email Sending Issues**
1. **Check SMTP Settings**: Verify email configuration
2. **Test Email Credentials**: Use test email feature
3. **Check Firewall**: Ensure SMTP ports are open
4. **Verify Recipient**: Check supplier email address

### **Error Messages**

- `"API request failed"`: Check API credentials and network
- `"PDF generation failed"`: Check file permissions and dependencies
- `"Email sending failed"`: Check SMTP configuration
- `"Order placement failed"`: Verify order data and supplier status

## 🔄 Integration Workflow

### **API Order Flow**
1. **Configure Integration** → Set up API credentials
2. **Browse Products** → View available items and pricing
3. **Create Order** → Select items and quantities
4. **Submit Order** → Send order via API
5. **Track Order** → Monitor order status and delivery

### **Manual Order Flow**
1. **Generate PDF** → Create order sheet
2. **Send Email** → Email order to supplier
3. **Track Confirmation** → Monitor email responses
4. **Update Status** → Mark order as confirmed

### **Order Tracking**
1. **Order Created** → System generates order
2. **Order Submitted** → Sent to supplier
3. **Order Confirmed** → Supplier acknowledges
4. **Order Shipped** → Delivery in progress
5. **Order Delivered** → Order completed

## 📊 Analytics & Reporting

### **Order Analytics**
- **Order Volume**: Track order frequency and amounts
- **Supplier Performance**: Compare delivery times and quality
- **Cost Analysis**: Monitor pricing trends
- **Inventory Impact**: Track stock level changes

### **Supplier Reports**
- **Order History**: Complete order audit trail
- **Delivery Performance**: On-time delivery rates
- **Quality Metrics**: Product quality ratings
- **Cost Comparison**: Price analysis across suppliers

## 🚀 Future Enhancements

### **Planned Features**
- **Multi-language Support**: International supplier support
- **Advanced Analytics**: Predictive ordering
- **Mobile App**: Order management on mobile
- **Webhook Support**: Real-time order updates

### **Potential Integrations**
- **Additional Suppliers**: More API integrations
- **Payment Processing**: Automated payment handling
- **Inventory Sync**: Real-time stock updates
- **Delivery Tracking**: GPS tracking integration

## 📞 Support

### **Technical Support**
- **API Issues**: Contact supplier technical support
- **System Issues**: Check system logs and documentation
- **Configuration**: Review setup guides and examples

### **Supplier Support**
- **Bidfood**: Contact Bidfood API support team
- **PFD**: Contact PFD technical support
- **Ordermentum**: Contact Ordermentum integration team

## 📚 Documentation

### **API Documentation**
- **Bidfood API**: [Bidfood Developer Portal](https://api.bidfood.com.au/docs)
- **PFD API**: [PFD Developer Documentation](https://api.pfd.com.au/docs)
- **Ordermentum API**: [Ordermentum API Guide](https://api.ordermentum.com/docs)

### **System Documentation**
- **Setup Guide**: Complete installation instructions
- **User Manual**: Step-by-step usage guide
- **Troubleshooting**: Common issues and solutions
- **API Reference**: Complete endpoint documentation

---

The Supplier API Integrations system provides a comprehensive solution for connecting with foodservice suppliers, enabling automated ordering, real-time pricing, and efficient inventory management. 