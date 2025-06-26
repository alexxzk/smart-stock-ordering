# Excel File Conversion Guide

## 🎯 **Your Excel File Issue**

Your Excel file `BranchSalesAnalysisDepartment (4).xls` appears to be in an old format that's causing corruption issues. Here's how to fix it:

## 📋 **Step-by-Step Conversion**

### **Option 1: Using Microsoft Excel (Recommended)**

1. **Open your Excel file** in Microsoft Excel
2. **Go to File → Save As**
3. **Choose file type**: "CSV (Comma delimited) (*.csv)"
4. **Save as**: `sales_data.csv`
5. **Click Save**
6. **If prompted about compatibility**, click "Yes"

### **Option 2: Using Google Sheets**

1. **Upload your Excel file** to Google Drive
2. **Right-click** the file → "Open with" → "Google Sheets"
3. **Go to File → Download → CSV (.csv)**
4. **Save as**: `sales_data.csv`

### **Option 3: Using Numbers (Mac)**

1. **Open your Excel file** in Numbers
2. **Go to File → Export To → CSV**
3. **Choose options** and click "Next"
4. **Save as**: `sales_data.csv`

## 🔍 **Required Data Format**

Your CSV file should have these columns (or similar):

```csv
date,item,quantity,revenue
2024-01-01,Coffee,45,225.00
2024-01-01,Cappuccino,32,192.00
2024-01-02,Latte,28,168.00
```

### **Column Requirements:**
- **date**: Date of sale (YYYY-MM-DD format preferred)
- **item**: Product name
- **quantity**: Number of items sold
- **revenue**: Total revenue for that item

### **Flexible Column Names:**
The app will recognize variations like:
- Date, Sale Date, Transaction Date
- Item, Product, Item Name, Product Name
- Quantity, Qty, Amount, Units
- Revenue, Sales, Price, Total

## 🧪 **Testing Your Converted File**

1. **Save the CSV file** in your project folder
2. **Go to the Forecasting page**: http://localhost:5173/forecasting
3. **Upload your CSV file**
4. **Check the data preview** to ensure it looks correct
5. **Generate a forecast** to test the functionality

## 🚨 **Common Issues & Solutions**

### **"Missing required columns" error:**
- Check that your CSV has columns for date, item, quantity, and revenue
- Column names can be variations (e.g., "Sale Date" instead of "date")

### **"File size too large" error:**
- The app supports files up to 10MB
- If your file is larger, consider splitting it into smaller files

### **"Invalid date format" error:**
- Ensure dates are in a recognizable format (YYYY-MM-DD, MM/DD/YYYY, etc.)
- The app will try to parse various date formats

## 📊 **Sample Data Structure**

Here's what your data should look like:

| date | item | quantity | revenue |
|------|------|----------|---------|
| 2024-01-01 | Coffee | 45 | 225.00 |
| 2024-01-01 | Cappuccino | 32 | 192.00 |
| 2024-01-02 | Latte | 28 | 168.00 |
| 2024-01-02 | Espresso | 15 | 45.00 |

## 🎉 **Next Steps**

Once you've converted your file:

1. **Upload it** to the Forecasting page
2. **Review the data preview** to ensure accuracy
3. **Generate forecasts** for your sales data
4. **Explore the charts and insights** provided by the app

## 💡 **Need Help?**

If you're still having issues:
1. Check that your Excel file isn't corrupted
2. Try opening it in a different application first
3. Make sure you have the required columns
4. Contact support if the conversion doesn't work

---

**Ready to test?** Convert your file and upload it to the Forecasting page! 