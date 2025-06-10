"""
generate_etf_day_stats.py

Purpose:
--------
Generate a lookup table of daily price statistics for each Treasury ETF,
broken down by trading day number within each calendar month.

Why:
----
This table helps compare the current month's trading day price against
historical averages and ranges for that specific trading day in prior months,
enabling better detection of unusual price movements or expected values.

Input:
------
- CSV file with daily ETF prices for multiple ETFs (e.g., data/etf_prices_2023_2025.csv)
  The file must include a 'Date' column and columns for each ETF ticker.

Output:
-------
- CSV file with stats saved as signals/etf_day_stats.csv, containing:
  ETF, Trading_Day, Count, Mean, Min, Max, Median, Std

How:
----
- Assign a "trading day" number within each month for each date (starting at 1).
- For each ETF and trading day number, calculate summary statistics over all months.
- Save these aggregated stats for fast historical reference and comparison.

"""

import pandas as pd
import os

INPUT_CSV = 'data/etf_prices_2023_2025.csv'
OUTPUT_CSV = 'signals/etf_day_stats.csv'
ETF_LIST = ['USFR', 'SGOV', 'BIL', 'TFLO', 'SHV', 'ICSH']

os.makedirs('signals', exist_ok=True)

def assign_trading_day(df):
    """
    Add a 'Trading_Day' column that numbers each trading day within
    a given month starting at 1.

    Parameters:
    -----------
    df: DataFrame with a 'Date' column (datetime64)

    Returns:
    --------
    DataFrame with new 'Trading_Day' column
    """
    df = df.sort_values('Date').copy()
    # Create a YearMonth period for grouping
    df['YearMonth'] = df['Date'].dt.to_period('M')
    # Assign trading day by counting days within each YearMonth group
    df['Trading_Day'] = df.groupby('YearMonth').cumcount() + 1
    return df

def generate_lookup_table(df_all):
    """
    Generate the lookup table with statistics for each ETF and trading day.

    Parameters:
    -----------
    df_all: DataFrame with Date and ETF price columns

    Returns:
    --------
    DataFrame with aggregated stats: ETF, Trading_Day, Count, Mean, Min, Max, Median, Std
    """
    records = []

    for etf in ETF_LIST:
        # Extract date and price columns for the ETF
        etf_df = df_all[['Date', etf]].dropna().copy()
        etf_df = etf_df.rename(columns={etf: 'Price'})
        etf_df['Date'] = pd.to_datetime(etf_df['Date'])

        # Assign trading day number per month
        etf_df = assign_trading_day(etf_df)

        # Group prices by trading day number and calculate stats
        grouped = etf_df.groupby('Trading_Day')['Price']

        for trading_day, group in grouped:
            count = group.count()
            mean = group.mean()
            min_val = group.min()
            max_val = group.max()
            median = group.median()
            std = group.std()

            records.append({
                'ETF': etf,
                'Trading_Day': trading_day,
                'Count': count,
                'Mean': round(mean, 5),
                'Min': round(min_val, 5),
                'Max': round(max_val, 5),
                'Median': round(median, 5),
                'Std': round(std, 5)
            })

    return pd.DataFrame(records)

def main():
    try:
        df_all = pd.read_csv(INPUT_CSV)
    except Exception as e:
        print(f"❌ Failed to load input CSV: {e}")
        return

    lookup_df = generate_lookup_table(df_all)
    lookup_df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Lookup table saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
