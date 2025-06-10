# scripts/usfr_post_peak_lows.py
# Description: Detects USFR's lowest price within 1–3 trading days after its monthly peak to identify ideal re-entry points.

import pandas as pd
from datetime import datetime

# Load the ETF price data
df = pd.read_csv("data/etf_prices_2023_2025.csv", index_col=0, parse_dates=True)
df.index = pd.to_datetime(df.index, utc=True).tz_convert(None)

usfr = 'USFR'
latest_date = df.index.max()
months = pd.date_range(start="2023-01-01", end=latest_date, freq='MS')

results = []

for month_start in months:
    month_end = month_start + pd.offsets.MonthEnd(0)
    df_month = df[(df.index >= month_start) & (df.index <= month_end)]

    if df_month.empty or df_month[usfr].isnull().all():
        continue

    # Identify the peak day for USFR between the 21st and 26th
    df_mid = df_month[(df_month.index.day >= 21) & (df_month.index.day <= 26)]
    if df_mid.empty:
        continue

    max_price = df_mid[usfr].max()
    peak_candidates = df_mid[df_mid[usfr] == max_price]
    usfr_peak_day = peak_candidates.index.max()
    usfr_peak_price = max_price

    # Find the next 3 **trading** days after the peak
    post_peak = df[df.index > usfr_peak_day]
    post_peak = post_peak[post_peak[usfr].notna()]
    post_peak_trading_days = post_peak.head(3)  # First 3 trading days only

    if post_peak_trading_days.empty:
        continue

    usfr_low_price = post_peak_trading_days[usfr].min()
    usfr_low_day = post_peak_trading_days[post_peak_trading_days[usfr] == usfr_low_price].index[0]

    drop_pct = (usfr_low_price - usfr_peak_price) / usfr_peak_price * 100

    # Keep realistic drops only
    if usfr_peak_price > 0 and usfr_low_price > 0 and drop_pct > -5:
        results.append({
            "Month": month_start.strftime("%Y-%m"),
            "USFR_Peak_Date": usfr_peak_day.strftime("%Y-%m-%d"),
            "USFR_Peak": usfr_peak_price,
            "USFR_Low_Date": usfr_low_day.strftime("%Y-%m-%d"),
            "USFR_Low": usfr_low_price,
            "Drop_%": round(drop_pct, 3)
        })

summary_df = pd.DataFrame(results)
summary_df.to_csv("signals/usfr_post_peak_lows.csv", index=False)

print("📉 USFR post-peak low analysis complete. Saved to signals/usfr_post_peak_lows.csv.")
