import pandas as pd

def convert_excel_to_csv(excel_file, csv_file):
    # Read the Excel file, skipping any unnamed headers
    health_data = pd.read_excel(excel_file, header=0)
    
    # Drop any completely empty columns
    health_data.dropna(axis=1, how='all', inplace=True)
    
    # Drop any completely empty rows
    health_data.dropna(axis=0, how='all', inplace=True)
    
    # Reset index after dropping rows
    health_data.reset_index(drop=True, inplace=True)
    
    # Ensure the date column is in datetime format
    if 'date' in health_data.columns:
        health_data['date'] = pd.to_datetime(health_data['date'], errors='coerce')
    
    # Save it as a CSV file without unnamed headers
    health_data.to_csv(csv_file, index=False)
    print(f"Converted {excel_file} to {csv_file}")

if __name__ == "__main__":
    convert_excel_to_csv("dsa210 health metrics.xlsx", "health_metrics.csv") 