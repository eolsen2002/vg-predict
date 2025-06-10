"""
scripts/analyze_peaks.py

Purpose:
--------
Check if today matches the latest monthly peak date for a specified Treasury ETF.

Functionality:
--------------
- Reads combined peak data from 'signals/all_etfs_peaks.csv'.
- Filters data for the given ETF symbol (case-insensitive).
- Compares the latest recorded peak date with today's date.
- Returns or prints a message indicating whether today is the ETF's peak day.

Inputs:
--------
- ETF symbol passed as a command-line argument (e.g., USFR, SGOV).

Outputs:
---------
- Prints peak date and value for the ETF.
- Indicates if today is the ETF's peak day.
- Error messages if CSV is missing or data is invalid.

Usage:
--------
Run from command line:
    python analyze_peaks.py USFR
"""

import pandas as pd
from datetime import datetime
import os
import sys

def check_peak(etf: str):
    today = pd.Timestamp(datetime.today().date())
    filename = "signals/all_etfs_peaks.csv"
    
    if not os.path.exists(filename):
        return f"❌ No combined peak CSV found at {filename}"

    try:
        df = pd.read_csv(filename)
    except Exception as e:
        return f"⚠️ Error reading {filename}: {e}"

    # Filter for this ETF only, use .copy() to avoid SettingWithCopyWarning
    df_etf = df[df['ETF'].str.upper() == etf.upper()].copy()
    if df_etf.empty:
        return f"⚠️ No peak data found for {etf.upper()} in combined CSV."

    # Convert 'Peak_Date' column *after* filtering
    try:
        df_etf['Peak_Date'] = pd.to_datetime(df_etf['Peak_Date'])
    except Exception as e:
        return f"⚠️ Date conversion failed: {e}"

    # Get latest peak row
    latest = df_etf.iloc[-1]
    peak_date = latest["Peak_Date"]
    peak_price = latest["Peak"]

    print(f"📄 Latest {etf.upper()} peak date in CSV: {peak_date.date()}, value: ${peak_price:.2f}")

    if peak_date.normalize() == today:
        return (
            f"📈 Today IS the {etf.upper()} PEAK day!\n"
            f"• Peak Date: {peak_date.date()} at ${peak_price:.2f}\n"
            f"• Today: {today.date()}\n"
            f"🔔 {etf.upper()} PEAK SIGNAL ACTIVE"
        )
    else:
        return f"📉 Today is NOT a {etf.upper()} peak day."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_peaks.py ETF_SYMBOL")
        sys.exit(1)
    
    etf = sys.argv[1]
    result = check_peak(etf)
    print(result)
