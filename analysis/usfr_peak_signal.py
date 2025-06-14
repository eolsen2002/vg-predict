# analysis/usfr_peak_signal.py

"""
Real-time USFR Peak Signal Detection

Purpose:
Detect whether the current day is a likely USFR peak, using multiple indicators:
- Price proximity to recent 10-day high
- Calendar timing (target range: 18–25 of each month)
- Divergence from other Treasury ETFs (SGOV, TFLO, SHV, BIL, ICSH)
- (Optional) Reverse Repo volume or macro indicators (placeholder)

Outputs:
- Dict for GUI integration: date, score, message, USFR price
- Logs daily score and signal to: logs/usfr_peak_signals.csv

Usage:
- Import get_usfr_peak_signal() from this file for GUI display
- Run directly to print today's score

Last updated: 2025-06-13
"""

import pandas as pd
from datetime import datetime, timedelta
import os

ETF_PEERS = ["SGOV", "TFLO", "SHV", "BIL", "ICSH"]
LOG_PATH = "logs/usfr_peak_signals.csv"
DATA_PATH = "data/etf_prices_2023_2025.csv"

def load_data():
    df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(None)
    return df[["USFR"] + ETF_PEERS].dropna()

def compute_score(today, df):
    if today not in df.index:
        return None, "No data for today", None

    today_price = df.loc[today, "USFR"]
    recent_window = df.loc[today - timedelta(days=10):today]
    ten_day_high = recent_window["USFR"].max()
    high_proximity = 1 - ((ten_day_high - today_price) / ten_day_high)

    # Calendar timing score
    day = today.day
    calendar_score = 1 if 18 <= day <= 25 else 0.5 if 15 <= day <= 27 else 0

    # ETF divergence score
    peer_mean = df.loc[today, ETF_PEERS].mean()
    divergence = today_price - peer_mean
    divergence_score = 1 if divergence > 0.05 else 0.5 if divergence > 0.01 else 0

    # Placeholder for reverse repo or macro score
    rrp_score = 0.5

    # Weighted total score
    score = round((0.4 * high_proximity + 0.3 * calendar_score + 0.2 * divergence_score + 0.1 * rrp_score) * 100, 1)

    message = (
        "✅ Likely USFR Peak" if score >= 75 else
        "⚠️ Watch Closely" if score >= 60 else
        "⬇️ No Peak Signal"
    )
    return score, message, today_price

def log_signal(today, score, message):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    row = pd.DataFrame([[today.strftime("%Y-%m-%d"), score, message]], columns=["Date", "Score", "Signal"])
    if os.path.exists(LOG_PATH):
        row.to_csv(LOG_PATH, mode='a', header=False, index=False)
    else:
        row.to_csv(LOG_PATH, index=False)

def get_usfr_peak_signal():
    df = load_data()
    today = df.index.max()
    score, message, price = compute_score(today, df)

    if score is not None:
        log_signal(today, score, message)
        return {
            "date": today.strftime("%Y-%m-%d"),
            "score": score,
            "message": message,
            "price": round(price, 4)
        }
    else:
        return {
            "date": today.strftime("%Y-%m-%d"),
            "score": None,
            "message": "❌ No data for today",
            "price": None
        }

def main():
    result = get_usfr_peak_signal()
    print(f"USFR Peak Score for {result['date']}: {result['score']} — {result['message']}")

if __name__ == "__main__":
    main()
