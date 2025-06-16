# scripts/analyze_signals.py
from datetime import datetime, timedelta
import csv
from dateutil import parser

def get_next_market_day(start_date):
    """Returns the next weekday (Mon–Fri) after the given date."""
    date = start_date + timedelta(days=1)
    while date.weekday() >= 5:  # 5=Saturday, 6=Sunday
        date += timedelta(days=1)
    return date

def check_etf_signal_with_countdown(etf, signal_type):
    signal_file = f"signals/{etf.lower()}_full_cycles.csv"
    today = datetime.today().date()
    modal_day = None
    next_date = None
    lines = []

    try:
        with open(signal_file, newline='') as f:
            reader = list(csv.DictReader(f))

            print(f"[DEBUG] Columns found in {etf} signal file:", reader[0].keys())
            print(f"[DEBUG] First 3 rows:")
            for r in reader[:3]:
                print(r)
            
            # Detect month column dynamically:
            possible_month_cols = ["Cycle_Month", "Cycle_Start_Month", "Month"]
            month_col = next((col for col in possible_month_cols if col in reader[0]), None)
            print(f"[DEBUG] Using month_col: {month_col}")

            if not month_col:
                return {
                    "text": f"Month column not found in {etf} signal file.",
                    "modal_day": None,
                    "next_date": None,
                    "days_until": None
                }

            current_month = today.strftime("%Y-%m")
            print(f"[DEBUG] current_month: {current_month}")

            current_rows = [r for r in reader if r[month_col].startswith(current_month)]
            print(f"[DEBUG] Number of rows matching current month: {len(current_rows)}")

            # Try to detect the correct month column name
            possible_month_cols = ["Cycle_Month", "Cycle_Start_Month", "Month"]
            month_col = next((col for col in possible_month_cols if col in reader[0]), None)

            if not month_col:
                return {
                    "text": f"Month column not found in {etf} signal file.",
                    "modal_day": None,
                    "next_date": None,
                    "days_until": None
                }

            current_rows = [r for r in reader if r[month_col].startswith(current_month)]

            if not current_rows:
                return {
                    "text": f"No signal data found for {etf} in {current_month}.",
                    "modal_day": None,
                    "next_date": None,
                    "days_until": None
                }

            row = current_rows[0]

            try:
                modal_day = int(row[f"{signal_type}_Modal_Day"])
                modal_date = datetime(today.year, today.month, modal_day).date()

                # Special rule for USFR Low: one market day after Peak
                if etf.upper() == "USFR" and signal_type == "Low":
                    modal_date = get_next_market_day(modal_date)

                next_date = modal_date.strftime("%-m/%-d/%y")
                days_until = max((modal_date - today).days, 0)

                lines.append(f"{etf} expected {signal_type.lower()} around modal day {modal_day}.")
                lines.append(f"    Likely next {signal_type.lower()} on {next_date}")
                lines.append(f"    {days_until} days until likely {signal_type.lower()}")

                # ✅ Add this debug line before return
                print(f"[DEBUG] {etf} {signal_type} → modal_day: {modal_day}, next_date: {next_date}, days_until: {days_until}")

                return {
                    "text": "\n".join(lines),
                    "modal_day": modal_day,
                    "next_date": next_date,
                    "days_until": days_until
                }

            except Exception as parse_err:
                return {
                    "text": f"Could not parse modal date for {etf}: {parse_err}",
                    "modal_day": None,
                    "next_date": None,
                    "days_until": None
                }

    except Exception as e:
        return {
            "text": f"Error reading signal file for {etf}: {e}",
            "modal_day": None,
            "next_date": None,
            "days_until": None
        }
