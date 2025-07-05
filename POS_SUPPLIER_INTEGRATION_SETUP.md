# 🚀 POS & Supplier Integration Setup Guide

## Overview

This guide will help you set up POS (Point of Sale) integrations and supplier integrations for your Smart Stock Ordering system. These integrations will enable:

- **Real-time inventory updates** from your POS system
- **Automated supplier ordering** with real-time pricing
- **Sales data synchronization** for better forecasting
- **Streamlined ordering process** with multiple suppliers

## 📋 Table of Contents

1. [POS Integrations Setup](#pos-integrations-setup)
2. [Supplier Integrations Setup](#supplier-integrations-setup)
3. [Quick Order Process](#quick-order-process)
4. [Inventory Synchronization](#inventory-synchronization)
5. [Troubleshooting](#troubleshooting)

---

## 🏪 POS Integrations Setup

### Supported POS Systems

Your app now supports integration with these popular POS systems:

| POS System | Integration Type | Features | Setup Difficulty |
|------------|------------------|----------|------------------|
| **Square POS** | API (OAuth2) | Sales sync, Inventory sync, Real-time | ⭐⭐ |
| **Toast POS** | API (API Key) | Sales sync, Inventory sync, Menu sync | ⭐⭐ |
| **Clover POS** | API (OAuth2) | Sales sync, Inventory sync | ⭐⭐⭐ |
| **Lightspeed Restaurant** | API (OAuth2) | Sales sync, Inventory sync, Customer sync | ⭐⭐⭐ |
| **Shopify POS** | API (API Key) | Sales sync, Inventory sync, Product sync | ⭐⭐ |

### Step-by-Step POS Setup

#### 1. Access POS Integrations

1. Navigate to **POS Integrations** in your sidebar
2. Click **"Connect New POS"**
3. Select your POS system from the dropdown

#### 2. Square POS Setup

**Prerequisites:**
- Square Developer Account
- Square App with API access

**Setup Steps:**
1. Go to [Square Developer Dashboard](https://developer.squareup.com/)
2. Create a new application
3. Get your **Application ID** and **Access Token**
4. In your app, enter:
   - **Connection Name**: "My Square Store"
   - **Access Token**: Your Square access token
   - **Store ID**: Your Square location ID (optional)

**API Endpoints Used:**
- `GET /v2/locations` - Get store locations
- `GET /v2/orders` - Get sales data
- `GET /v2/inventory/counts` - Get inventory levels

#### 3. Toast POS Setup

**Prerequisites:**
- Toast Partner Account
- API credentials from Toast

**Setup Steps:**
1. Contact Toast for API access
2. Get your **API Key** and **Restaurant ID**
3. In your app, enter:
   - **Connection Name**: "My Toast Restaurant"
   - **API Key**: Your Toast API key
   - **Store ID**: Your Toast restaurant ID

#### 4. Test Your Connection

After setup:
1. Click **"Test Connection"** to verify
2. If successful, you'll see "Connection test successful!"
3. If failed, check your credentials and try again

### POS Data Synchronization

#### Automatic Sync
- **Sales Data**: Syncs daily sales, items sold, and revenue
- **Inventory Levels**: Updates current stock levels
- **Real-time Updates**: Via webhooks (if supported)

#### Manual Sync
- Click **"Sync Sales"** to get latest sales data
- Click **"Sync Inventory"** to update stock levels
- Click **"Sync All"** for complete synchronization

---

## 🛒 Supplier Integrations Setup

### Available Suppliers

Your app comes pre-configured with these major suppliers:

| Supplier | Type | Categories | Min Order | Delivery |
|----------|------|------------|-----------|----------|
| **Sysco** | API | Food, Beverages, Supplies | $500 | 2 days |
| **US Foods** | API | Food, Beverages, Equipment | $300 | 1 day |
| **Gordon Food Service** | Web Scraping | Food, Beverages, Supplies | $200 | 2 days |
| **Local Produce** | Email | Produce, Organic | $50 | 1 day |
| **Coffee Supplier** | API | Coffee, Equipment | $100 | 3 days |
| **Dairy Supplier** | Manual | Dairy, Alternatives | $75 | 1 day |

### Step-by-Step Supplier Setup

#### 1. Access Supplier Integrations

1. Navigate to **Suppliers** in your sidebar
2. View available suppliers
3. Click on a supplier to start integration

#### 2. API-Based Suppliers (Sysco, US Foods, Coffee Supplier)

**Setup Steps:**
1. Contact the supplier for API access
2. Get your API credentials
3. Configure integration in your app
4. Test the connection

**Example Sysco Setup:**
```json
{
  "supplier_id": "sysco",
  "api_key": "your_sysco_api_key",
  "location_id": "your_location_id",
  "webhook_url": "https://your-domain.com/webhooks/sysco"
}
```

#### 3. Web Scraping Suppliers (Gordon Food Service)

**Setup Steps:**
1. No API credentials needed
2. System automatically scrapes pricing
3. Configure delivery preferences
4. Set up order email templates

#### 4. Email-Based Suppliers (Local Produce)

**Setup Steps:**
1. Add supplier email address
2. Configure order email template
3. Set up email parsing rules
4. Test order placement

#### 5. Manual Suppliers (Dairy Supplier)

**Setup Steps:**
1. Add supplier contact information
2. Configure pricing manually
3. Set up order forms
4. Generate order documents

### Supplier Pricing & Ordering

#### Get Real-Time Pricing

1. Select a supplier
2. Enter items (comma-separated)
3. Click **"Get Pricing"**
4. View real-time prices and availability

#### Place Orders

1. Select items and quantities
2. Enter delivery address
3. Choose delivery date
4. Add notes (optional)
5. Click **"Place Order"**

#### Order Tracking

- **Order ID**: Generated automatically
- **Status Updates**: Real-time tracking
- **Delivery Confirmation**: Email notifications
- **Inventory Updates**: Automatic stock updates

---

## ⚡ Quick Order Process

### One-Click Ordering

1. **From Inventory Page:**
   - Click **"Order"** next to low-stock items
   - Select supplier
   - Confirm quantities
   - Place order

2. **From Dashboard:**
   - View low stock alerts
   - Click **"Quick Order"**
   - Select items and supplier
   - Place order

3. **From Forecasting:**
   - View predicted shortages
   - Click **"Pre-order"**
   - Select supplier and quantities
   - Schedule delivery

### Bulk Ordering

1. **Select Multiple Items:**
   - Check items in inventory
   - Click **"Bulk Order"**
   - Choose supplier
   - Review and confirm

2. **Template Orders:**
   - Save common order templates
   - Use templates for regular orders
   - Modify quantities as needed

---

## 📊 Inventory Synchronization

### Real-Time Updates

#### From POS Systems
- **Sales Transactions**: Automatically reduce inventory
- **Returns**: Automatically increase inventory
- **Adjustments**: Manual corrections sync to POS

#### From Suppliers
- **Deliveries**: Automatically increase inventory
- **Order Confirmations**: Update expected deliveries
- **Stock Updates**: Real-time availability checks

### Sync Schedule

- **Sales Data**: Every 15 minutes
- **Inventory Levels**: Every hour
- **Supplier Pricing**: Daily
- **Order Status**: Real-time

### Manual Sync

If automatic sync fails:
1. Go to **POS Integrations**
2. Click **"Sync All"** on your connection
3. Check sync status and logs
4. Contact support if issues persist

---

## 🔧 Troubleshooting

### Common Issues

#### POS Connection Issues

**Problem**: "Connection test failed"
**Solutions**:
1. Check API credentials
2. Verify network connectivity
3. Ensure POS system is online
4. Check API rate limits

**Problem**: "No data synced"
**Solutions**:
1. Verify date range settings
2. Check POS system permissions
3. Ensure data exists in POS
4. Review sync logs

#### Supplier Integration Issues

**Problem**: "Pricing not available"
**Solutions**:
1. Check supplier API status
2. Verify item names match
3. Check supplier inventory
4. Contact supplier support

**Problem**: "Order placement failed"
**Solutions**:
1. Verify minimum order amounts
2. Check delivery address
3. Ensure items are in stock
4. Review order validation

### Error Codes

| Error Code | Meaning | Solution |
|------------|---------|----------|
| `401` | Authentication failed | Check API credentials |
| `403` | Access denied | Verify permissions |
| `404` | Resource not found | Check item names/IDs |
| `429` | Rate limit exceeded | Wait and retry |
| `500` | Server error | Contact support |

### Support Resources

- **Documentation**: Check this guide
- **API Status**: Monitor supplier/POS status pages
- **Logs**: Review sync logs in the app
- **Support**: Contact technical support

---

## 🎯 Best Practices

### POS Integration

1. **Test Regularly**: Test connections weekly
2. **Monitor Syncs**: Check sync status daily
3. **Backup Data**: Export data regularly
4. **Update Credentials**: Rotate API keys quarterly

### Supplier Management

1. **Multiple Suppliers**: Use multiple suppliers for key items
2. **Price Comparison**: Compare prices regularly
3. **Order Templates**: Create templates for common orders
4. **Delivery Scheduling**: Plan deliveries around busy periods

### Inventory Management

1. **Real-time Monitoring**: Monitor inventory levels continuously
2. **Automated Alerts**: Set up low stock alerts
3. **Regular Audits**: Conduct physical inventory counts
4. **Forecast Integration**: Use sales data for better forecasting

---

## 🚀 Advanced Features

### Webhook Configuration

For real-time updates, configure webhooks:

```json
{
  "webhook_url": "https://your-domain.com/webhooks/pos",
  "events": ["sales", "inventory", "orders"],
  "secret": "your_webhook_secret"
}
```

### API Customization

For custom integrations, use the API:

```bash
# Get POS connections
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-api.com/api/pos-integrations/connections

# Sync data
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-api.com/api/pos-integrations/connections/CONNECTION_ID/sync
```

### Automation Rules

Set up automation rules for:
- **Low Stock Alerts**: Automatic reordering
- **Price Changes**: Notifications when prices change
- **Delivery Scheduling**: Automatic delivery scheduling
- **Inventory Reconciliation**: Regular stock checks

---

## 📞 Support

For additional help:

- **Email**: support@ordix.ai
- **Documentation**: Check the app's help section
- **Community**: Join our user community
- **Training**: Schedule a training session

---

*Last updated: January 2024* 