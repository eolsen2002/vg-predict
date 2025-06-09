# scripts/is_today_usfr_low.py

import pandas as pd
from datetime import datetime
import os

print("🚀 Script started")
print("📆 Today is:", datetime.today().date())

def check_usfr_low():
    df = pd.read_csv("signals/usfr_post_peak_lows.csv", parse_dates=['USFR_Peak_Date', 'USFR_Low_Date'])

    latest = df.iloc[-1]
    print(f"📄 Latest USFR low date in CSV: {latest['USFR_Low_Date'].date()}, value: ${latest['USFR_Low']:.2f}")

    today = pd.Timestamp(datetime.today().date())

    row = df[df['USFR_Low_Date'] == today]
    if not row.empty:
        r = row.iloc[0]
        return (
            f"📅 Today IS the USFR low day!\n"
            f"• Peak Date: {r['USFR_Peak_Date'].strftime('%Y-%m-%d')} at ${r['USFR_Peak']:.2f}\n"
            f"• Projected Low Date: {r['USFR_Low_Date'].strftime('%Y-%m-%d')} at ${r['USFR_Low']:.2f}\n"
            f"• Drop: {r['Drop_%']:.3f}%\n"
            f"• Today: {today.strftime('%Y-%m-%d')}\n"
        )
    else:
        future_lows = df[df['USFR_Low_Date'] > today]
        if not future_lows.empty:
            next_low = future_lows.iloc[0]
            days_until = (next_low['USFR_Low_Date'] - today).days
            return (
                f"📅 Today is NOT the USFR low day.\n"
                f"• Peak Date: {next_low['USFR_Peak_Date'].strftime('%Y-%m-%d')} at ${next_low['USFR_Peak']:.2f}\n"
                f"• Projected Low Date: {next_low['USFR_Low_Date'].strftime('%Y-%m-%d')} at ${next_low['USFR_Low']:.2f}\n"
                f"• Drop: {next_low['Drop_%']:.3f}%\n"
                f"• Today: {today.strftime('%Y-%m-%d')} — {days_until} day(s) from low\n"
            )
        else:
            return "No upcoming USFR low dates found in data."

if __name__ == "__main__":
    summary = check_usfr_low()
    print(summary)

    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)

    # Write the summary to a daily log file (overwrite mode)
    log_filename = f"reports/usfr_report_{datetime.now().strftime('%Y-%m-%d')}.txt"
    with open(log_filename, "w") as f:
        f.write(summary)
