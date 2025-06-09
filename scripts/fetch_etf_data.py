"""
fetch_etf_data.py
Script to fetch data from yahoo finance to determine when to buy/sell
EFTs
and then  Save to Excel and CSV
df.to_excel("data/etf_prices_2023_2025.xlsx")
df.to_csv("data/etf_prices_2023_2025.csv")

"""
import yfinance as yf
import pandas as pd
from datetime import datetime

# ETFs in your rotation strategy
etfs = ['USFR', 'SGOV', 'BIL', 'TFLO', 'SHV', 'ICSH']
start_date = '2023-01-01'
# Automatically set end_date to today (formatted as YYYY-MM-DD)
end_date = datetime.today().strftime('%Y-%m-%d') # 🔄 Auto-update to today

# Download daily closing price for each ETF
data = {}
for etf in etfs:
    print(f"Downloading {etf}...")
    ticker = yf.Ticker(etf)
    # Ensure no dividend or split adjustments
    # This should give you the unadjusted Close price, but sometimes 
    # yfinance returns adjusted prices by default in the DataFrame's 'Close' 
    # column (or it depends on the ETF). To be safe, we can explicitly specify 
    # you want unadjusted Close prices.
    #hist = ticker.history(start=start_date, end=end_date)

    #This tells yfinance to NOT adjust prices for dividends or splits, so 'Close' is the real traded price.
    hist = ticker.history(start=start_date, end=end_date, auto_adjust=False)

    data[etf] = hist['Close']

# Combine into a single DataFrame
df = pd.DataFrame(data)

# Remove timezone from index to avoid Excel errors
df.index = df.index.tz_localize(None)

# Save to Excel and CSV
df.to_excel("data/etf_prices_2023_2025.xlsx")
df.to_csv("data/etf_prices_2023_2025.csv")
print("✅ Price data saved.")
