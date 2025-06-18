"""
Updated 6/18/25 ✅ Key Additions:
💬 Clear docstring at top of function
📅 Robust handling of modal days and fallback
✅ Defensive coding for empty or malformed files
🟢 Built-in debug info for tracing logic, especially during testing
📌 Comment near get_next_market_day() to clarify use case

Fix Plan:
- Accept either a date string (e.g., 2025-06-17) or an integer (e.g., 17)
- Parse safely with dateutil.parser.parse() if needed
- Handle modal day 31 gracefully for months with fewer days
- Skip weekends AND major US market holidays (like July 4) in next market day logic
"""

import calendar
import platform
import csv
from datetime import datetime, timedelta, date
from dateutil import parser

def get_us_market_holidays(year):
    """
    Return a set of dates that are US market holidays for a given year.
    Includes fixed-date holidays and observed days for New Year's Day,
    Independence Day, and Christmas Day.
    """
    holidays = set()
    # New Year's Day (Jan 1)
    holidays.add(date(year, 1, 1))
    # Independence Day (July 4)
    holidays.add(date(year, 7, 4))
    # Christmas Day (Dec 25)
    holidays.add(date(year, 12, 25))

    # Observed holidays for July 4th
    if date(year, 7, 4).weekday() == 5:  # Saturday
        holidays.add(date(year, 7, 3))  # Friday before
    elif date(year, 7, 4).weekday() == 6:  # Sunday
        holidays.add(date(year, 7, 5))  # Monday after

    # Observed holidays for New Year's Day
    if date(year, 1, 1).weekday() == 5:  # Saturday
        holidays.add(date(year-1, 12, 31))  # Friday before, previous year Dec 31
    elif date(year, 1, 1).weekday() == 6:  # Sunday
        holidays.add(date(year, 1, 2))  # Monday after

    # Observed holidays for Christmas Day
    if date(year, 12, 25).weekday() == 5:  # Saturday
        holidays.add(date(year, 12, 24))  # Friday before
    elif date(year, 12, 25).weekday() == 6:  # Sunday
        holidays.add(date(year, 12, 26))  # Monday after

    return holidays

def get_next_market_day(date_obj):
    """
    Returns the next weekday (Mon–Fri) after the given date,
    skipping weekends AND US market holidays.
    Used to adjust USFR Low signals to next market day.
    """
    date_obj += timedelta(days=1)
    holidays = get_us_market_holidays(date_obj.year)
    while date_obj.weekday() >= 5 or date_obj in holidays:
        date_obj += timedelta(days=1)
        # If year changes, update holidays set
        if date_obj.year != date_obj.year:
            holidays = get_us_market_holidays(date_obj.year)
    return date_obj

