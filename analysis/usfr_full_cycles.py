# scripts/usfr_full_cycles.py
"""
Detects full low-to-peak cycles for USFR.

Cycle definition:
- Low typically occurs near the end of the month (e.g., 5/24/24)
- Peak typically occurs mid-to-late in the following month (e.g., 6/24/24)
- Requires a clean pattern: distinct low → recovery → peak, with minimum 10-day separation
- Adds confirmation logic:
  - Peak must be higher than following 1–2 days to avoid false peaks
  - Low must be a local minimum post-peak (lowest among next 2 days)

Output:
- Saves full cycle data to signals/usfr_full_cycles.csv with gain %

Last updated: 2025-06-13
"""

import pandas as pd
from datetime import timedelta

def load_usfr_data(csv_path="data/etf_prices_2023_2025.csv"):
    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(None)
    return df[["USFR"]].dropna()

def detect_usfr_full_cycles(df):
    results = []
    months = pd.date_range(start=df.index.min(), end=df.index.max(), freq="MS")

    for i in range(len(months) - 1):
        month1 = months[i]
        month2 = months[i + 1]

        # Define late part of month1 and mid-late part of month2
        late_month1 = df[(df.index >= month1 + pd.Timedelta(days=18)) & (df.index <= month1 + pd.offsets.MonthEnd(0))]
        mid_late_month2 = df[(df.index >= month2 + pd.Timedelta(days=15)) & (df.index <= month2 + pd.offsets.MonthEnd(0))]

        if late_month1.empty or mid_late_month2.empty:
            continue

        # Detect low in late_month1
        low_price = late_month1["USFR"].min()
        low_day = late_month1[late_month1["USFR"] == low_price].index.min()

        # Detect peak in mid_late_month2
        peak_price = mid_late_month2["USFR"].max()
        peak_day = mid_late_month2[mid_late_month2["USFR"] == peak_price].index.max()

        # Require minimum 10-day gap
        if (peak_day - low_day).days < 10:
            continue

        # Confirm it's a valid peak: next 1–2 days must not be equal or higher
        future_days = df[(df.index > peak_day) & (df.index <= peak_day + timedelta(days=2))]
        if not future_days.empty and future_days["USFR"].max() >= peak_price:
            continue

        # Confirm it's a valid low: lowest point within next 2 days
        post_low_window = df[(df.index >= low_day) & (df.index <= low_day + timedelta(days=2))]
        if low_price != post_low_window["USFR"].min():
            continue

        gain_pct = round((peak_price - low_price) / low_price * 100, 3)

        if gain_pct > 0:
            results.append({
                "Cycle_Start_Month": month1.strftime("%Y-%m"),
                "Low_Date": low_day.strftime("%Y-%m-%d"),
                "Low": low_price,
                "Peak_Date": peak_day.strftime("%Y-%m-%d"),
                "Peak": peak_price,
                "Gain_%": gain_pct
            })

    return pd.DataFrame(results)

def main():
    df = load_usfr_data()
    full_cycles = detect_usfr_full_cycles(df)
    full_cycles.to_csv("signals/usfr_full_cycles.csv", index=False)
    print("✅ USFR full low-to-peak cycles saved to signals/usfr_full_cycles.csv")

if __name__ == "__main__":
    main()
