
"""
scripts/other_etfs_post_peak_lows.py
Description:
Detects post-peak lows for 5 Treasury ETFs (SGOV, BIL, SHV, TFLO, ICSH),
which usually peak in the last 3 trading days of the month and drop within next 1–3 days.
Outputs combined CSV with one row per month and columns for each ETF’s peak/low dates, drop %, and modal low day.
Updated 6/15/2025 10:12 PM to include Low_Modal_Day fields to support signal countdowns.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from collections import Counter
from utils.data_loader import load_etf_data
from config.etf_parameters import ETF_CONFIG, get_peak_day_window

# List of ETFs to analyze in this script
OTHER_ETFS = ['SGOV', 'BIL', 'SHV', 'TFLO', 'ICSH']

def detect_post_peak_lows_combined(df, etf_symbols=OTHER_ETFS):
    latest_date = df.index.max()
    months = pd.date_range(start=df.index.min(), end=latest_date, freq='MS')
    combined_results = []

    for month_start in months:
        month_end = month_start + pd.offsets.MonthEnd(0)
        df_month = df.loc[month_start:month_end]

        if df_month.empty:
            continue

        month_data = {'Month': month_start.strftime("%Y-%m")}

        for etf_symbol in etf_symbols:
            if etf_symbol not in df_month.columns or df_month[etf_symbol].isnull().all():
                month_data.update({
                    f"{etf_symbol}_Peak_Date": None,
                    f"{etf_symbol}_Peak": None,
                    f"{etf_symbol}_Low_Date": None,
                    f"{etf_symbol}_Low": None,
                    f"{etf_symbol}_Drop_%": None,
                    f"{etf_symbol}_Low_Modal_Day": None,
                })
                continue

            try:
                peak_start_date, peak_end_date = get_peak_day_window(df_month, etf_symbol)
            except Exception as e:
                print(f"⚠️ Skipping peak window for {etf_symbol} in {month_start.strftime('%Y-%m')} due to error: {e}")
                month_data.update({
                    f"{etf_symbol}_Peak_Date": None,
                    f"{etf_symbol}_Peak": None,
                    f"{etf_symbol}_Low_Date": None,
                    f"{etf_symbol}_Low": None,
                    f"{etf_symbol}_Drop_%": None,
                    f"{etf_symbol}_Low_Modal_Day": None,
                })
                continue

            df_peak_window = df_month.loc[peak_start_date:peak_end_date]

            if df_peak_window.empty or df_peak_window[etf_symbol].isnull().all():
                month_data.update({
                    f"{etf_symbol}_Peak_Date": None,
                    f"{etf_symbol}_Peak": None,
                    f"{etf_symbol}_Low_Date": None,
                    f"{etf_symbol}_Low": None,
                    f"{etf_symbol}_Drop_%": None,
                    f"{etf_symbol}_Low_Modal_Day": None,
                })
                continue

            max_price = df_peak_window[etf_symbol].max()
            peak_candidates = df_peak_window[df_peak_window[etf_symbol] == max_price]
            etf_peak_day = peak_candidates.index.max()
            etf_peak_price = max_price

            post_peak_low_days = ETF_CONFIG[etf_symbol]['post_peak_low_days']
            post_peak = df[df.index > etf_peak_day]
            post_peak = post_peak[post_peak[etf_symbol].notna()]
            post_peak_trading_days = post_peak.head(post_peak_low_days)

            if post_peak_trading_days.empty:
                month_data.update({
                    f"{etf_symbol}_Peak_Date": etf_peak_day.strftime("%Y-%m-%d"),
                    f"{etf_symbol}_Peak": etf_peak_price,
                    f"{etf_symbol}_Low_Date": None,
                    f"{etf_symbol}_Low": None,
                    f"{etf_symbol}_Drop_%": None,
                    f"{etf_symbol}_Low_Modal_Day": None,
                })
                continue

            low_price = post_peak_trading_days[etf_symbol].min()
            low_day = post_peak_trading_days[post_peak_trading_days[etf_symbol] == low_price].index[0]

            drop_pct = (low_price - etf_peak_price) / etf_peak_price * 100
            drop_pct = round(drop_pct, 3) if etf_peak_price > 0 and low_price > 0 and drop_pct > -5 else None

            modal_low_day = Counter(post_peak_trading_days.index.day).most_common(1)[0][0]

            month_data.update({
                f"{etf_symbol}_Peak_Date": etf_peak_day.strftime("%Y-%m-%d"),
                f"{etf_symbol}_Peak": round(etf_peak_price, 4),
                f"{etf_symbol}_Low_Date": low_day.strftime("%Y-%m-%d"),
                f"{etf_symbol}_Low": round(low_price, 4),
                f"{etf_symbol}_Drop_%": drop_pct,
                f"{etf_symbol}_Low_Modal_Day": modal_low_day,
            })

        combined_results.append(month_data)

    return pd.DataFrame(combined_results)

def main():
    df = load_etf_data('data/etf_prices_2023_2025.csv')
    summary_df = detect_post_peak_lows_combined(df)
    summary_df.to_csv("signals/other_etfs_post_peak_lows.csv", index=False)
    print("📉 Other 5 ETFs post-peak low analysis complete. Saved to signals/other_etfs_post_peak_lows.csv.")

if __name__ == "__main__":
    main()
