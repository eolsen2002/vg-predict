"""
a script to detect USFR's low points after its monthly peak, so you can better time re-entry after selling near the top.

This script will:

Identify the peak day of USFR each month (as before).

Look at the trading days after that peak (e.g., next 5–6 trading days).

Find the lowest USFR price in that post-peak window.

Save that low date and price for each month.
"""
import pandas as pd

# Load the ETF price data
df = pd.read_csv("data/etf_prices_2023_2025.csv", index_col=0, parse_dates=True)
df.index = pd.to_datetime(df.index, utc=True).tz_convert(None)

usfr = 'USFR'
months = pd.date_range(start="2023-01-01", end="2025-05-31", freq='MS')

results = []

for month_start in months:
    month_end = month_start + pd.offsets.MonthEnd(0)
    df_month = df[(df.index >= month_start) & (df.index <= month_end)]

    if df_month.empty or df_month[usfr].isnull().all():
        continue

    # Identify the peak day for USFR between the 18th and 23rd
    df_mid = df_month[(df_month.index.day >= 18) & (df_month.index.day <= 23)]
    if df_mid.empty:
        continue

    #usfr_peak_day = df_mid[usfr].idxmax()
    max_price = df_mid[usfr].max()
    peak_candidates = df_mid[df_mid[usfr] == max_price]
    usfr_peak_day = peak_candidates.index.max()
    usfr_peak_price = max_price

    # Post-peak: next 5 calendar days
    post_peak = df[(df.index > usfr_peak_day) & (df.index <= usfr_peak_day + pd.Timedelta(days=6))]
    if post_peak.empty:
        continue

    usfr_low_day = post_peak[usfr].idxmin()
    usfr_low_price = post_peak[usfr].min()

    drop_pct = (usfr_low_price - usfr_peak_price) / usfr_peak_price * 100

    # Sanity check: Only include realistic drop percentages (e.g., > -2%)
    if usfr_peak_price > 0 and usfr_low_price > 0 and drop_pct > -2:
        results.append({
            "Month": month_start.strftime("%Y-%m"),
            "USFR_Peak_Date": usfr_peak_day.strftime("%Y-%m-%d"),
            "USFR_Peak": usfr_peak_price,
            "USFR_Low_Date": usfr_low_day.strftime("%Y-%m-%d"),
            "USFR_Low": usfr_low_price,
            "Drop_%": round(drop_pct, 3)
         })


summary_df = pd.DataFrame(results)

# Filter to keep only rows where Drop_% is between -5% and +5%
summary_df = summary_df[(summary_df['Drop_%'] > -5) & (summary_df['Drop_%'] < 5)]

summary_df.to_csv("signals/usfr_post_peak_lows.csv", index=False)

print("📉 USFR post-peak low analysis complete. Saved to signals/usfr_post_peak_lows.csv.")
