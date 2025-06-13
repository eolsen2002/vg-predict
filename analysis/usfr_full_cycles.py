# scripts/usfr_full_cycles.py
"""
Detects full low-to-peak cycles for USFR.
- Low typically occurs near the end of the month (e.g., 5/24/24)
- Peak occurs mid-to-late in the following month (e.g., 6/24/24)
- Enforces clean pattern: distinct low → recovery → peak, minimum 10-day gap

✅ What this script does:
Loads USFR data from your main price file.

For each month pair:

Looks for low in the last 10–13 trading days of Month 1.

Looks for peak in the mid-to-late part of Month 2.

Ensures a minimum 10-day gap between low and peak.

Only records valid upward cycles with a positive % gain.

Last updated: 2025-06-12, 8:59 pm
"""

import pandas as pd

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

        if (peak_day - low_day).days < 10:
            continue  # too close — likely noise

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
