"""
scripts/generate_peak_csvs.py

Purpose:
--------
Generate monthly post-peak CSV files for six Treasury ETFs by applying
ETF-specific peak detection rules based on historical price data.

Key Logic:
-----------
- USFR ETF:
  * Peak window typically between days 18 and 25 of each month.
  * Peak validation includes checking for a recent low within the prior 10 days.
- Other ETFs (SGOV, BIL, SHV, TFLO, ICSH):
  * Peak defined as the highest closing price on the last trading day of the month.

Input:
-------
- Historical ETF price data file: data/etf_prices_2023_2025.csv
  * Must include daily prices and dates for all 6 ETFs.

Output:
--------
- Individual CSV files saved in signals/ directory for each ETF:
  * [etf]_post_peak_highs.csv
  * Each contains detected monthly peak dates and prices per ETF.

Usage:
-------
Run this script after updating historical price data to generate
fresh peak signals for the 6 Treasury ETFs.
"""

import os
import sys
import pandas as pd

# 🧠 Add project root to path so 'utils' can be imported from scripts/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.peak_detection import find_post_peak_peaks  # ✅ External function import

ETF_LIST = ['USFR', 'SGOV', 'BIL', 'TFLO', 'SHV', 'ICSH']
INPUT_CSV = 'data/etf_prices_2023_2025.csv'
OUTPUT_DIR = 'signals'

# Ensure output folder exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    try:
        df = pd.read_csv(INPUT_CSV)
    except Exception as e:
        print(f"❌ Failed to load input CSV: {e}")
        return

    for etf in ETF_LIST:
        print(f"📈 Processing {etf}...")
        result_df = find_post_peak_peaks(etf, df)

        if not result_df.empty:
            output_file = os.path.join(OUTPUT_DIR, f"{etf.lower()}_post_peak_highs.csv")
            result_df.to_csv(output_file, index=False)
            print(f"✅ Saved: {output_file}")
        else:
            print(f"⚠️ No valid peak data found for {etf}")

if __name__ == "__main__":
    main()
