# scripts/generate_peak_csvs.py
"""
Purpose:
Generate post-peak peak CSVs for 6 Treasury ETFs using ETF-specific timing rules.

USFR:     peak = day 18–25, validate with 10-day prior low
Others:   peak = highest in last 3 trading days of calendar month

Input:
- data/etf_prices_2023_2025.csv

Output:
- signals/[etf]_post_peak_highs.csv
"""

import pandas as pd
import os
from datetime import timedelta

ETF_LIST = ['USFR', 'SGOV', 'BIL', 'TFLO', 'SHV', 'ICSH']
INPUT_CSV = 'data/etf_prices_2023_2025.csv'
OUTPUT_DIR = 'signals'
REB_THRESHOLD = 0.002  # 0.2% rebound required for a peak

os.makedirs(OUTPUT_DIR, exist_ok=True)

def find_post_peak_peaks(etf_name: str, df: pd.DataFrame) -> pd.DataFrame:
    etf_df = df[['Date', etf_name]].dropna().copy()
    etf_df['Date'] = pd.to_datetime(etf_df['Date'])
    etf_df.set_index('Date', inplace=True)

    monthly_peaks = []

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

        # === Others: peak = highest in last 3 trading days of calendar month ===
        else:
            last_day = group.index.max()
            # Get last 3 business days including last_day
            last_3_trading_days = group[group.index >= last_day - pd.offsets.BDay(2)]
            if last_3_trading_days.empty:
                continue
            peak_window = last_3_trading_days
            peak_date = peak_window[etf_name].idxmax()
            peak_value = peak_window[etf_name].max()

        # Look back 10 days for pre-peak low
        pre_peak = etf_df.loc[:peak_date - timedelta(days=1)].tail(10)
        if pre_peak.empty:
            continue

        low_date = pre_peak[etf_name].idxmin()
        low_value = pre_peak[etf_name].min()
        rebound_pct = round(((peak_value - low_value) / low_value) * 100, 3)
        days_between = (peak_date - low_date).days
        was_peak_in_prior_month = peak_date.month != low_date.month or peak_date.year != low_date.year

        multi_peak_dates = peak_window[peak_window[etf_name] == peak_value].index
        is_multi_day_peak = len(multi_peak_dates) > 1

        if rebound_pct >= REB_THRESHOLD:
            monthly_peaks.append({
                'Month': month.strftime('%Y-%m'),
                f'{etf_name}_Low_Date': low_date.date(),
                f'{etf_name}_Low': round(low_value, 4),
                f'{etf_name}_Peak_Date': peak_date.date(),
                f'{etf_name}_Peak': round(peak_value, 4),
                'Rebound_%': rebound_pct,
                'Days_Between_Low_and_Peak': days_between,
                'Multi_Peak_Days': len(multi_peak_dates),
                'Is_Multi_Day_Peak': is_multi_day_peak,
                '10D_Low_Before_Peak': round(pre_peak[etf_name].min(), 4),
                'Was_Peak_in_Prior_Month': was_peak_in_prior_month
            })

    return pd.DataFrame(monthly_peaks)

def main():
    try:
        df = pd.read_csv(INPUT_CSV)
    except Exception as e:
        print(f"❌ Failed to load input CSV: {e}")
        return

    for etf in ETF_LIST:
        print(f"📈 Processing {etf}...")
        result_df = find_post_peak_peaks(etf, df)

        if not result_df.empty:
            output_file = os.path.join(OUTPUT_DIR, f"{etf.lower()}_post_peak_highs.csv")
            result_df.to_csv(output_file, index=False)
            print(f"✅ Saved: {output_file}")
        else:
            print(f"⚠️ No valid peak data found for {etf}")

if __name__ == "__main__":
    main()
