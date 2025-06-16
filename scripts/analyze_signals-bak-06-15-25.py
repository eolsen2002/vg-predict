# scripts/analyze_signals.py
"""
✅ Enhanced unified logic for detecting low or peak signal dates for Treasury ETFs.

Changes & Additions:
- Supports auto-adjustment for signal days like "31" to the last valid day of month (e.g., Feb 28/29).
- Added modal day logic for estimating next signal when future signals are unavailable.
- Optional future enhancement support for symbolic modal days like "EOM".
- Fully documented with comments and docstrings for clarity and maintainability.

Typical Use:
    check_etf_signal_with_countdown('SGOV', 'Peak') returns a dict with:
        • signal summary text
        • countdown days to next expected signal
"""

import pandas as pd
import os
from datetime import timedelta
import calendar

def get_valid_peak_date(year: int, month: int, day: int) -> pd.Timestamp:
    """
    Given a year, month, and desired day,
    returns a pd.Timestamp with the day adjusted to last valid day of month if necessary.

    Example:
        get_valid_peak_date(2025, 2, 31) -> Timestamp('2025-02-28')
    """
    last_day = calendar.monthrange(year, month)[1]
    valid_day = min(day, last_day)
    return pd.Timestamp(year=year, month=month, day=valid_day)

def check_etf_signal_with_countdown(etf: str, signal_type: str, signal_dir="signals") -> dict:
    """
    Checks if today is a low or peak signal day for a given ETF and computes days until next signal.

    Args:
        etf (str): Ticker symbol like 'USFR', 'SGOV', etc.
        signal_type (str): Either 'Low' or 'Peak'
        signal_dir (str): Directory where signal CSVs live (default = 'signals')

    Returns:
        dict: Contains:
            - 'text': Human-readable status or signal message
            - 'days_until': Integer days until next expected signal or -1 if unknown
    """
    etf = etf.upper()
    signal_type = signal_type.capitalize()
    today = pd.Timestamp.today().normalize()

    if signal_type not in ["Low", "Peak"]:
        return {"text": f"❌ Invalid signal type '{signal_type}' for {etf}.", "days_until": -1}

    # Construct the appropriate filename and column names
    filename = os.path.join(signal_dir, f"{etf.lower()}_post_peak_{'lows' if signal_type == 'Low' else 'highs'}.csv")
    date_col = "Peak_Date" if signal_type == "Peak" else f"{etf}_Low_Date"
    price_col = "Peak" if signal_type == "Peak" else f"{etf}_Low"

    if not os.path.exists(filename):
        return {"text": f"❌ No {signal_type} signal CSV found for {etf}.", "days_until": -1}

    try:
        df = pd.read_csv(filename, parse_dates=[date_col])
    except Exception as e:
        return {"text": f"⚠️ Error reading {filename}: {e}", "days_until": -1}

    if df.empty:
        return {"text": f"⚠️ {signal_type} CSV for {etf} is empty.", "days_until": -1}

    # 1️⃣ Check for future signals ≥ today
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
        # 2️⃣ No future signals: Estimate next likely signal date
        df = df.sort_values(by=date_col)
        last_signal = df.iloc[-1]
        signal_price = last_signal[price_col]

        day_series = df[date_col].dt.day
        most_common_day = int(day_series.mode().iloc[0]) if not day_series.empty else 22

        # Find next valid candidate date in this or next month
        month_offset = 0
        candidate_date = None
        while month_offset < 2:
            check_date = today + pd.DateOffset(months=month_offset)
            candidate_date = get_valid_peak_date(check_date.year, check_date.month, most_common_day)
            if candidate_date >= today:
                break
            month_offset += 1

        if candidate_date is None or candidate_date < today:
            candidate_date = today + timedelta(days=10)

        # Adjust weekends → next Monday
        if candidate_date.weekday() == 5:
            candidate_date += timedelta(days=2)
        elif candidate_date.weekday() == 6:
            candidate_date += timedelta(days=1)

        days_until = (candidate_date - today).days
        if candidate_date != today:
            days_until += 1  # Show full-day wait

        text = (
            f"📄 {etf} {signal_type.lower()} date: {last_signal[date_col].date()}, value: ${signal_price:.2f}\n"
            f"🧠 Estimated next {signal_type.lower()} (modal day {most_common_day}): {candidate_date.date()}\n"
            f"⏳ {days_until} days until likely {signal_type.lower()}"
        )

    return {"text": text, "days_until": days_until}
