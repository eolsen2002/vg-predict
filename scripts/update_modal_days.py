# scripts/update_modal_days.py
# Created: 6/16/25, updated 6/27/25, 1:41 PM
# Updates Peak_Modal_Day in each *_full_cycles.csv based on current month's highest price.
# Internal renaming of 'Cycle_Start_Month' to 'Cycle_Month' for consistency.
# Uses debug_print from utils.debug with debug_mode toggle.

# Step 1 — Fix ModuleNotFoundError in update_modal_days.py

# At the top of scripts/update_modal_days.py, insert this so it can find utils/:
'''
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
'''
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from datetime import datetime
from utils.debug import debug_print

def update_peak_modal_day(etf: str):
    price_path = 'data/etf_prices_2023_2025.csv'
    cycles_path = f'signals/{etf.lower()}_full_cycles.csv'

    try:
        prices = pd.read_csv(price_path)
        cycles = pd.read_csv(cycles_path)
    except FileNotFoundError:
        print(f"[WARN] Missing file for {etf}, skipping.")
        return

    # Parse 'Date' column to datetime
    prices['Date'] = pd.to_datetime(prices['Date'])

    etf_price_col = etf.upper()      # e.g. 'USFR'
    etf_volume_col = etf.upper() + '_Volume'  # e.g. 'USFR_Volume'

    if etf_price_col not in prices.columns:
        print(f"[ERROR] ETF price column {etf_price_col} not found in CSV")
        return

    # Extract relevant columns for this ETF, rename locally
    prices_etf = prices[['Date', etf_price_col, etf_volume_col]].copy()
    prices_etf.rename(columns={etf_price_col: 'Price', etf_volume_col: 'Volume'}, inplace=True)

    # Debug output - only if debug_mode = True
    debug_print(f"prices_etf sample for {etf}:\n{prices_etf.head()}")

    # Internal rename for consistency if needed (no permanent CSV change)
    if 'Cycle_Start_Month' in cycles.columns and 'Cycle_Month' not in cycles.columns:
        cycles.rename(columns={'Cycle_Start_Month': 'Cycle_Month'}, inplace=True)

    # Get current year-month string e.g. '2025-06'
    today = datetime.today()
    current_month = today.strftime('%Y-%m')

    # Filter ETF prices to current month only
    month_prices = prices_etf[prices_etf['Date'].dt.strftime('%Y-%m') == current_month]

    if month_prices.empty:
        print(f"[INFO] No price data for {etf} in {current_month}")
        return

    # Find row with highest 'Price' (corrected from 'Close')
    peak_row = month_prices.loc[month_prices['Price'].idxmax()]
    peak_date = peak_row['Date'].strftime('%Y-%m-%d')

    # Add 'Peak_Modal_Day' column if missing (will be None initially)
    if 'Peak_Modal_Day' not in cycles.columns:
        cycles['Peak_Modal_Day'] = None

    # Update last row's Peak_Modal_Day with the peak_date (string formatted)
    cycles.at[cycles.index[-1], 'Peak_Modal_Day'] = peak_date

    # Save updated cycles CSV
    cycles.to_csv(cycles_path, index=False)

    print(f"[UPDATED] {etf} Peak_Modal_Day → {peak_date}")

def update_all_modal_days():
    # List ETFs to update
    etfs = ['SGOV', 'BIL', 'SHV', 'TFLO', 'ICSH']
    for etf in etfs:
        update_peak_modal_day(etf)

if __name__ == "__main__":
    update_all_modal_days()
