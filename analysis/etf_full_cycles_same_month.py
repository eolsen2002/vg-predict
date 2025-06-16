# analysis/etf_full_cycles_same_month.py

"""
Detects same-month low-to-peak cycles for 5 short-duration Treasury ETFs:
SGOV, BIL, SHV, TFLO, ICSH.

For each ETF:
- Finds local low in days 1–5 of each month
- Finds local peak in days 25–end of month (or max so far if month incomplete)
- Calculates gain %, marks incomplete cycles if current month is not yet finished

Output:
- One CSV per ETF in signals/ (e.g., sgov_full_cycles.csv)
- Columns: Cycle_Month, Low_Date, Low, Peak_Date, Peak, Gain_%, Cycle_Complete

Last updated: 2025-06-15, 7:36 pm
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

DATA_PATH = Path("data/etf_prices_2023_2025.csv")
SIGNALS_DIR = Path("signals")
SIGNALS_DIR.mkdir(exist_ok=True)

df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
df.index = pd.to_datetime(df.index, utc=True).tz_convert(None)

etfs = ["SGOV", "BIL", "SHV", "TFLO", "ICSH"]

def get_low_window(df_month):
    return df_month[df_month.index.day <= 5]

def get_peak_window(df_month):
    return df_month[df_month.index.day >= 25]

def extract_same_month_cycles(df, etf):
    results = []
    months = pd.date_range(start="2023-01-01", end=df.index.max(), freq="MS")
    today = pd.Timestamp.today().normalize()

    for month_start in months:
        month_end = month_start + pd.offsets.MonthEnd(0)
        df_month = df[(df.index >= month_start) & (df.index <= month_end)]

        if df_month.empty or df_month[etf].isnull().all():
            continue

        low_window = get_low_window(df_month)
        if low_window.empty:
            continue

        low_price = low_window[etf].min()
        low_date = low_window[low_window[etf] == low_price].index.min()

        # Handle peak logic
        is_current_month = month_start.month == today.month and month_start.year == today.year
        if is_current_month:
            peak_window = df_month[df_month.index > low_date]  # Use data so far
        else:
            peak_window = get_peak_window(df_month)

        if peak_window.empty:
            continue

        peak_price = peak_window[etf].max()
        peak_date = peak_window[peak_window[etf] == peak_price].index.max()

        if peak_date > low_date and peak_price > 0 and low_price > 0:
            gain = (peak_price - low_price) / low_price * 100
            cycle_complete = not is_current_month
            results.append({
                "Cycle_Month": month_start.strftime("%Y-%m"),
                "Low_Date": low_date.date(),
                "Low": round(low_price, 6),
                "Peak_Date": peak_date.date(),
                "Peak": round(peak_price, 6),
                "Gain_%": round(gain, 3),
                "Cycle_Complete": cycle_complete,
                "Peak_Signal_Strength": 0  # Placeholder for future use
            })

    return pd.DataFrame(results)

def main():
    for etf in etfs:
        df_cycles = extract_same_month_cycles(df, etf)
        out_path = SIGNALS_DIR / f"{etf.lower()}_full_cycles.csv"
        df_cycles.to_csv(out_path, index=False)
        print(f"✅ {etf} cycles saved to {out_path}")

if __name__ == "__main__":
    main()