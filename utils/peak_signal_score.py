"""
peak_signal_score.py - Real-time Peak Signal Scoring for Treasury ETFs

This module defines logic to compute a daily peak signal score for same-month peaking ETFs
(SGOV, BIL, SHV, TFLO, ICSH) based on proximity to recent high, volume spike, and timing.

Score Criteria:
- Price within 0.03% of 10-day high → +1
- Volume ≥ 30% above 5-day avg → +1
- Calendar day in [28–31] → +1
- Consecutive day at same peak price → +0.5

Returns:
    dict with score, breakdown, and context data
"""
import pandas as pd
from datetime import datetime, timedelta

def compute_peak_score(etf: str, df: pd.DataFrame, today: datetime = None, debug: bool = False):
    if today is None:
        today = pd.Timestamp.today().normalize()

    # Ensure datetime
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)

    price_col = etf
    vol_col = f"{etf}_Volume"

    if today not in df.index:
        if debug:
            print(f"[SKIP] {etf} — No data for {today.date()}")
        return None

    # Extract relevant data windows
    recent_df = df.loc[:today].tail(11)
    if len(recent_df) < 6:
        if debug:
            print(f"[SKIP] {etf} — Not enough data for scoring")
        return None

    # 10-day high (excluding today)
    prev_10 = recent_df.iloc[:-1]
    high_10d = prev_10[price_col].max()
    price_today = recent_df.iloc[-1][price_col]

    # Price near high (within 0.03%)
    price_close_to_high = abs(price_today - high_10d) / high_10d <= 0.0003

    # Volume spike
    vol_today = recent_df.iloc[-1][vol_col]
    vol_avg = prev_10[vol_col].tail(5).mean()
    volume_spike = vol_today >= 1.3 * vol_avg

    # End-of-month timing
    calendar_score = today.day >= 28

    # Consecutive-day peak check
    peak_match_yesterday = (recent_df.iloc[-2][price_col] == price_today)

    score = (
        1.0 * price_close_to_high +
        1.0 * volume_spike +
        1.0 * calendar_score +
        0.5 * peak_match_yesterday
    )

    result = {
        'Date': today.date(),
        'ETF': etf,
        'Score': round(score, 2),
        'Price_Today': round(price_today, 4),
        '10D_High': round(high_10d, 4),
        'Volume_Today': int(vol_today),
        'Avg_Vol_5D': int(vol_avg),
        'Price_Near_High': price_close_to_high,
        'Volume_Spike': volume_spike,
        'Late_Month': calendar_score,
        'Repeat_High': peak_match_yesterday,
        'Comment': '✅ Strong signal' if score >= 3 else '⚠️ Watch closely' if score >= 2 else 'No clear peak yet'
    }

    if debug:
        print(f"[{etf}] Score: {score} — Detail: {result}")

    return result