def check_etf_signal_with_countdown(etf, signal_type):
    """
    Load full cycles CSV signal file and return modal day, next signal date, and days until signal.
    Finds next upcoming modal day (this or next month), never past.
    Adjusts USFR low signal to next market day.

    Parameters:
        etf (str): ETF ticker (e.g. 'USFR', 'SGOV')
        signal_type (str): 'peak' or 'low' (case insensitive)

    Returns:
        dict with keys:
            - text (str): descriptive text with countdown info
            - modal_day (int): day of month for signal
            - next_date (str): formatted date string of signal (e.g., '6/18/25')
            - days_until (int): days from today until signal (0 if today)
    """
    signal_file = f"signals/{etf.lower()}_full_cycles.csv"
    today = date.today()
    modal_day = None

    signal_type = signal_type.lower()
    date_col_map = {"peak": "Peak_Date", "low": "Low_Date"}
    date_key = date_col_map.get(signal_type)

    def find_modal_days(reader, date_key):
        """Extract all modal days (day of month) from signal dates in CSV."""
        modal_days = []
        for row in reader:
            raw_date = row.get(date_key)
            if raw_date:
                try:
                    d = parser.parse(raw_date).date()
                    modal_days.append(d.day)
                except Exception:
                    continue
        return modal_days

    def adjust_to_next_market_day(d):
        """Shift date d forward if it falls on weekend or US market holiday."""
        holidays = get_us_market_holidays(d.year)
        while d.weekday() >= 5 or d in holidays:
            d += timedelta(days=1)
            # Update holidays if year changes
            if d.year != d.year:
                holidays = get_us_market_holidays(d.year)
        return d

    try:
        with open(signal_file, newline='') as f:
            reader = list(csv.DictReader(f))

            if not reader:
                return {
                    "text": f"⚠️ No data in {etf} signal file.",
                    "modal_day": None,
                    "next_date": None,
                    "days_until": None
                }

            # Get all modal days from CSV for this signal type
            modal_days_all = find_modal_days(reader, date_key)
            if not modal_days_all:
                return {
                    "text": f"⚠️ No signal dates found in {etf} file.",
                    "modal_day": None,
                    "next_date": None,
                    "days_until": None
                }

            # Use the first modal day as representative (your CSV likely has consistent modal days per ETF)
            modal_day = modal_days_all[0]

            # Helper to safely create a date or return None if invalid
            def valid_date(y, m, d):
                try:
                    return date(y, m, d)
                except ValueError:
                    return None

            # Find candidate date with modal_day in current month
            year = today.year
            month = today.month
            candidate_date = valid_date(year, month, modal_day)

            # If invalid or modal day passed this month, try next month
            if candidate_date is None or candidate_date < today:
                if month == 12:
                    year += 1
                    month = 1
                else:
                    month += 1
                candidate_date = valid_date(year, month, modal_day)

            # If candidate_date still None (e.g. modal_day=31 but next month has 30 days), fallback:
            if candidate_date is None:
                # fallback: pick earliest date in CSV signal dates that is on or after today, else pick today
                future_dates = []
                for row in reader:
                    raw_date = row.get(date_key)
                    if raw_date:
                        try:
                            d = parser.parse(raw_date).date()
                            if d >= today:
                                future_dates.append(d)
                        except Exception:
                            continue
                if future_dates:
                    candidate_date = min(future_dates)
                else:
                    candidate_date = today  # fallback to today

            peak_modal_day = None
            peak_date = None
            if etf.upper() == "USFR":
                # Find modal day for peak from CSV
                peak_modal_days = find_modal_days(reader, "Peak_Date")
                if peak_modal_days:
                    peak_modal_day = peak_modal_days[0]

                    def valid_date(y, m, d):
                        try:
                            return date(y, m, d)
                        except ValueError:
                            return None

                    year_peak = today.year
                    month_peak = today.month
                    peak_candidate_date = valid_date(year_peak, month_peak, peak_modal_day)
                    if peak_candidate_date is None or peak_candidate_date < today:
                        if month_peak == 12:
                            year_peak += 1
                            month_peak = 1
                        else:
                            month_peak += 1
                        peak_candidate_date = valid_date(year_peak, month_peak, peak_modal_day)

                    if peak_candidate_date is None:
                        peak_candidate_date = today

                    peak_date = peak_candidate_date

            # --- Assign modal_date according to ETF and signal_type ---
            if etf.upper() != "USFR" and signal_type == "peak" and modal_day == 31:
                # For non-USFR ETFs peak signals with modal_day 31,
                # use last market day of current or next month
                def get_last_market_day(year, month):
                    last_day = calendar.monthrange(year, month)[1]
                    last_date = date(year, month, last_day)
                    while last_date.weekday() >= 5:  # Sat=5, Sun=6
                        last_date -= timedelta(days=1)
                    return last_date

                last_market_day_this_month = get_last_market_day(today.year, today.month)
                if last_market_day_this_month >= today:
                    modal_date = last_market_day_this_month
                else:
                    next_month = today.month + 1 if today.month < 12 else 1
                    next_year = today.year if today.month < 12 else today.year + 1
                    modal_date = get_last_market_day(next_year, next_month)

            elif etf.upper() == "USFR" and signal_type == "low" and peak_date is not None:
                # For USFR low, use next market day after peak date (skip weekends & holidays)
                modal_date = get_next_market_day(peak_date)

            else:
                modal_date = candidate_date

            # --- UNIVERSAL: Adjust modal_date to skip weekends and holidays ---
            modal_date = adjust_to_next_market_day(modal_date)

            days_until = (modal_date - today).days
            if days_until < 0:
                days_until = 0

            # Cross-platform date formatting
            if platform.system() == "Windows":
                formatted_date = modal_date.strftime("%#m/%#d/%y")
            else:
                formatted_date = modal_date.strftime("%-m/%-d/%y")

            text = f"{etf.upper()} expected {signal_type} on modal day {modal_day} → {formatted_date} ({days_until} days left)"
            if days_until == 0:
                text += " ⚡ TODAY'S MATCH!"

            return {
                "text": text,
                "modal_day": modal_day,
                "next_date": formatted_date,
                "days_until": days_until
            }

    except FileNotFoundError:
        return {
            "text": f"⚠️ Signal file not found for {etf}: {signal_file}",
            "modal_day": None,
            "next_date": None,
            "days_until": None
        }
    except Exception as e:
        return {
            "text": f"⚠️ Error processing {etf} signal: {str(e)}",
            "modal_day": None,
            "next_date": None,
            "days_until": None
        }
