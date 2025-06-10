# scripts/generate_low_csvs.py
"""
Purpose:
Generate post-peak low CSVs for 6 Treasury ETFs using ETF-specific timing rules.

USFR:     peak = day 18–25, low = next 1–6 calendar days
Others:   peak = last trading day of month or prior if weekend, low = next 1–3 trading days

Input:
- data/etf_prices_2023_2025.csv

Output:
- signals/[etf]_post_peak_lows.csv
"""

import pandas as pd
import os
from datetime import timedelta

ETF_LIST = ['USFR', 'SGOV', 'BIL', 'TFLO', 'SHV', 'ICSH']
INPUT_CSV = 'data/etf_prices_2023_2025.csv'
OUTPUT_DIR = 'signals'
REB_THRESHOLD = 0.000  # capture all drops for now

def find_post_peak_lows(etf_name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Find post-peak lows based on ETF-specific timing rules."""
    etf_df = df[['Date', etf_name]].dropna().copy()
    etf_df['Date'] = pd.to_datetime(etf_df['Date'])
    etf_df.set_index('Date', inplace=True)

    monthly_lows = []

    for month, group in etf_df.groupby(pd.Grouper(freq='M')):
        if group.empty:
            continue

        # === USFR logic: peak = day 18–25 ===
        if etf_name == 'USFR':
            peak_window = group[(group.index.day >= 18) & (group.index.day <= 25)]
            if peak_window.empty:
                continue
            peak_date = peak_window[etf_name].idxmax()
            peak_value = peak_window[etf_name].max()
            lookahead_end = peak_date + timedelta(days=6)
            low_window = etf_df.loc[peak_date + timedelta(days=1):lookahead_end]

        # === Others: last trading day or prior if weekend ===
        else:
            last_trading_days = group.tail(3)
            if last_trading_days.empty:
                continue

            # Default to last day as peak
            peak_date = last_trading_days.index[-1]
            peak_value = last_trading_days[etf_name].iloc[-1]

            if len(last_trading_days) >= 2:
                second_last_price = last_trading_days[etf_name].iloc[-2]
                if peak_value < second_last_price:
                    peak_date = last_trading_days.index[-2]
                    peak_value = second_last_price

            try:
                peak_idx = etf_df.index.get_loc(peak_date)
                low_window = etf_df.iloc[peak_idx + 1 : peak_idx + 4]
            except KeyError:
                continue

        if low_window.empty:
            continue

        low_date = low_window[etf_name].idxmin()
        low_value = low_window[etf_name].min()

        multi_low_dates = low_window[low_window[etf_name] == low_value].index
        is_multi_day_low = len(multi_low_dates) > 1

        drop_pct = round(((low_value - peak_value) / peak_value) * 100, 3)
        days_between = (low_date - peak_date).days
        was_low_in_next_month = low_date.month != peak_date.month or low_date.year != peak_date.year

        ten_day_window_before_peak = etf_df.loc[peak_date - timedelta(days=10):peak_date - timedelta(days=1)]
        high_before_peak = ten_day_window_before_peak[etf_name].max() if not ten_day_window_before_peak.empty else None

        ten_day_window_after_low = etf_df.loc[low_date + timedelta(days=1):low_date + timedelta(days=10)]
        low_after_low = ten_day_window_after_low[etf_name].min() if not ten_day_window_after_low.empty else None

        if drop_pct < -REB_THRESHOLD:
            monthly_lows.append({
                'Month': month.strftime('%Y-%m'),
                f'{etf_name}_Peak_Date': peak_date.date(),
                f'{etf_name}_Peak': round(peak_value, 4),
                f'{etf_name}_Low_Date': low_date.date(),
                f'{etf_name}_Low': round(low_value, 4),
                'Drop_%': round(drop_pct, 4),
                'Days_Between_Peak_and_Low': days_between,
                'Multi_Low_Days': len(multi_low_dates),
                'Is_Multi_Day_Low': is_multi_day_low,
                '10D_High_Before_Peak': round(high_before_peak, 4) if high_before_peak else None,
                '10D_Low_After_Low': round(low_after_low, 4) if low_after_low else None,
                'Was_Low_in_Next_Month': was_low_in_next_month
            })

    return pd.DataFrame(monthly_lows)

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    try:
        df = pd.read_csv(INPUT_CSV)
    except Exception as e:
        print(f"❌ Failed to load input CSV: {e}")
        return

    for etf in ETF_LIST:
        print(f"📊 Processing {etf}...")
        result_df = find_post_peak_lows(etf, df)

        if not result_df.empty:
            output_file = os.path.join(OUTPUT_DIR, f"{etf.lower()}_post_peak_lows.csv")
            result_df.to_csv(output_file, index=False)
            print(f"✅ Saved: {output_file}")
        else:
            print(f"⚠️ No valid swing data found for {etf}")

if __name__ == "__main__":
    main()
