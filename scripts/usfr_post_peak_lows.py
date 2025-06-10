"""
scripts/usfr_post_peak_lows.py
Description:
Detects USFR's lowest price within post-peak days after its monthly peak 
(typically days 18–25 from config) to identify ideal re-entry points.
Outputs CSV with monthly peak/low dates and drop percentages.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from utils.data_loader import load_etf_data
from config.etf_parameters import ETF_CONFIG, get_peak_day_window

def detect_post_peak_lows(df, etf_symbol='USFR'):
    """
    Detects post-peak lows for a given ETF.

    Parameters:
        df (pd.DataFrame): Preprocessed ETF price data with Date index.
        etf_symbol (str): ETF ticker symbol to analyze.

    Returns:
        pd.DataFrame: Summary with monthly peak/low dates and drop percentages.
    """
    latest_date = df.index.max()
    months = pd.date_range(start=df.index.min(), end=latest_date, freq='MS')

    post_peak_low_days = ETF_CONFIG[etf_symbol]['post_peak_low_days']
    results = []

    for month_start in months:
        month_end = month_start + pd.offsets.MonthEnd(0)
        df_month = df.loc[month_start:month_end]

        if df_month.empty or df_month[etf_symbol].isnull().all():
            continue

        # Get dynamic peak day window for this month's data
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

        # Find next N trading days after peak
        post_peak = df[df.index > etf_peak_day]
        post_peak = post_peak[post_peak[etf_symbol].notna()]
        post_peak_trading_days = post_peak.head(post_peak_low_days)

        if post_peak_trading_days.empty:
            continue

        low_price = post_peak_trading_days[etf_symbol].min()
        low_day = post_peak_trading_days[post_peak_trading_days[etf_symbol] == low_price].index[0]

        drop_pct = (low_price - etf_peak_price) / etf_peak_price * 100

        if etf_peak_price > 0 and low_price > 0 and drop_pct > -5:
            results.append({
                "Month": month_start.strftime("%Y-%m"),
                f"{etf_symbol}_Peak_Date": etf_peak_day.strftime("%Y-%m-%d"),
                f"{etf_symbol}_Peak": etf_peak_price,
                f"{etf_symbol}_Low_Date": low_day.strftime("%Y-%m-%d"),
                f"{etf_symbol}_Low": low_price,
                "Drop_%": round(drop_pct, 3)
            })

    return pd.DataFrame(results)

def main():
    # Load and preprocess data using your helper
    df = load_etf_data('data/etf_prices_2023_2025.csv')

    # Run the detection for USFR
    summary_df = detect_post_peak_lows(df, etf_symbol='USFR')

    # Save results to CSV
    summary_df.to_csv("signals/usfr_post_peak_lows.csv", index=False)
    print("📉 USFR post-peak low analysis complete. Saved to signals/usfr_post_peak_lows.csv.")

if __name__ == "__main__":
    main()
