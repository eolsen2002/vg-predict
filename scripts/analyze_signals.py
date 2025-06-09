# scripts/analyze_signals.py
# ✅ Unified logic for checking low or peak signal for an ETF

import pandas as pd
import os
from datetime import datetime

def check_etf_signal(etf: str, signal_type: str, signal_dir="signals") -> str:
    """
    Checks if today is a low or peak signal day for a given ETF.

    Args:
        etf (str): Ticker symbol like 'USFR'
        signal_type (str): Either 'Low' or 'Peak'
        signal_dir (str): Directory where signal CSVs live

    Returns:
        str: Summary of the signal status
    """
    etf = etf.upper()
    signal_type = signal_type.capitalize()
    today = pd.Timestamp.today().normalize()

    if signal_type not in ["Low", "Peak"]:
        return f"❌ Invalid signal type '{signal_type}' for {etf}."

    
    # Build filename and columns
    filename = os.path.join(signal_dir, f"{etf.lower()}_post_peak_{'lows' if signal_type == 'Low' else 'highs'}.csv")
    date_col = f"{etf}_{signal_type}_Date"
    price_col = f"{etf}_{signal_type}"

    if not os.path.exists(filename):
        return f"❌ No {signal_type} signal CSV found for {etf}."

    try:
        df = pd.read_csv(filename, parse_dates=[date_col])
    except Exception as e:
        return f"⚠️ Error reading {filename}: {e}"

    if df.empty:
        return f"⚠️ {signal_type} CSV for {etf} is empty."

    latest = df.iloc[-1]
    signal_date = latest[date_col].normalize()
    signal_price = latest[price_col]

    if signal_date == today:
        return (
            f"🔔 {etf} {signal_type.upper()} SIGNAL ACTIVE\n"
            f"• Date: {signal_date.date()} at ${signal_price:.2f}"
        )
    else:
        return (
            f"📄 Latest {etf} {signal_type.lower()} date: {signal_date.date()}, value: ${signal_price:.2f}\n"
            f"📉 Today is NOT a {signal_type.lower()} signal day for {etf}."
        )
