"""scripts/update_modal_days.py
created 6/16/25, 1:08 pm
"""
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
    prices_etf = prices[prices['Symbol'] == etf]

    today = datetime.today()
    current_month = today.strftime('%Y-%m')
    month_prices = prices_etf[prices_etf['Date'].dt.strftime('%Y-%m') == current_month]

    if month_prices.empty:
        print(f"[INFO] No price data for {etf} in {current_month}")
        return

    peak_row = month_prices.loc[month_prices['Close'].idxmax()]
    peak_date = peak_row['Date'].strftime('%Y-%m-%d')

    if 'Peak_Modal_Day' not in cycles.columns:
        cycles['Peak_Modal_Day'] = None

    cycles.at[cycles.index[-1], 'Peak_Modal_Day'] = peak_date
    cycles.to_csv(cycles_path, index=False)
    print(f"[UPDATED] {etf} Peak_Modal_Day → {peak_date}")

def update_all_modal_days():
    etfs = ['SGOV', 'BIL', 'SHV', 'TFLO', 'ICSH']
    for etf in etfs:
        update_peak_modal_day(etf)

if __name__ == "__main__":
    update_all_modal_days()
