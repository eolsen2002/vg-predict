"""
6/10/25, 11:54 AM; updated 12:43 pm- Complete config/etf_parameters.py file including:

The full ETF_CONFIG dictionary for all 6 ETFs with their parameters,

The helper function get_peak_day_window() that interprets the peak_day_range config for 
both positive (calendar day) and negative (relative to last trading day) ranges.
"""

import pandas as pd

ETF_CONFIG = {
    'USFR': {
        'peak_day_range': (18, 25),   # calendar days in month
        'post_peak_low_days': 6,
        'peak_validation': True,
    },
    'SGOV': {
        'peak_day_range': (-3, 0),    # last 3 trading days of month (relative)
        'post_peak_low_days': 3,
        'peak_validation': False,
    },
    'TFLO': {
        'peak_day_range': (-3, 0),
        'post_peak_low_days': 3,
        'peak_validation': False,
    },
    'BIL': {
        'peak_day_range': (-3, 0),
        'post_peak_low_days': 3,
        'peak_validation': False,
    },
    'SHV': {
        'peak_day_range': (-3, 0),
        'post_peak_low_days': 3,
        'peak_validation': False,
    },
    'ICSH': {
        'peak_day_range': (-3, 0),
        'post_peak_low_days': 3,
        'peak_validation': False,
    }
}

def get_peak_day_window(df, etf_symbol):
    """
    Given a DataFrame with a DateTimeIndex and an ETF symbol,
    returns the date range (start_date, end_date) for the peak window
    according to ETF_CONFIG parameters.

    Supports:
    - Positive day range tuple (start_day, end_day) as days of month (e.g. 18–25)
    - Negative day range tuple (start_offset, end_offset) relative to last trading day of month (e.g. -3 to 0)

    Parameters:
        df (pd.DataFrame): DataFrame with DateTimeIndex covering the target month.
        etf_symbol (str): ETF ticker symbol.

    Returns:
        tuple: (start_date, end_date) as pd.Timestamp objects for the peak window.
    """
    config = ETF_CONFIG.get(etf_symbol.upper())
    if not config:
        raise ValueError(f"No ETF config found for symbol: {etf_symbol}")

    start_day, end_day = config['peak_day_range']

    # Assume df covers one calendar month
    month_start = df.index.min().replace(day=1)
    month_end = df.index.max()

    if start_day >= 1 and end_day >= 1:
        # Positive days: calendar day numbers of the month
        target_start = month_start + pd.Timedelta(days=start_day - 1)
        target_end = month_start + pd.Timedelta(days=end_day - 1)
        # Snap to nearest available dates in index
        start_idx = df.index.get_indexer([target_start], method='nearest')[0]
        end_idx = df.index.get_indexer([target_end], method='nearest')[0]
        start_date = df.index[start_idx]
        end_date = df.index[end_idx]

    elif start_day < 0 and end_day <= 0:
        # Negative days: relative to last trading day in df index
        last_trading_day = df.index.max()
        last_idx = df.index.get_loc(last_trading_day)
        start_idx = max(0, last_idx + start_day)
        end_idx = last_idx + end_day
        start_date = df.index[start_idx]
        end_date = df.index[end_idx]

    else:
        raise ValueError("Invalid peak_day_range configuration: must be both positive or both negative")

    return start_date, end_date
