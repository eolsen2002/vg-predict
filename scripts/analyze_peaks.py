# scripts/analyze_peaks.py

import pandas as pd
from datetime import datetime
import os


def check_peak(etf: str):
    today = pd.Timestamp(datetime.today().date())
    filename = f"signals/{etf.lower()}_post_peak_highs.csv"
    
    try:
        df = pd.read_csv(filename, parse_dates=[f"{etf}_Peak_Date"])
    except FileNotFoundError:
        return f"❌ No peak CSV found for {etf}."

    latest = df.iloc[-1]
    peak_date = latest[f"{etf}_Peak_Date"]
    peak_price = latest[f"{etf}_Peak"]
    
    print(f"📄 Latest {etf} peak date in CSV: {peak_date.date()}, value: ${peak_price:.2f}")

    if peak_date == today:
        return (
            f"📈 Today IS the {etf} PEAK day!\n"
            f"• Peak Date: {peak_date.date()} at ${peak_price:.2f}\n"
            f"• Today: {today.date()}\n"
            f"🔔 {etf} PEAK SIGNAL ACTIVE"
        )
    else:
        return f"📉 Today is NOT a {etf} peak day."


def check_etf_peak_signal(etf: str, signal_dir: str = "signals", price_csv: str = "data/etf_prices_2023_2025.csv") -> str:
    """
    Checks if today matches the most recent post-low peak signal for the given ETF.
    """
    peak_csv_path = os.path.join(signal_dir, f"{etf.lower()}_post_peak_highs.csv")

    if not os.path.exists(peak_csv_path):
        return f"❌ No peak CSV found for {etf.upper()}."

    # Load signal file
    try:
        df = pd.read_csv(peak_csv_path, parse_dates=[f"{etf.upper()}_Low_Date", f"{etf.upper()}_Peak_Date"])
    except Exception as e:
        return f"⚠️ Error reading {peak_csv_path}: {e}"

    if df.empty:
        return f"⚠️ Peak CSV for {etf.upper()} is empty."

    # Get most recent peak signal
    latest_row = df.iloc[-1]
    peak_date = latest_row[f"{etf.upper()}_Peak_Date"]
    peak_price = latest_row[f"{etf.upper()}_Peak"]

    today = pd.Timestamp.today().normalize()

    # Check if today matches the peak date
    if peak_date.normalize() == today:
        return (
            f"🔔 {etf.upper()} PEAK SIGNAL ACTIVE\n"
            f"• Low Date: {latest_row[f'{etf.upper()}_Low_Date'].date()} at ${latest_row[f'{etf.upper()}_Low']:.2f}\n"
            f"• Projected Peak Date: {peak_date.date()} at ${peak_price:.2f}\n"
            f"• Rebound: {((peak_price - latest_row[f'{etf.upper()}_Low']) / latest_row[f'{etf.upper()}_Low']) * 100:.3f}%"
        )
    else:
        return f"Today is NOT a {etf.upper()} peak day."
