"""
scripts/other_etfs_post_peak_lows.py
Description:
Detects post-peak lows for 5 Treasury ETFs (SGOV, BIL, SHV, TFLO, ICSH),
which usually peak in the last 3 trading days of the month and drop within next 1-3 days.
Outputs combined CSV with one row per month and columns for each ETF’s peak/low dates and drop %.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from utils.data_loader import load_etf_data
from config.etf_parameters import ETF_CONFIG, get_peak_day_window

# List of ETFs to analyze in this script
OTHER_ETFS = ['SGOV', 'BIL', 'SHV', 'TFLO', 'ICSH']

def detect_post_peak_lows_combined(df, etf_symbols=OTHER_ETFS):
    """
    Detects post-peak lows for multiple ETFs and combines results into a single DataFrame
    with one row per month and separate columns per ETF for peak/low info and drop %.

    Parameters:
        df (pd.DataFrame): ETF price data with DateTimeIndex.
        etf_symbols (list): List of ETF tickers.

    Returns:
        pd.DataFrame: Combined DataFrame indexed by month, columns for each ETF’s peak and low info.
    """
    latest_date = df.index.max()
    months = pd.date_range(start=df.index.min(), end=latest_date, freq='MS')

    combined_results = []

    for month_start in months:
        month_end = month_start + pd.offsets.MonthEnd(0)
        df_month = df.loc[month_start:month_end]

        # Skip month if no data at all
        if df_month.empty:
            continue

        month_data = {'Month': month_start.strftime("%Y-%m")}

        for etf_symbol in etf_symbols:
            # Skip if no data for this ETF in month
            if etf_symbol not in df_month.columns or df_month[etf_symbol].isnull().all():
                # Fill with NaNs for consistency
                month_data.update({
                    f"{etf_symbol}_Peak_Date": None,
                    f"{etf_symbol}_Peak": None,
                    f"{etf_symbol}_Low_Date": None,
                    f"{etf_symbol}_Low": None,
                    f"{etf_symbol}_Drop_%": None,
                })
                continue

            try:
                # Get concrete peak window dates
                peak_start_date, peak_end_date = get_peak_day_window(df_month, etf_symbol)
            except Exception as e:
                print(f"⚠️ Skipping peak window for {etf_symbol} in {month_start.strftime('%Y-%m')} due to error: {e}")
                # Fill with NaNs
                month_data.update({
                    f"{etf_symbol}_Peak_Date": None,
                    f"{etf_symbol}_Peak": None,
                    f"{etf_symbol}_Low_Date": None,
                    f"{etf_symbol}_Low": None,
                    f"{etf_symbol}_Drop_%": None,
                })
                continue

            # Filter ETF data in peak window
            df_peak_window = df_month.loc[peak_start_date:peak_end_date]

            if df_peak_window.empty or df_peak_window[etf_symbol].isnull().all():
                # No valid peak data in window
                month_data.update({
                    f"{etf_symbol}_Peak_Date": None,
                    f"{etf_symbol}_Peak": None,
                    f"{etf_symbol}_Low_Date": None,
                    f"{etf_symbol}_Low": None,
                    f"{etf_symbol}_Drop_%": None,
                })
                continue

            # Find peak price and day in peak window
            max_price = df_peak_window[etf_symbol].max()
            peak_candidates = df_peak_window[df_peak_window[etf_symbol] == max_price]
            etf_peak_day = peak_candidates.index.max()
            etf_peak_price = max_price

            # Find next N trading days after peak for low detection
            post_peak_low_days = ETF_CONFIG[etf_symbol]['post_peak_low_days']
            post_peak = df[df.index > etf_peak_day]
            post_peak = post_peak[post_peak[etf_symbol].notna()]
            post_peak_trading_days = post_peak.head(post_peak_low_days)

            if post_peak_trading_days.empty:
                # No data after peak
                month_data.update({
                    f"{etf_symbol}_Peak_Date": etf_peak_day.strftime("%Y-%m-%d"),
                    f"{etf_symbol}_Peak": etf_peak_price,
                    f"{etf_symbol}_Low_Date": None,
                    f"{etf_symbol}_Low": None,
                    f"{etf_symbol}_Drop_%": None,
                })
                continue

            low_price = post_peak_trading_days[etf_symbol].min()
            low_day = post_peak_trading_days[post_peak_trading_days[etf_symbol] == low_price].index[0]

            drop_pct = (low_price - etf_peak_price) / etf_peak_price * 100

            # Filter unrealistic drops (greater than -5%)
            if etf_peak_price > 0 and low_price > 0 and drop_pct > -5:
                drop_pct = round(drop_pct, 3)
            else:
                drop_pct = None  # Treat as no valid drop

            # Add ETF results for this month
            month_data.update({
                f"{etf_symbol}_Peak_Date": etf_peak_day.strftime("%Y-%m-%d"),
                f"{etf_symbol}_Peak": etf_peak_price,
                f"{etf_symbol}_Low_Date": low_day.strftime("%Y-%m-%d"),
                f"{etf_symbol}_Low": low_price,
                f"{etf_symbol}_Drop_%": drop_pct,
            })

        combined_results.append(month_data)

    return pd.DataFrame(combined_results)


def main():
    """
    Load ETF price data, detect combined post-peak lows for multiple ETFs,
    and save the results to CSV.
    """
    df = load_etf_data('data/etf_prices_2023_2025.csv')

    summary_df = detect_post_peak_lows_combined(df)

    summary_df.to_csv("signals/other_etfs_post_peak_lows.csv", index=False)
    print("📉 Other 5 ETFs post-peak low analysis complete. Saved to signals/other_etfs_post_peak_lows.csv.")


if __name__ == "__main__":
    main()
