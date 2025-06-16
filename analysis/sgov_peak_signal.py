"""
Real-time SGOV Peak Signal Detection
sgov_peak_signal.py 6/13/25, 11:18 pm

Purpose:
Detect whether the current day is a likely SGOV peak, using multiple indicators:
- Price proximity to recent 10-day high
- Calendar timing (target peak: last trading day of the month)
- Divergence from other Treasury ETFs (USFR, TFLO, SHV, BIL, ICSH)
- Placeholder for macro or volume indicator (static score for now)

Outputs:
- Dict for GUI integration: date, score, message, SGOV price
- Logs daily score to: logs/sgov_peak_signals.csv

Last updated: 2025-06-13
"""

import pandas as pd
from datetime import datetime, timedelta
import os

ETF = "SGOV"
PEERS = ["USFR", "TFLO", "SHV", "BIL", "ICSH"]
LOG_PATH = f"logs/{ETF.lower()}_peak_signals.csv"
DATA_PATH = "data/etf_prices_2023_2025.csv"

def load_data():
    df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(None)
    return df[[ETF] + PEERS].dropna()

def compute_score(today, df):
    if today not in df.index:
        return None, "No data for today", None

    today_price = df.loc[today, ETF]
    recent_window = df.loc[today - timedelta(days=10):today]
    ten_day_high = recent_window[ETF].max()
    high_proximity = 1 - ((ten_day_high - today_price) / ten_day_high)

    # Calendar score: peaks expected on last 1–2 days of the month
    day = today.day
    month = today.month
    year = today.year
    last_day = (today + pd.offsets.MonthEnd(0)).day
    calendar_score = 1 if day == last_day else 0.5 if day >= last_day - 1 else 0

    peer_mean = df.loc[today, PEERS].mean()
    divergence = today_price - peer_mean
    divergence_score = 1 if divergence > 0.05 else 0.5 if divergence > 0.01 else 0

    macro_score = 0.5  # placeholder

    score = round((0.4 * high_proximity + 0.3 * calendar_score + 0.2 * divergence_score + 0.1 * macro_score) * 100, 1)

    message = (
        "✅ Likely SGOV Peak" if score >= 75 else
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

def get_sgov_peak_signal():
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
    result = get_sgov_peak_signal()
    print(f"SGOV Peak Score for {result['date']}: {result['score']} — {result['message']}")

if __name__ == "__main__":
    main()
