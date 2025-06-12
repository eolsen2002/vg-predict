# utils/peak_detection.py — updated 6/11/25, 11:20 PM

"""
Peak Detection Utilities for Treasury ETFs

This module defines logic for identifying post-peak highs of Treasury ETFs
on a monthly basis using price rebound thresholds and ETF-specific timing rules.

Key Rules:
----------
- USFR:
  * Peak typically occurs between the 18th and 25th of each month.
  * Peak is defined as the highest price during this window.

- Other ETFs (SGOV, BIL, SHV, TFLO, ICSH):
  * Peak is defined as the highest price during the full calendar month.
  * If multiple days tie for the highest price, the latest one is used.

- A minimum rebound of 0.2% from a 10-day low before the peak is required.
- If no valid 10-day pre-peak low exists, the month is skipped.
- Additional diagnostic attributes include multi-day peaks and time from low to peak.

Functions:
----------
- find_post_peak_peaks(etf_name: str, df: pd.DataFrame) -> pd.DataFrame
    Detects monthly post-peak highs and related statistics for the given ETF.

Input:
------
- DataFrame with at least:
    'Date', and one column per ETF (e.g., 'SGOV', 'USFR', etc.)

Output:
-------
- DataFrame of detected monthly peak signals with fields:
    'ETF', 'Month', 'Low_Date', 'Low', 'Peak_Date', 'Peak',
    'Rebound_%', 'Days_Between_Low_and_Peak', 'Multi_Peak_Days',
    'Is_Multi_Day_Peak', '10D_Low_Before_Peak', 'Was_Peak_in_Prior_Month'

Changelog Summary – 6/11/25 Updates:
-------------------------------------
✅ Removed arbitrary <10 trading day month filter (overly restrictive)  
✅ Retained USFR-specific logic for intra-month peak window (days 18–25)  
✅ Ensured all months with valid data are considered  
✅ Maintained rebound threshold, low detection logic, and diagnostics  
✅ Clarified docstring for maintainability and debugging  
"""

import pandas as pd
from datetime import timedelta

REB_THRESHOLD = 0.002  # Minimum rebound threshold (0.2%)

def find_post_peak_peaks(etf_name: str, df: pd.DataFrame) -> pd.DataFrame:
    etf_df = df[['Date', etf_name]].dropna().copy()
    etf_df['Date'] = pd.to_datetime(etf_df['Date'])
    etf_df.set_index('Date', inplace=True)

    monthly_peaks = []

    for month, group in etf_df.groupby(pd.Grouper(freq='M')):
        if group.empty:
            continue

        group = group.sort_index()

        # --- USFR Special Handling: Day 18–25 window ---
        if etf_name == 'USFR':
            peak_window = group[(group.index.day >= 18) & (group.index.day <= 25)]
            if peak_window.empty:
                continue
            peak_value = peak_window[etf_name].max()
            peak_date = peak_window[peak_window[etf_name] == peak_value].index[-1]

        # --- Other ETFs: Use highest price in full month ---
        else:
            peak_value = group[etf_name].max()
            peak_date = group[group[etf_name] == peak_value].index[-1]  # Use latest if tie

        # --- Look back for 10-day low before peak ---
        pre_peak = etf_df.loc[:peak_date - timedelta(days=1)].tail(10)
        if pre_peak.empty:
            continue

        low_value = pre_peak[etf_name].min()
        low_date = pre_peak[etf_name].idxmin()

        rebound_pct = (peak_value - low_value) / low_value
        if rebound_pct < REB_THRESHOLD:
            continue

        days_between = (peak_date - low_date).days
        is_multi_day_peak = group[etf_name].eq(peak_value).sum() > 1
        was_peak_in_prior_month = peak_date.month != low_date.month or peak_date.year != low_date.year

        monthly_peaks.append({
            'ETF': etf_name,
            'Month': month.strftime('%Y-%m'),
            'Low_Date': low_date.date(),
            'Low': round(low_value, 4),
            'Peak_Date': peak_date.date(),
            'Peak': round(peak_value, 4),
            'Rebound_%': round(rebound_pct * 100, 3),
            'Days_Between_Low_and_Peak': days_between,
            'Multi_Peak_Days': group[etf_name].eq(peak_value).sum(),
            'Is_Multi_Day_Peak': is_multi_day_peak,
            '10D_Low_Before_Peak': round(low_value, 4),
            'Was_Peak_in_Prior_Month': was_peak_in_prior_month
        })

    return pd.DataFrame(monthly_peaks)
