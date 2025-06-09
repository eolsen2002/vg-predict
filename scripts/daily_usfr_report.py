"""
Step 1: Create a daily-run script that:
Runs the is_today_usfr_low.py logic

Prints or saves the output summary

Optionally emails or logs the report somewhere

Step 2: Use a scheduler to run the script daily
Windows: Use Task Scheduler

Linux/Mac: Use cron
"""

import datetime
from scripts import is_today_usfr_low  # assuming is_today_usfr_low is a function, else adapt

# If is_today_usfr_low.py is a standalone script, refactor it to a function like this:
# def check_usfr_low():
#    ... your existing code ...
#    return summary_string

# For demo, I’ll simulate calling that function here
def check_usfr_low():
    # Paste your logic from is_today_usfr_low.py here inside a function
    # Return the summary string instead of print
    import pandas as pd
    
    df = pd.read_csv("signals/usfr_post_peak_lows.csv", parse_dates=['USFR_Peak_Date', 'USFR_Low_Date'])
    
    today = pd.Timestamp(datetime.datetime.now().date())
    
    row = df[df['USFR_Low_Date'] == today]
    if not row.empty:
        r = row.iloc[0]
        summary = (
            f"📅 Today IS the USFR low day!\n"
            f"• Peak Date: {r['USFR_Peak_Date'].strftime('%Y-%m-%d')} at ${r['USFR_Peak']:.2f}\n"
            f"• Projected Low Date: {r['USFR_Low_Date'].strftime('%Y-%m-%d')} at ${r['USFR_Low']:.2f}\n"
            f"• Drop: {r['Drop_%']:.3f}%\n"
            f"• Today: {today.strftime('%Y-%m-%d')}\n"
        )
    else:
        # Find closest low date
        future_lows = df[df['USFR_Low_Date'] > today]
        if not future_lows.empty:
            next_low = future_lows.iloc[0]
            days_until = (next_low['USFR_Low_Date'] - today).days
            summary = (
                f"📅 Today is NOT the USFR low day.\n"
                f"• Peak Date: {next_low['USFR_Peak_Date'].strftime('%Y-%m-%d')} at ${next_low['USFR_Peak']:.2f}\n"
                f"• Projected Low Date: {next_low['USFR_Low_Date'].strftime('%Y-%m-%d')} at ${next_low['USFR_Low']:.2f}\n"
                f"• Drop: {next_low['Drop_%']:.3f}%\n"
                f"• Today: {today.strftime('%Y-%m-%d')} — {days_until} day(s) from low\n"
            )
        else:
            summary = "No upcoming USFR low dates found in data."
    return summary


if __name__ == "__main__":
    report = check_usfr_low()
    print(report)
    
    # Save to a daily log file
    log_filename = f"reports/usfr_report_{datetime.datetime.now().strftime('%Y-%m-%d')}.txt"
    with open(log_filename, "w") as f:
        f.write(report)
