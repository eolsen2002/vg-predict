# analyze_signals.py
# ✅ Unified logic for checking low or peak signal for an ETF with countdown to next signal

import pandas as pd
import os
from datetime import date, timedelta
import numpy as np


def check_etf_signal_with_countdown(etf: str, signal_type: str, signal_dir="signals") -> dict:
    """
    Checks if today is a low or peak signal day for a given ETF and computes days until next signal.

    Args:
        etf (str): Ticker symbol like 'USFR'
        signal_type (str): Either 'Low' or 'Peak'
        signal_dir (str): Directory where signal CSVs live

    Returns:
        dict: Contains 'text' and 'days_until' keys
    """
    etf = etf.upper()
    signal_type = signal_type.capitalize()
    today = pd.Timestamp.today().normalize()

    if signal_type not in ["Low", "Peak"]:
        return {"text": f"❌ Invalid signal type '{signal_type}' for {etf}.", "days_until": -1}

    # Build filename and columns
    filename = os.path.join(signal_dir, f"{etf.lower()}_post_peak_{'lows' if signal_type == 'Low' else 'highs'}.csv")
    date_col = f"{etf}_{signal_type}_Date"
    price_col = f"{etf}_{signal_type}"

    if not os.path.exists(filename):
        return {"text": f"❌ No {signal_type} signal CSV found for {etf}.", "days_until": -1}

    try:
        df = pd.read_csv(filename, parse_dates=[date_col])
    except Exception as e:
        return {"text": f"⚠️ Error reading {filename}: {e}", "days_until": -1}

    if df.empty:
        return {"text": f"⚠️ {signal_type} CSV for {etf} is empty.", "days_until": -1}

    # Find the next signal date that is today or later
    future_signals = df[df[date_col] >= today]
    if not future_signals.empty:
        next_signal = future_signals.iloc[0]
        signal_date = next_signal[date_col].normalize()
        signal_price = next_signal[price_col]
        days_until = (signal_date - today).days
        if signal_date == today:
            text = (
                f"🔔 {etf} {signal_type.upper()} SIGNAL ACTIVE\n"
                f"• Date: {signal_date.date()} at ${signal_price:.2f}"
            )
        else:
            text = (
                f"📅 Upcoming {etf} {signal_type.lower()} date: {signal_date.date()}, value: ${signal_price:.2f}\n"
                f"📉 {days_until} days until next {signal_type.lower()} signal."
            )
    else:
        # No future signals; estimate next based on historical pattern
        df = df.sort_values(by=date_col)
        last_signal = df.iloc[-1]
        signal_price = last_signal[price_col]

        # Use modal day of month from historical signals
        day_series = df[date_col].dt.day
        most_common_day = int(day_series.mode().iloc[0]) if not day_series.empty else 22

        # Start from today and loop to find nearest valid date in this or next month
        month_offset = 0
        while month_offset < 2:
            check_date = today + pd.DateOffset(months=month_offset)
            try:
                candidate_date = pd.Timestamp(year=check_date.year, month=check_date.month, day=most_common_day)
                if candidate_date >= today:
                    break
            except:
                pass
            month_offset += 1
        else:
            candidate_date = today + timedelta(days=10)

        # Adjust for weekends: shift to next Monday if Sat/Sun
        if candidate_date.weekday() == 5:
            candidate_date += timedelta(days=2)
        elif candidate_date.weekday() == 6:
            candidate_date += timedelta(days=1)

        days_until = (candidate_date - today).days
        if candidate_date != today:
            days_until += 1

        text = (
            f"📄 Latest {etf} {signal_type.lower()} date: {last_signal[date_col].date()}, value: ${signal_price:.2f}\n"
            f"🧠 Estimated next {signal_type.lower()} (modal day {most_common_day}): {candidate_date.date()}\n"
            f"⏳ {days_until} days until likely {signal_type.lower()}"
        )

    return {"text": text, "days_until": days_until}
