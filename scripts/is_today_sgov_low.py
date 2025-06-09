# scripts/is_today_sgov_low.py

import pandas as pd
from datetime import datetime
import os

print("🚀 SGOV script started")
print("📆 Today is:", datetime.today().date())

def check_sgov_low():
    df = pd.read_csv("signals/sgov_post_peak_lows.csv", parse_dates=['SGOV_Peak_Date', 'SGOV_Low_Date'])

    latest = df.iloc[-1]
    print(f"📄 Latest SGOV low date in CSV: {latest['SGOV_Low_Date'].date()}, value: ${latest['SGOV_Low']:.2f}")

    today = pd.Timestamp(datetime.today().date())
    row = df[df['SGOV_Low_Date'] == today]

    if not row.empty:
        r = row.iloc[0]
        print("📅 Today IS the SGOV low day!")
        print(f"• Peak Date: {r['SGOV_Peak_Date'].strftime('%Y-%m-%d')} at ${r['SGOV_Peak']:.2f}")
        print(f"• Projected Low Date: {r['SGOV_Low_Date'].strftime('%Y-%m-%d')} at ${r['SGOV_Low']:.2f}")
        print(f"• Drop: {r['Drop_%']:.3f}%")
        print(f"• Today: {today.date()}")
        return "🔔 SGOV LOW SIGNAL ACTIVE"
    else:
        print("📉 Today is NOT a SGOV low day.")
        return "No SGOV signal today."
