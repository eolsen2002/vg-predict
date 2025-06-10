"""Optional GUI to be developed"""
# eft_dashboard.py
import pandas as pd
from datetime import timedelta

# Load the USFR post-peak signals
usfr_signals = pd.read_csv("signals/usfr_post_peak_lows.csv", parse_dates=["USFR_Peak_Date", "USFR_Low_Date"])

# Optional: print recent months to verify
print(usfr_signals.tail())

# ✅ Check Today’s Date vs Signal (Re-entry Alert Logic)
today = pd.Timestamp.today().normalize()  # Get today's date without time

# Set re-entry detection window (±1 calendar day)
reentry_window = 1

# Find any matching re-entry rows
matching_row = usfr_signals[
    (usfr_signals["USFR_Low_Date"] >= today - timedelta(days=reentry_window)) &
    (usfr_signals["USFR_Low_Date"] <= today + timedelta(days=reentry_window))
]

# Output results
if not matching_row.empty:
    print("📈 USFR re-entry signal detected!")
    print(matching_row.to_string(index=False))
else:
    print("🔍 No USFR re-entry signal today.")

# ✅ Load latest USFR price
price_df = pd.read_csv("data/etf_prices_2023_2025.csv", index_col=0, parse_dates=True)
price_df.index = pd.to_datetime(price_df.index, utc=True).tz_convert(None)

# Filter for USFR column only
usfr_price_series = price_df["USFR"].dropna()

# Get most recent trading day and price
latest_date = usfr_price_series.index.max()
latest_price = usfr_price_series.loc[latest_date]

# 🧠 Get most recent signal low
most_recent_low = usfr_signals["USFR_Low"].iloc[-1]
most_recent_low_date = usfr_signals["USFR_Low_Date"].iloc[-1]

# 🔍 Compare if today’s price is near the most recent low (±$0.01)
price_diff = abs(latest_price - most_recent_low)

print(f"\n📅 Latest USFR price ({latest_date.date()}): {latest_price:.3f}")
print(f"📉 Most recent signal low ({most_recent_low_date.date()}): {most_recent_low:.3f}")

if price_diff <= 0.01:
    print("⚠️  USFR price is within 1¢ of the most recent post-peak low — possible re-entry opportunity!")
else:
    print("✅ USFR not near recent low — no alert.")
