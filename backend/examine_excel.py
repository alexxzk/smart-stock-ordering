import pandas as pd
import sys
import os

def examine_excel_file(file_path):
    """Examine the structure of an Excel file"""
    try:
        # Read the Excel file
        print(f"Reading Excel file: {file_path}")
        
        # Try to read all sheets
        excel_file = pd.ExcelFile(file_path)
        print(f"\nSheets found: {excel_file.sheet_names}")
        
        # Examine each sheet
        for sheet_name in excel_file.sheet_names:
            print(f"\n{'='*50}")
            print(f"Sheet: {sheet_name}")
            print('='*50)
            
            # Read the sheet
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            print(f"Shape: {df.shape} (rows, columns)")
            print(f"Columns: {list(df.columns)}")
            
            # Show first few rows
            print("\nFirst 5 rows:")
            print(df.head())
            
            # Show data types
            print("\nData types:")
            print(df.dtypes)
            
            # Show basic statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                print("\nNumeric columns statistics:")
                print(df[numeric_cols].describe())
            
            # Check for missing values
            missing_values = df.isnull().sum()
            if missing_values.sum() > 0:
                print("\nMissing values:")
                print(missing_values[missing_values > 0])
            
            print(f"\nTotal rows in this sheet: {len(df)}")
            
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

if __name__ == "__main__":
    # Path to the Excel file
    excel_file_path = "../BranchSalesAnalysisDepartment (4).xls"
    
    if os.path.exists(excel_file_path):
        examine_excel_file(excel_file_path)
    else:
        print(f"File not found: {excel_file_path}")
        print("Current directory:", os.getcwd())
        print("Files in current directory:", os.listdir(".")) 