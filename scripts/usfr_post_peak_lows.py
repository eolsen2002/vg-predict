"""
scripts/usfr_post_peak_lows.py
Description:
Detects USFR's lowest price within post-peak days after its monthly peak 
(typically days 18–25 from config) to identify ideal re-entry points.
Outputs CSV with monthly peak/low dates, drop %, and modal low day (for countdowns).
Last update: 6/15/2025, 10:26 PM
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from collections import Counter
from utils.data_loader import load_etf_data
from config.etf_parameters import ETF_CONFIG, get_peak_day_window

def detect_post_peak_lows(df, etf_symbol='USFR'):
    latest_date = df.index.max()
    months = pd.date_range(start=df.index.min(), end=latest_date, freq='MS')

    post_peak_low_days = ETF_CONFIG[etf_symbol]['post_peak_low_days']
    results = []

    for month_start in months:
        month_end = month_start + pd.offsets.MonthEnd(0)
        df_month = df.loc[month_start:month_end]

        if df_month.empty or df_month[etf_symbol].isnull().all():
            continue

        try:
            peak_start_date, peak_end_date = get_peak_day_window(df_month, etf_symbol)
        except Exception as e:
            print(f"⚠️ Skipping {month_start.strftime('%Y-%m')} due to window error: {e}")
            continue

        df_peak_window = df_month.loc[peak_start_date:peak_end_date]
        if df_peak_window.empty:
            continue

        max_price = df_peak_window[etf_symbol].max()
        peak_candidates = df_peak_window[df_peak_window[etf_symbol] == max_price]
        etf_peak_day = peak_candidates.index.max()
        etf_peak_price = max_price

        post_peak = df[df.index > etf_peak_day]
        post_peak = post_peak[post_peak[etf_symbol].notna()]
        post_peak_trading_days = post_peak.head(post_peak_low_days)

        if post_peak_trading_days.empty:
            continue

        low_price = post_peak_trading_days[etf_symbol].min()
        low_day = post_peak_trading_days[post_peak_trading_days[etf_symbol] == low_price].index[0]
        drop_pct = (low_price - etf_peak_price) / etf_peak_price * 100
        drop_pct = round(drop_pct, 3) if etf_peak_price > 0 and low_price > 0 and drop_pct > -5 else None

        modal_low_day = Counter(post_peak_trading_days.index.day).most_common(1)[0][0]

        results.append({
            "Month": month_start.strftime("%Y-%m"),
            f"{etf_symbol}_Peak_Date": etf_peak_day.strftime("%Y-%m-%d"),
            f"{etf_symbol}_Peak": round(etf_peak_price, 4),
            f"{etf_symbol}_Low_Date": low_day.strftime("%Y-%m-%d"),
            f"{etf_symbol}_Low": round(low_price, 4),
            "Drop_%": drop_pct,
            f"{etf_symbol}_Low_Modal_Day": modal_low_day
        })

    return pd.DataFrame(results)

def run_usfr_post_peak_lows():
    df = load_etf_data('data/etf_prices_2023_2025.csv')
    summary_df = detect_post_peak_lows(df, etf_symbol='USFR')
    summary_df.to_csv("signals/usfr_post_peak_lows.csv", index=False)
    return summary_df

def main():
    df = load_etf_data('data/etf_prices_2023_2025.csv')
    summary_df = detect_post_peak_lows(df, etf_symbol='USFR')
    summary_df.to_csv("signals/usfr_post_peak_lows.csv", index=False)
    print("📉 USFR post-peak low analysis complete. Saved to signals/usfr_post_peak_lows.csv.")

if __name__ == "__main__":
    main()
