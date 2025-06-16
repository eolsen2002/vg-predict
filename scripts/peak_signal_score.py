"""
scripts/peak_signal_score.py
Updated: 2025-06-13, 10:02 pm

Purpose:
- Compute peak signal scores for 5 Treasury ETFs (SGOV, TFLO, SHV, BIL, ICSH)
- Based on:
  - Price proximity to 10-day high
  - Calendar window (day 25–31 = strongest)
  - ETF-specific monthly timing logic

Exports:
- get_peak_signal_score(etf: str)
- get_all_peak_scores()
"""

import pandas as pd
from datetime import datetime, timedelta
import os

DATA_PATH = "data/etf_prices_2023_2025.csv"
ETF_LIST = ["SGOV", "TFLO", "SHV", "BIL", "ICSH"]

def load_data():
    df = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(None)
    return df[ETF_LIST].dropna()

def compute_score(df, etf, today):
    if today not in df.index:
        return None, "No data for today", None

    today_price = df.loc[today, etf]
    recent_window = df.loc[today - timedelta(days=10):today]
    ten_day_high = recent_window[etf].max()
    high_proximity = 1 - ((ten_day_high - today_price) / ten_day_high)

    # Calendar timing score
    day = today.day
    calendar_score = 1 if day >= 27 else 0.5 if day >= 25 else 0

    score = round((0.7 * high_proximity + 0.3 * calendar_score) * 100, 1)

    message = (
        "✅ Likely Peak" if score >= 75 else
        "⚠️ Watch Closely" if score >= 60 else
        "⬇️ No Peak Signal"
    )
    return score, message, today_price

def get_peak_signal_score(etf: str):
    df = load_data()
    today = df.index.max()
    score, message, price = compute_score(df, etf, today)

    return {
        "date": today.strftime("%Y-%m-%d"),
        "score": score,
        "message": message,
        "price": round(price, 4) if price else None
    }

def get_all_peak_scores():
    df = load_data()
    today = df.index.max()
    results = {}

    for etf in ETF_LIST:
        score, message, price = compute_score(df, etf, today)
        results[etf] = {
            "date": today.strftime("%Y-%m-%d"),
            "score": score,
            "message": message,
            "price": round(price, 4) if price else None
        }

    return results
