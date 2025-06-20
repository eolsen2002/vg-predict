# scripts/split_usfr_highs_lows.py

"""
scripts/split_usfr_highs_lows.py

Purpose:
--------
This script processes the combined USFR post-peak highs and lows data
(from signals/usfr_post_peak_highs.csv) and extracts clean, chronological
lists of valid low and high points as separate CSV files.

Functionality:
--------------
- Reads the combined CSV containing USFR peak and low dates and prices.
- Sorts data by the low dates chronologically.
- Filters to only include valid low→high cycles, ensuring each high date
  is strictly after the previous high to avoid overlaps.
- Saves the filtered peaks and lows into two separate CSV files:
  - signals/usfr_post_peak_highs_only.csv
  - signals/usfr_post_peak_lows_only.csv

This separation helps downstream analysis and signal detection by
providing clean, ordered data for highs and lows individually.

Output:
--------
- Two CSV files containing clean USFR peak and low data respectively.

Usage:
-------
Run as a standalone script after generating or updating
signals/usfr_post_peak_highs.csv to refresh the separate peak and low files.
"""


import pandas as pd
import os

# Load the original file
input_file = "signals/usfr_post_peak_highs.csv"
df = pd.read_csv(input_file, parse_dates=["USFR_Low_Date", "USFR_Peak_Date"])

# Sort chronologically by low date
df = df.sort_values(by="USFR_Low_Date").reset_index(drop=True)

# Step 1: Track valid low → high cycles
lows = []
highs = []

last_high_date = pd.Timestamp("2000-01-01")  # baseline

for _, row in df.iterrows():
    low_date = row["USFR_Low_Date"]
    low_price = row["USFR_Low"]
    high_date = row["USFR_Peak_Date"]
    high_price = row["USFR_Peak"]

    # Only treat this high as valid if it's after the last high
    if low_date > last_high_date:
        lows.append({"USFR_Low_Date": low_date, "USFR_Low": low_price})
        highs.append({"USFR_Peak_Date": high_date, "USFR_Peak": high_price})
        last_high_date = high_date

# Save clean output
pd.DataFrame(highs).to_csv("signals/usfr_post_peak_highs_only.csv", index=False)
pd.DataFrame(lows).to_csv("signals/usfr_post_peak_lows_only.csv", index=False)

print("✅ Split complete. Files written:")
print(" • signals/usfr_post_peak_highs_only.csv")
print(" • signals/usfr_post_peak_lows_only.csv")
