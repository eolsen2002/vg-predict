"""
fetch_etf_data.py – updated 6/10/25, 8:56 AM
Script to fetch ETF daily price and volume data from Yahoo Finance.
Saves output to CSV for use in swing signal scripts and dashboard.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

# ETFs in your rotation strategy
etfs = ['USFR', 'SGOV', 'BIL', 'TFLO', 'SHV', 'ICSH']
start_date = '2023-01-01'
end_date = datetime.today().strftime('%Y-%m-%d')  # Auto-update to today

# Download unadjusted daily closing price and volume for each ETF
data = {}
for etf in etfs:
    print(f"📥 Downloading {etf}...")
    ticker = yf.Ticker(etf)
    hist = ticker.history(start=start_date, end=end_date, auto_adjust=False)
    data[etf] = hist['Close']
    data[f"{etf}_Volume"] = hist['Volume']

# Combine into a single DataFrame
df = pd.DataFrame(data)

# Preprocess for saving: remove timezone, reset index, rename column
df.index = df.index.tz_localize(None)
df.reset_index(inplace=True)
df.rename(columns={'index': 'Date'}, inplace=True)

# Save to CSV
df.to_csv("data/etf_prices_2023_2025.csv", index=False)
print("✅ Price data saved to data/etf_prices_2023_2025.csv")
