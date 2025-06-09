"""
generate_peak_csvs.py
Generates monthly peak signal CSVs for 6 Treasury ETFs from wide-format historical prices.

Input:
- data/etf_prices_2023_2025.csv (columns: Date, USFR, SGOV, etc.)

Output:
- signals/usfr_post_peak_highs.csv
- signals/sgov_post_peak_highs.csv
- signals/tflo_post_peak_highs.csv
- signals/bil_post_peak_highs.csv
- signals/shv_post_peak_highs.csv
- signals/icsh_post_peak_highs.csv
"""

import pandas as pd
import os

# === Config ===
input_path = "data/etf_prices_2023_2025.csv"
output_dir = "signals"
os.makedirs(output_dir, exist_ok=True)

etfs = ["USFR", "SGOV", "TFLO", "BIL", "SHV", "ICSH"]
rebound_threshold = 0.002  # 0.2% minimum rebound for a valid peak

# === Load and reshape price data ===
df = pd.read_csv(input_path, parse_dates=["Date"])
df_long = df.melt(id_vars=["Date"], var_name="ETF", value_name="Close")
df_long["Month"] = df_long["Date"].dt.to_period("M")

# === Peak signal generation ===
def find_valid_peaks(df_etf: pd.DataFrame, etf: str) -> pd.DataFrame:
    peak_signals = []

    for month, group in df_etf.groupby("Month"):
        month_str = str(month)
        peak_row = None
        window = group[(group["Date"].dt.day >= 18) & (group["Date"].dt.day <= 23)]

        # Fallback: use full month if 18–23 window is empty
        if window.empty:
            print(f"⚠️ {etf} {month_str}: No data in 18–23 window, using full month.")
            window = group

        peak_row = window.loc[window["Close"].idxmax()]
        peak_date = peak_row["Date"]
        peak_price = peak_row["Close"]

        # Look back 10 trading days before peak for lowest price
        pre_peak = group[group["Date"] < peak_date]
        pre_window = pre_peak.tail(10)

        if pre_window.empty:
            print(f"⚠️ {etf} {month_str}: No 10-day pre-window, skipping.")
            continue

        low_row = pre_window.loc[pre_window["Close"].idxmin()]
        low_date = low_row["Date"]
        low_price = low_row["Close"]

        rebound_pct = (peak_price - low_price) / low_price

        if rebound_pct >= rebound_threshold:
            signal = {
                f"{etf}_Low_Date": low_date.date(),
                f"{etf}_Low": round(low_price, 3),
                f"{etf}_Peak_Date": peak_date.date(),
                f"{etf}_Peak": round(peak_price, 3),
                'Multi_Peak_Days': int((window["Close"] == peak_price).sum()),
                '10D_Low_Before_Peak': round(pre_window["Close"].min(), 3),
                'Was_Peak_in_Prior_Month': peak_date.month != low_date.month
            }
            peak_signals.append(signal)
        else:
            print(f"⚠️ {etf} {month_str}: Rebound {rebound_pct:.3%} too small, using full month.")
            # Retry using full month
            full_peak_row = group.loc[group["Close"].idxmax()]
            peak_date = full_peak_row["Date"]
            peak_price = full_peak_row["Close"]
            pre_peak = group[group["Date"] < peak_date].tail(10)

            if pre_peak.empty:
                continue

            low_row = pre_peak.loc[pre_peak["Close"].idxmin()]
            low_date = low_row["Date"]
            low_price = low_row["Close"]

            fallback_signal = {
                f"{etf}_Low_Date": low_date.date(),
                f"{etf}_Low": round(low_price, 3),
                f"{etf}_Peak_Date": peak_date.date(),
                f"{etf}_Peak": round(peak_price, 3),
                'Multi_Peak_Days': int((group["Close"] == peak_price).sum()),
                '10D_Low_Before_Peak': round(pre_peak["Close"].min(), 3),
                'Was_Peak_in_Prior_Month': peak_date.month != low_date.month
            }
            peak_signals.append(fallback_signal)

    return pd.DataFrame(peak_signals)


# === Run generation for all ETFs ===
for etf in etfs:
    df_etf = df_long[df_long["ETF"] == etf].copy()
    peak_df = find_valid_peaks(df_etf, etf)

    if not peak_df.empty:
        out_file = os.path.join(output_dir, f"{etf.lower()}_post_peak_highs.csv")
        peak_df.to_csv(out_file, index=False)
        print(f"✅ {etf} peak CSV saved: {out_file}")
    else:
        print(f"⚠️ No valid peak signals for {etf}")
