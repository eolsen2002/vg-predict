"""
scripts/usfr_peaks.py

Purpose:
Detect monthly peak prices for the USFR Treasury ETF within a defined date window each month.
This helps identify the typical monthly peak period (usually days 18 to 25) when USFR price
reaches a local maximum, useful for timing swing trades or rebalancing.

Key Features:
- Loads historical daily ETF price data from a CSV file.
- For each month, finds the highest USFR closing price within the configured peak window.
- Outputs a CSV listing detected peak dates and prices by month.

Input:
- data/etf_prices_2023_2025.csv
  Must contain columns: Date, USFR (ETF closing prices)

Output:
- signals/usfr_post_peak_highs.csv
  CSV with columns: YearMonth, Peak_Date, Peak

Configuration:
- Peak detection window for USFR is defined in ETF_CONFIG as days 18–25 of each month.
- Extendable to other ETFs by adding configs.

Usage:
Run directly from the command line:
    python scripts/usfr_peaks.py

Dependencies:
- pandas

"""

import pandas as pd
from datetime import datetime
import os

# Config for ETFs and their monthly peak windows (day of month)
ETF_CONFIG = {
    "USFR": {
        "price_col": "USFR",       # column name in CSV with price data
        "peak_window_start": 18,   # start day of monthly peak window
        "peak_window_end": 25,     # end day of monthly peak window
    },
    # Add more ETFs if needed
}

INPUT_CSV = "data/etf_prices_2023_2025.csv"
OUTPUT_CSV = "signals/usfr_post_peak_highs.csv"

def detect_usfr_peaks():
    if not os.path.exists(INPUT_CSV):
        print(f"❌ Input data file not found: {INPUT_CSV}")
        return
    
    try:
        df = pd.read_csv(INPUT_CSV, parse_dates=["Date"])
    except Exception as e:
        print(f"❌ Error reading input CSV: {e}")
        return
    
    etf = "USFR"
    config = ETF_CONFIG.get(etf)
    if not config:
        print(f"❌ No config found for {etf}")
        return
    
    price_col = config["price_col"]
    if price_col not in df.columns:
        print(f"❌ Required price column '{price_col}' not found in input data.")
        return

    peaks = []

    df['YearMonth'] = df['Date'].dt.to_period('M')

    # Group by month
    for ym, group in df.groupby('YearMonth'):
        peak_window = group[(group['Date'].dt.day >= config["peak_window_start"]) & 
                            (group['Date'].dt.day <= config["peak_window_end"])]
        if peak_window.empty:
            # No data in peak window for this month, skip
            continue
        
        idx_max = peak_window[price_col].idxmax()
        peak_date = df.loc[idx_max, 'Date']
        peak_price = df.loc[idx_max, price_col]
        
        peaks.append({
            "YearMonth": str(ym),
            "Peak_Date": peak_date.strftime("%Y-%m-%d"),
            "Peak": peak_price
        })

    if not peaks:
        print("⚠️ No peaks detected.")
        return

    peaks_df = pd.DataFrame(peaks)

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    peaks_df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Peak detection complete. Output saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    detect_usfr_peaks()
