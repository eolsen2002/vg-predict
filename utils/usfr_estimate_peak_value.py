# utils/usfr_estimate_peak_value.py

import pandas as pd
from datetime import datetime, timedelta

def estimate_usfr_peak_value(
    price_csv="data/etf_prices_2023_2025.csv",
    cycles_csv="signals/usfr_full_cycles.csv",
    ex_div_date="2025-06-25"
):
    """
    Estimate the likely USFR peak value before ex-dividend date.
    Assumes peak is 1 market day before ex-div date.
    Uses recent price slope + past peak gains to forecast.
    """

    # Convert to date object
    ex_div = datetime.strptime(ex_div_date, "%Y-%m-%d").date()
    expected_peak_date = ex_div - timedelta(days=1)

    # Load price history
    prices = pd.read_csv(price_csv, parse_dates=["Date"])
    prices = prices[["Date", "USFR"]].dropna()
    prices["Date"] = pd.to_datetime(prices["Date"]).dt.date
    prices.sort_values("Date", inplace=True)

    # Filter last 5 USFR trading days
    recent = prices.tail(5).copy()
    if len(recent) < 2:
        return {"error": "Not enough recent USFR data to estimate"}

    # Calculate slope (simple average daily change)
    recent["Change"] = recent["USFR"].diff()
    slope = recent["Change"].mean()

    # Most recent date + price
    last_date = recent.iloc[-1]["Date"]
    last_price = recent.iloc[-1]["USFR"]

    # Estimate days remaining to peak
    days_until_peak = max((expected_peak_date - last_date).days, 0)
    est_peak = last_price + slope * days_until_peak

    # Optional: use last 6 peak gains as benchmark
    try:
        cycles = pd.read_csv(cycles_csv)
        peak_gains = cycles["Gain_%"].dropna().astype(float).tail(6)
        avg_peak_gain = peak_gains.mean() / 100  # Convert % to multiplier
        hist_peak_est = last_price * (1 + avg_peak_gain)
    except:
        avg_peak_gain = None
        hist_peak_est = None

    return {
        "last_price": round(last_price, 4),
        "recent_slope": round(slope, 6),
        "days_until_peak": days_until_peak,
        "est_peak_value_slope": round(est_peak, 4),
        "est_peak_value_hist": round(hist_peak_est, 4) if hist_peak_est else None,
        "expected_peak_date": expected_peak_date.strftime("%Y-%m-%d"),
        "source_last_date": last_date.strftime("%Y-%m-%d"),
    }

