# scripts/analyze_lows.py
import pandas as pd
from datetime import datetime, timedelta
import os

def check_low(etf: str, signal_csv: str = "signals/all_etfs_post_peak_lows.csv") -> str:
    today = pd.Timestamp(datetime.today().date())

    if not os.path.exists(signal_csv):
        return f"❌ No combined low CSV found at {signal_csv}."

    try:
        df = pd.read_csv(signal_csv)
    except Exception as e:
        return f"⚠️ Error reading {signal_csv}: {e}"

    # Filter rows for the requested ETF (case-insensitive)
    df_etf = df[df["ETF"].str.upper() == etf.upper()]

    if df_etf.empty:
        return f"❌ No low data found for {etf.upper()}."

    # Convert Low_Date to datetime
    df_etf['Low_Date'] = pd.to_datetime(df_etf['Low_Date'])

    # Get most recent low signal for this ETF
    latest_row = df_etf.iloc[-1]
    low_date = latest_row["Low_Date"]
    low_price = latest_row["Low"]

    output = f"📄 Latest {etf.upper()} low date in CSV: {low_date.date()}, value: ${low_price:.2f}\n"

    if low_date.normalize() == today:
        output += f"🔔 {etf.upper()} LOW SIGNAL ACTIVE\n• Low Date: {low_date.date()} at ${low_price:.2f}"
    else:
        output += f"📉 Today is NOT a {etf.upper()} low day."

    # Check for upcoming lows within the next 3 days
    upcoming = df_etf[(df_etf['Low_Date'] > today) & (df_etf['Low_Date'] <= today + timedelta(days=3))]
    if not upcoming.empty:
        output += "\n\n⏳ Upcoming low dates within 3 days:\n"
        for _, row in upcoming.iterrows():
            output += f"• {row['Low_Date'].date()} at ${row['Low']:.2f}\n"

    return output.strip()

# Example usage:
if __name__ == "__main__":
    import sys
    etf_name = sys.argv[1] if len(sys.argv) > 1 else "USFR"
    print(check_low(etf_name))
