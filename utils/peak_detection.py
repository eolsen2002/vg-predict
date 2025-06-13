"""
utils/peak_detection.py
Peak Detection Utilities for Treasury ETFs

This module defines logic for identifying post-peak highs of Treasury ETFs
on a monthly basis using price rebound thresholds and ETF-specific timing rules.

Key Rules:
----------
- USFR:
  * Peak typically occurs between the 18th and 25th of each month.
  * Peak is defined as the highest price during this window.

- Other ETFs (SGOV, BIL, SHV, TFLO, ICSH):
  * Peak is defined as the highest price in the full calendar month.
  * However, lows in the last 10 days of the prior month are now considered to avoid missing valid rebound signals.

- A minimum ETF-specific rebound (typically 0.07–0.1%) from a valid 10-day low before the peak is required.
- If no valid 10-day pre-peak low exists, the month is skipped.
- Monthly detection logic respects ETF-specific windowing and fallback behavior.
- Data is sorted chronologically by date to ensure correct window handling.
- Debug logging is available via `debug=True`.

Functions:
----------
- find_post_peak_peaks(etf_name: str, df: pd.DataFrame, debug: bool = False) -> pd.DataFrame
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

Changelog – 2025-06-13:
------------------------
✅ Added prior-month 10-day lookback for all ETFs (not just USFR)
✅ Corrected logic to detect valid rebounds even when low is in previous month
✅ Retained strict day-18–25 filtering for USFR peak detection
✅ Improved debug logging granularity
"""

import pandas as pd

# Minimum % rebound thresholds for each ETF
REB_THRESHOLDS = {
    'USFR': 0.0010,   # 0.10%
    'SGOV': 0.0007,
    'BIL':  0.0007,
    'SHV':  0.0007,
    'TFLO': 0.0007,
    'ICSH': 0.0007
}

def find_post_peak_peaks(etf_name: str, df: pd.DataFrame, debug: bool = False) -> pd.DataFrame:
    etf_df = df[['Date', etf_name]].dropna().copy()
    etf_df['Date'] = pd.to_datetime(etf_df['Date'])
    etf_df.set_index('Date', inplace=True)
    etf_df.sort_index(inplace=True)

    monthly_peaks = []

    last_month = etf_df.index.max().replace(day=1) + pd.DateOffset(months=1)
    months = pd.date_range(start=etf_df.index.min().replace(day=1), end=last_month, freq='MS')

    for month_start in months:
        month_end = month_start + pd.offsets.MonthEnd(0)

        # Include up to 10 trading days before this month to capture prior-month lows
        prior_days = etf_df[(etf_df.index < month_start)].tail(10)
        this_month = etf_df[(etf_df.index >= month_start) & (etf_df.index <= month_end)]
        group = pd.concat([prior_days, this_month]).sort_index()

        if group.empty:
            if debug:
                print(f"[SKIP] {etf_name} — No price data for {month_start.strftime('%Y-%m')}")
            continue

        # USFR-specific window: only days 18–25
        if etf_name == 'USFR':
            peak_candidates = group[
                (group.index.day >= 18) &
                (group.index.day <= 25) &
                (group.index.month == month_start.month) &
                (group.index.year == month_start.year)
            ]
        else:
            peak_candidates = this_month  # full month for others

        if peak_candidates.empty:
            if debug:
                print(f"[SKIP] {etf_name} — No peak window data in {month_start.strftime('%Y-%m')}")
            continue

        peak_value = peak_candidates[etf_name].max()
        peak_dates = peak_candidates[peak_candidates[etf_name] == peak_value].index
        peak_date = peak_dates[-1] if len(peak_dates) > 0 else None

        if not peak_date:
            if debug:
                print(f"[SKIP] {etf_name} — No valid peak found in {month_start.strftime('%Y-%m')}")
            continue

        # Get last 10 trading days before the peak
        pre_peak = etf_df[etf_df.index < peak_date]
        if pre_peak.empty:
            if debug:
                print(f"[SKIP] {etf_name} — No data before peak {peak_date}")
            continue

        pre_10d = pre_peak.tail(10)
        if len(pre_10d) < 5:
            if debug:
                print(f"[SKIP] {etf_name} — Too few pre-peak days ({len(pre_10d)}) before {peak_date}")
            continue

        low_value = pre_10d[etf_name].min()
        low_date = pre_10d[etf_name].idxmin()

        if low_date >= peak_date:
            if debug:
                print(f"[SKIP] {etf_name} — Low date {low_date.date()} not before peak {peak_date.date()}")
            continue

        rebound_pct = (peak_value - low_value) / low_value
        reb_thresh = REB_THRESHOLDS.get(etf_name, 0.00075)

        if rebound_pct < reb_thresh:
            if debug:
                print(f"[SKIP] {etf_name} — Rebound too small ({rebound_pct:.3%}) [thresh: {reb_thresh:.3%}] in {month_start.strftime('%Y-%m')}")
            continue

        multi_peak_count = group[etf_name].eq(peak_value).sum()

        monthly_peaks.append({
            'ETF': etf_name,
            'Month': month_start.strftime('%Y-%m'),
            'Low_Date': low_date.strftime('%Y-%m-%d'),
            'Low': round(low_value, 4),
            'Peak_Date': peak_date.strftime('%Y-%m-%d'),
            'Peak': round(peak_value, 4),
            'Rebound_%': round(rebound_pct * 100, 3),
            'Days_Between_Low_and_Peak': (peak_date - low_date).days,
            'Multi_Peak_Days': multi_peak_count,
            'Is_Multi_Day_Peak': multi_peak_count > 1,
            '10D_Low_Before_Peak': round(low_value, 4),
            'Was_Peak_in_Prior_Month': low_date.month != peak_date.month
        })

    return pd.DataFrame(monthly_peaks) if monthly_peaks else pd.DataFrame(columns=[
        'ETF', 'Month', 'Low_Date', 'Low', 'Peak_Date', 'Peak',
        'Rebound_%', 'Days_Between_Low_and_Peak', 'Multi_Peak_Days',
        'Is_Multi_Day_Peak', '10D_Low_Before_Peak', 'Was_Peak_in_Prior_Month'
    ])
