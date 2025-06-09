# scripts/analyze_lows.py

import pandas as pd
from datetime import datetime

def check_low(etf: str):
    today = pd.Timestamp(datetime.today().date())
    filename = f"signals/{etf.lower()}_post_peak_lows.csv"

    try:
        df = pd.read_csv(filename, parse_dates=[f"{etf}_Low_Date", f"{etf}_Peak_Date"])
    except FileNotFoundError:
        return f"❌ No low CSV found for {etf}."

    latest = df.iloc[-1]
    low_date = latest[f"{etf}_Low_Date"]
    low_price = latest[f"{etf}_Low"]
    peak_date = latest[f"{etf}_Peak_Date"]
    peak_price = latest[f"{etf}_Peak"]
    drop_pct = latest["Drop_%"]

    print(f"📄 Latest {etf} low date in CSV: {low_date.date()}, value: ${low_price:.2f}")

    if low_date == today:
        return (
            f"📅 Today IS the {etf} LOW day!\n"
            f"• Peak Date: {peak_date.date()} at ${peak_price:.2f}\n"
            f"• Projected Low Date: {low_date.date()} at ${low_price:.2f}\n"
            f"• Drop: {drop_pct:.3f}%\n"
            f"• Today: {today.date()}\n"
            f"🔔 {etf} LOW SIGNAL ACTIVE"
        )
    else:
        return f"📈 Today is NOT a {etf} low day."

def check_etf_low_signal(etf_name: str) -> str:
    """
    Checks if today is the post-peak low date for a given ETF.

    Parameters:
        etf_name (str): ETF symbol, e.g., "USFR", "SGOV", etc.

    Returns:
        str: Human-readable result.
    """
    today = pd.Timestamp.today().normalize()
    file_path = f"signals/{etf_name.lower()}_post_peak_lows.csv"

    try:
        df = pd.read_csv(file_path, parse_dates=[f"{etf_name}_Peak_Date", f"{etf_name}_Low_Date"])
    except FileNotFoundError:
        return f"❌ No low CSV found for {etf_name}.\n"

    if df.empty:
        return f"⚠️ No data available for {etf_name}.\n"

    latest_row = df.iloc[-1]
    low_date = latest_row[f"{etf_name}_Low_Date"].date()
    low_price = latest_row[f"{etf_name}_Low"]
    peak_date = latest_row[f"{etf_name}_Peak_Date"].date()
    peak_price = latest_row[f"{etf_name}_Peak"]

    result = (
        f"📄 Latest {etf_name} low date: {low_date}, value: ${low_price:.2f}\n"
        f"📅 Peak Date: {peak_date} at ${peak_price:.2f}\n"
        f"📉 Drop: {100 * (peak_price - low_price) / peak_price:.3f}%\n"
    )

    if today.date() == low_date:
        result += f"🔔 {etf_name} LOW SIGNAL ACTIVE (Today = Low)\n"
    else:
        result += f"📉 Today is NOT a low signal day for {etf_name}.\n"

    return result