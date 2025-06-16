# scripts/update_modal_days.py
# Created: 6/16/25, updated 5:20 PM
# Updates Peak_Modal_Day in each *_full_cycles.csv based on current month's highest price.
# Internal renaming of 'Cycle_Start_Month' to 'Cycle_Month' for consistency.

import pandas as pd
from datetime import datetime

def update_peak_modal_day(etf: str):
    price_path = 'data/etf_prices_2023_2025.csv'
    cycles_path = f'signals/{etf.lower()}_full_cycles.csv'

    try:
        prices = pd.read_csv(price_path)
        cycles = pd.read_csv(cycles_path)
    except FileNotFoundError:
        print(f"[WARN] Missing file for {etf}, skipping.")
        return

    prices['Date'] = pd.to_datetime(prices['Date'])

    etf_price_col = etf.upper()  # e.g. 'USFR'
    etf_volume_col = etf.upper() + '_Volume'  # e.g. 'USFR_Volume'

    if etf_price_col not in prices.columns:
        print(f"[ERROR] ETF price column {etf_price_col} not found in CSV")
        return

    # Extract relevant columns and rename for clarity
    prices_etf = prices[['Date', etf_price_col, etf_volume_col]].copy()
    prices_etf.rename(columns={etf_price_col: 'Price', etf_volume_col: 'Volume'}, inplace=True)

    # Debug: Show first rows to verify data
    print(f"[DEBUG] prices_etf sample for {etf}:\n", prices_etf.head())

    # Rename 'Cycle_Start_Month' to 'Cycle_Month' internally if needed
    if 'Cycle_Start_Month' in cycles.columns and 'Cycle_Month' not in cycles.columns:
        cycles.rename(columns={'Cycle_Start_Month': 'Cycle_Month'}, inplace=True)

    # Ensure Peak_Modal_Day column exists
    if 'Peak_Modal_Day' not in cycles.columns:
        cycles['Peak_Modal_Day'] = None

    # Copy Peak_Date into Peak_Modal_Day for all existing rows, if Peak_Date exists
    if 'Peak_Date' in cycles.columns:
        cycles['Peak_Modal_Day'] = cycles['Peak_Date']

    # Get current year-month string, e.g. '2025-06'
    today = datetime.today()
    current_month = today.strftime('%Y-%m')

    # Filter prices to current month
    month_prices = prices_etf[prices_etf['Date'].dt.strftime('%Y-%m') == current_month]

    if month_prices.empty:
        print(f"[INFO] No price data for {etf} in {current_month}")
        # Still save after copying historical Peak_Date values
        cycles.to_csv(cycles_path, index=False)
        return

    # Find the date with max Price in the current month
    peak_idx = month_prices['Price'].idxmax()
    peak_row = month_prices.loc[peak_idx]
    peak_date = peak_row['Date'].strftime('%Y-%m-%d')

    # Override Peak_Modal_Day for current month in cycles DataFrame
    # Find the row matching current month
    mask_current_month = cycles['Cycle_Month'] == current_month
    if mask_current_month.any():
        cycles.loc[mask_current_month, 'Peak_Modal_Day'] = peak_date
    else:
        # If current month not found, optionally append a new row? (skip for now)
        print(f"[WARN] Current month {current_month} not found in {cycles_path}")

    # Save back to CSV
    cycles.to_csv(cycles_path, index=False)

    print(f"[UPDATED] {etf}: Peak_Modal_Day for {current_month} → {peak_date}")


def update_all_modal_days():
    etfs = ['USFR', 'SGOV', 'BIL', 'SHV', 'TFLO', 'ICSH']
    for etf in etfs:
        update_peak_modal_day(etf)


if __name__ == "__main__":
    update_all_modal_days()
