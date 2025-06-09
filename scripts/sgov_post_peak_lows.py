"""
sgov_post_peak_lows.py
This script will:

- Load your existing price dataset
- Find SGOV's monthly peak (between the 18th–23rd)
- Identify the lowest price in the following 6 calendar days
- Export the results to signals/sgov_post_peak_lows.csv
"""
import pandas as pd

# Load data
df = pd.read_csv("data/etf_prices_2023_2025.csv", index_col=0, parse_dates=True)
df.index = pd.to_datetime(df.index, utc=True).tz_convert(None)

sgov = 'SGOV'
months = pd.date_range(start="2023-01-01", end="2025-05-31", freq='MS')

all_results = []
filtered_results = []

for month_start in months:
    month_end = month_start + pd.offsets.MonthEnd(0)
    df_month = df[(df.index >= month_start) & (df.index <= month_end)]

    valid_prices = df_month[sgov].dropna()
    print(f"{month_start.strftime('%Y-%m')} - valid SGOV price days: {len(valid_prices)}")

    if df_month.empty or df_month[sgov].isnull().all():
        continue

    # Use the last valid trading day of the month as the peak
    sgov_month_prices = df_month[sgov].dropna()
    if sgov_month_prices.empty:
        continue

    sgov_peak_day = sgov_month_prices.index.max()
    sgov_peak_price = sgov_month_prices.loc[sgov_peak_day]

    # Post-peak window: first 3 valid trading days of next month
    next_month_start = month_end + pd.Timedelta(days=1)
    next_month_end = next_month_start + pd.offsets.BDay(5)  # At most 5 biz days
    df_next = df[(df.index >= next_month_start) & (df.index <= next_month_end)]
    post_peak_prices = df_next[sgov].dropna()

    if post_peak_prices.empty:
        continue

    sgov_low_price = post_peak_prices.min()
    sgov_low_day = post_peak_prices.idxmin()

    drop_pct = (sgov_low_price - sgov_peak_price) / sgov_peak_price * 100

    print(f"{month_start.strftime('%Y-%m')}: Peak {sgov_peak_price:.4f} on {sgov_peak_day.date()}, "
          f"Low {sgov_low_price:.4f} on {sgov_low_day.date()}, Drop% = {drop_pct:.3f}")

    # Append ALL results
    all_results.append({
        "Month": month_start.strftime("%Y-%m"),
        "SGOV_Peak_Date": sgov_peak_day.strftime("%Y-%m-%d"),
        "SGOV_Peak": sgov_peak_price,
        "SGOV_Low_Date": sgov_low_day.strftime("%Y-%m-%d"),
        "SGOV_Low": sgov_low_price,
        "Drop_%": round(drop_pct, 3)
    })

    # Append only if drop is negative
    if drop_pct < 0:
        filtered_results.append({
            "Month": month_start.strftime("%Y-%m"),
            "SGOV_Peak_Date": sgov_peak_day.strftime("%Y-%m-%d"),
            "SGOV_Peak": sgov_peak_price,
            "SGOV_Low_Date": sgov_low_day.strftime("%Y-%m-%d"),
            "SGOV_Low": sgov_low_price,
            "Drop_%": round(drop_pct, 3)
        })

# After loop ends, convert to DataFrame and save
summary_all_df = pd.DataFrame(all_results)
summary_filtered_df = pd.DataFrame(filtered_results)

print("\n🔎 All detected SGOV peak-low pairs (all months):")
print(summary_all_df)

print("\n📉 Filtered SGOV peak-low pairs (negative drops only):")
print(summary_filtered_df)

# Save to CSV
summary_all_df.to_csv("signals/sgov_post_peak_lows_full.csv", index=False)
summary_filtered_df.to_csv("signals/sgov_post_peak_lows.csv", index=False)

print(f"\n✅ SGOV post-peak low analysis complete.")
print(f"📄 Full results saved to signals/sgov_post_peak_lows_full.csv")
print(f"📄 Filtered results saved to signals/sgov_post_peak_lows.csv")
