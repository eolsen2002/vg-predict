# sripts/analyze_dec_jan.py

import pandas as pd

def analyze_dec_jan_low_peak(file_path):
    # Load CSV with Date parsing
    df = pd.read_csv(file_path, parse_dates=['Date'])
    df.set_index('Date', inplace=True)
    
    # Define ETFs to analyze
    etfs = ["USFR", "SGOV", "BIL", "TFLO", "SHV", "ICSH"]
    
    # Slice date range for analysis: Dec 1, 2024 to Jan 31, 2025
    df_sub = df.loc["2024-12-01":"2025-01-31"]
    
    results = []
    
    for etf in etfs:
        # Find December low AFTER Dec 10 (to match ICSH low around Dec 18)
        dec_data = df_sub.loc["2024-12-11":"2024-12-31"]
        dec_low = dec_data[etf].min()
        dec_low_date = dec_data[dec_data[etf] == dec_low].index.min()
        
        # Find January peak AFTER Jan 20 (to match ICSH peak Jan 30)
        jan_data = df_sub.loc["2025-01-21":"2025-01-31"]
        jan_peak = jan_data[etf].max()
        jan_peak_date = jan_data[jan_data[etf] == jan_peak].index.max()
        
        results.append({
            'ETF': etf,
            'Dec Low Date': dec_low_date.date() if pd.notnull(dec_low_date) else None,
            'Dec Low Price': dec_low,
            'Jan Peak Date': jan_peak_date.date() if pd.notnull(jan_peak_date) else None,
            'Jan Peak Price': jan_peak
        })
    
    # Create DataFrame for clean output
    results_df = pd.DataFrame(results)
    print("\nLow-to-Peak cycle from Dec 2024 to Jan 2025:\n")
    print(results_df)
    
    # Optionally save results to CSV
    results_df.to_csv("dec_jan_low_peak_analysis.csv", index=False)
    print("\nResults saved to dec_jan_low_peak_analysis.csv")

if __name__ == "__main__":
    # Replace 'path/to/your/etf_prices.csv' with your actual CSV path
    analyze_dec_jan_low_peak(r'C:\xampp\htdocs\vg-predict\data\etf_prices_2023_2025.csv')
