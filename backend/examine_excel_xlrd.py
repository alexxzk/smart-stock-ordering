import xlrd
import os

def examine_excel_with_xlrd(file_path):
    """Examine Excel file using xlrd for .xls format"""
    try:
        print(f"Reading Excel file: {file_path}")
        
        # Open the workbook
        workbook = xlrd.open_workbook(file_path)
        
        print(f"Workbook loaded successfully!")
        print(f"Sheets found: {workbook.sheet_names()}")
        
        # Examine each sheet
        for sheet_name in workbook.sheet_names():
            print(f"\n{'='*50}")
            print(f"Sheet: {sheet_name}")
            print('='*50)
            
            sheet = workbook.sheet_by_name(sheet_name)
            
            # Get dimensions
            num_rows = sheet.nrows
            num_cols = sheet.ncols
            
            print(f"Dimensions: {num_rows} rows x {num_cols} columns")
            
            # Read first few rows to understand structure
            print("\nFirst 10 rows (first 10 columns):")
            for row in range(min(10, num_rows)):
                row_data = []
                for col in range(min(10, num_cols)):
                    cell_value = sheet.cell_value(row, col)
                    row_data.append(str(cell_value) if cell_value != '' else '')
                print(f"Row {row + 1}: {row_data}")
            
            # Try to identify headers
            if num_rows > 0:
                print(f"\nPotential headers (Row 1):")
                headers = []
                for col in range(min(10, num_cols)):
                    header_value = sheet.cell_value(0, col)
                    headers.append(str(header_value) if header_value != '' else f'Column_{col + 1}')
                print(headers)
                
                # Show some sample data rows
                if num_rows > 1:
                    print(f"\nSample data rows (rows 2-5):")
                    for row in range(1, min(6, num_rows)):
                        row_data = []
                        for col in range(min(10, num_cols)):
                            cell_value = sheet.cell_value(row, col)
                            row_data.append(str(cell_value) if cell_value != '' else '')
                        print(f"Row {row + 1}: {row_data}")
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Path to the Excel file
    excel_file_path = "../BranchSalesAnalysisDepartment (4).xls"
    
    if os.path.exists(excel_file_path):
        examine_excel_with_xlrd(excel_file_path)
    else:
        print(f"File not found: {excel_file_path}")
        print("Current directory:", os.getcwd())
        print("Files in current directory:", os.listdir(".")) 