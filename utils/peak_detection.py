"""
utils/peak_detection.py

Peak Detection Utilities for Treasury ETFs

This module provides functions to detect monthly post-peak highs for
Treasury ETFs based on their specific trading patterns.

Key Rules:
----------
- USFR typically peaks between days 18 and 25 of each month.
- Other ETFs typically peak on the last trading day of the calendar month.
- A minimum rebound of 0.2% is required between the pre-peak low and the peak.
- Multi-day peaks and timing between low and peak are also tracked.

Functions:
----------
- find_post_peak_peaks(etf_name: str, df: pd.DataFrame) -> pd.DataFrame:
    Detects monthly peak signals for the specified ETF.
"""

import pandas as pd
from datetime import timedelta

REB_THRESHOLD = 0.002  # Minimum rebound threshold (0.2%)

def find_post_peak_peaks(etf_name: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify monthly post-peak highs for a given ETF.

    Parameters:
    -----------
    etf_name : str
        The ticker/name of the ETF column in the DataFrame.
    df : pd.DataFrame
        Historical daily price data with 'Date' column and ETF price columns.

    Returns:
    --------
    pd.DataFrame
        DataFrame of monthly peak statistics with standard columns:
        'ETF', 'Month', 'Low_Date', 'Low', 'Peak_Date', 'Peak', etc.
    """
    etf_df = df[['Date', etf_name]].dropna().copy()
    etf_df['Date'] = pd.to_datetime(etf_df['Date'])
    etf_df.set_index('Date', inplace=True)

    monthly_peaks = []

    for month, group in etf_df.groupby(pd.Grouper(freq='M')):
        if group.empty:
            continue

        # USFR: peak window from day 18 to 25
        if etf_name == 'USFR':
            peak_window = group[(group.index.day >= 18) & (group.index.day <= 25)]
            if peak_window.empty:
                continue
            peak_date = peak_window[etf_name].idxmax()
            peak_value = peak_window[etf_name].max()
        else:
            last_day = group.index.max()
            peak_window = group[group.index == last_day]
            if peak_window.empty:
                continue
            peak_date = last_day
            peak_value = peak_window[etf_name].iloc[0]

        # Pre-peak low in prior 10 days
        pre_peak = etf_df.loc[:peak_date - timedelta(days=1)].tail(10)
        if pre_peak.empty:
            continue

        low_date = pre_peak[etf_name].idxmin()
        low_value = pre_peak[etf_name].min()
        rebound_pct = (peak_value - low_value) / low_value

        days_between = (peak_date - low_date).days
        is_multi_day_peak = peak_window[etf_name].eq(peak_value).sum() > 1
        was_peak_in_prior_month = peak_date.month != low_date.month or peak_date.year != low_date.year

        if rebound_pct >= REB_THRESHOLD:
            monthly_peaks.append({
                'ETF': etf_name,
                'Month': month.strftime('%Y-%m'),
                'Low_Date': low_date.date(),
                'Low': round(low_value, 4),
                'Peak_Date': peak_date.date(),
                'Peak': round(peak_value, 4),
                'Rebound_%': round(rebound_pct * 100, 3),
                'Days_Between_Low_and_Peak': days_between,
                'Multi_Peak_Days': peak_window[etf_name].eq(peak_value).sum(),
                'Is_Multi_Day_Peak': is_multi_day_peak,
                '10D_Low_Before_Peak': round(pre_peak[etf_name].min(), 4),
                'Was_Peak_in_Prior_Month': was_peak_in_prior_month
            })

    return pd.DataFrame(monthly_peaks)
