# scripts/generate_peak_low_signals.py
"""ADD DESCRIPTION
ADD DATE AND TIME WHEN UPDATED"""

import pandas as pd
from datetime import datetime

df = pd.read_csv("data/etf_prices_2023_2025.csv", index_col=0, parse_dates=True)
df.index = pd.to_datetime(df.index, utc=True).tz_convert(None)

etfs = ["USFR", "SGOV", "TFLO", "BIL", "SHV", "ICSH"]

def get_last_trading_day(df_month):
    valid_days = df_month.dropna(how='all')
    return valid_days.index.max() if not valid_days.empty else None

def find_peak_dates(df, etf, months):
    peaks = []
    for month_start in months:
        month_end = month_start + pd.offsets.MonthEnd(0)
        df_month = df[(df.index >= month_start) & (df.index <= month_end)]

        if df_month.empty or df_month[etf].isnull().all():
            continue

        if etf == "USFR":
            df_mid = df_month[(df_month.index.day >= 21) & (df_month.index.day <= 26)]
            if df_mid.empty:
                continue
            peak_price = df_mid[etf].max()
            peak_day = df_mid[df_mid[etf] == peak_price].index.max()
        else:
            peak_day = get_last_trading_day(df_month)
            if peak_day is None:
                continue
            peak_price = df_month.loc[peak_day, etf]

        peaks.append({
            "Month": month_start.strftime("%Y-%m"),
            "ETF": etf,
            "Peak_Date": peak_day,
            "Peak": peak_price
        })

    return pd.DataFrame(peaks)

def find_post_peak_lows(df, etf, peak_df):
    lows = []
    for _, row in peak_df.iterrows():
        peak_day = row["Peak_Date"]
        peak_price = row["Peak"]
        post_peak = df[df.index > peak_day]
        post_peak = post_peak[post_peak[etf].notna()]
        post_peak_3 = post_peak.head(3)

        if post_peak_3.empty:
            continue

        low_price = post_peak_3[etf].min()
        low_day = post_peak_3[post_peak_3[etf] == low_price].index[0]
        drop_pct = (low_price - peak_price) / peak_price * 100

        if peak_price > 0 and low_price > 0 and drop_pct > -5:
            lows.append({
                "Month": row["Month"],
                "ETF": etf,
                "Peak_Date": peak_day,
                "Peak": peak_price,
                "Low_Date": low_day,
                "Low": low_price,
                "Drop_%": round(drop_pct, 3)
            })

    return pd.DataFrame(lows)

def main():
    latest_date = df.index.max()
    months = pd.date_range(start="2023-01-01", end=latest_date, freq='MS')

    all_peaks = []
    all_lows = []

    for etf in etfs:
        peak_df = find_peak_dates(df, etf, months)
        low_df = find_post_peak_lows(df, etf, peak_df)

        all_peaks.append(peak_df)
        all_lows.append(low_df)

    pd.concat(all_peaks).to_csv("signals/all_etfs_peaks.csv", index=False)
    pd.concat(all_lows).to_csv("signals/all_etfs_post_peak_lows.csv", index=False)

    print("✅ Peaks and post-peak lows saved (long-form) to signals/")

if __name__ == "__main__":
    main()
