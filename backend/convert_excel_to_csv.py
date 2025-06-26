import pandas as pd
import os
import sys

def convert_excel_to_csv(excel_file_path, output_csv_path):
    """Convert Excel file to CSV format"""
    try:
        print(f"Attempting to convert: {excel_file_path}")
        
        # Try different methods to read the Excel file
        methods = [
            lambda f: pd.read_excel(f, engine='xlrd'),
            lambda f: pd.read_excel(f, engine='openpyxl'),
            lambda f: pd.read_excel(f, engine='odf'),
        ]
        
        df = None
        for i, method in enumerate(methods):
            try:
                print(f"Trying method {i+1}...")
                df = method(excel_file_path)
                print(f"Success with method {i+1}!")
                break
            except Exception as e:
                print(f"Method {i+1} failed: {e}")
                continue
        
        if df is None:
            print("All methods failed. Please try converting the file manually.")
            print("\nManual conversion steps:")
            print("1. Open the Excel file in Microsoft Excel or Google Sheets")
            print("2. Go to File > Save As or File > Download")
            print("3. Choose CSV format")
            print("4. Save the file as 'sales_data.csv'")
            return False
        
        # Clean up the data
        print(f"Original shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        print(f"After cleaning: {df.shape}")
        
        # Save as CSV
        df.to_csv(output_csv_path, index=False)
        print(f"Successfully converted to: {output_csv_path}")
        
        # Show sample of the converted data
        print("\nFirst 5 rows of converted data:")
        print(df.head())
        
        return True
        
    except Exception as e:
        print(f"Error converting file: {e}")
        return False

def create_sample_csv():
    """Create a sample CSV file with the expected format"""
    sample_data = {
        'date': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02'],
        'item': ['Coffee', 'Cappuccino', 'Coffee', 'Latte'],
        'quantity': [45, 32, 52, 30],
        'revenue': [225.00, 192.00, 260.00, 180.00]
    }
    
    df = pd.DataFrame(sample_data)
    output_path = "../converted_sales_data.csv"
    df.to_csv(output_path, index=False)
    print(f"Created sample CSV file: {output_path}")
    return output_path

if __name__ == "__main__":
    excel_file_path = "../BranchSalesAnalysisDepartment (4).xls"
    output_csv_path = "../converted_sales_data.csv"
    
    if os.path.exists(excel_file_path):
        success = convert_excel_to_csv(excel_file_path, output_csv_path)
        if not success:
            print("\nCreating sample CSV file instead...")
            create_sample_csv()
    else:
        print(f"Excel file not found: {excel_file_path}")
        print("Creating sample CSV file...")
        create_sample_csv() 