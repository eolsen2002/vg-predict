# analysis/usfr_full_cycles.py

# Last updated: 2025-06-15, 3:50 pm

"""

Detects low-to-peak cycles for USFR, including incomplete ongoing cycles.



Cycle rules:

- Low typically occurs near end of the month

- Peak occurs mid-to-late in the following month

- At least 10 calendar days between low and peak

- Peak must be local max (higher than next 1–2 days), unless in current month

- Low must be local min within its 2-day window



Adds:

- 'Cycle_Complete' = False if peak is not yet confirmed

- 'Peak_Signal_Strength' = proximity to 10-day high (lower % = stronger peak)

"""



import pandas as pd

from datetime import timedelta



def load_usfr_data(csv_path="data/etf_prices_2023_2025.csv"):

    """

    Load USFR price series from a CSV file.

    Returns a DataFrame with datetime index and 'USFR' price column.

    """

    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)

    df.index = pd.to_datetime(df.index, utc=True).tz_convert(None)

    return df[["USFR"]].dropna()



def compute_peak_signal_strength(df, peak_day):

    """

    Computes peak signal strength as % distance between the peak

    and the highest price in the prior 10 trading days.

    Lower % distance = stronger signal.

    """

    prior_window = df[(df.index <= peak_day) & (df.index >= peak_day - timedelta(days=10))]

    if prior_window.empty:

        return None

    high_10d = prior_window["USFR"].max()

    peak_price = df.loc[peak_day]["USFR"]

    return round((high_10d - peak_price) / high_10d * 100, 3)



def detect_usfr_full_cycles(df):
    """
    Scans for valid low-to-peak cycles using monthly patterns.
    Returns a DataFrame of full cycles, including incomplete ones.
    """
    results = []
    months = pd.date_range(start=df.index.min(), end=df.index.max(), freq="MS")
    latest_date = df.index.max()

    for i in range(len(months) - 1):
        month1 = months[i]
        month2 = months[i + 1]

        # Low = late part of month1
        late_month1 = df[(df.index >= month1 + pd.Timedelta(days=18)) & 
                         (df.index <= month1 + pd.offsets.MonthEnd(0))]

        # Peak = mid-late part of month2 (use available data even if incomplete)
        peak_start = month2 + pd.Timedelta(days=12)
        peak_end = min(month2 + pd.offsets.MonthEnd(0), latest_date)
        mid_late_month2 = df[(df.index >= peak_start) & (df.index <= peak_end)]

        if late_month1.empty or mid_late_month2.empty:
            continue

        # Detect low and peak prices and dates
        low_price = late_month1["USFR"].min()
        low_day = late_month1[late_month1["USFR"] == low_price].index.min()

        peak_price = mid_late_month2["USFR"].max()
        peak_day = mid_late_month2[mid_late_month2["USFR"] == peak_price].index.max()

        # Require minimum separation
        if (peak_day - low_day).days < 10:
            continue

        # Confirm valid low (lowest in a 3-day window)
        post_low_window = df[(df.index >= low_day) & (df.index <= low_day + timedelta(days=2))]
        if low_price != post_low_window["USFR"].min():
            continue

        # Confirm valid peak unless it's still unfolding
        future_days = df[(df.index > peak_day) & (df.index <= peak_day + timedelta(days=2))]
        cycle_complete = True
        if not future_days.empty and future_days["USFR"].max() >= peak_price:
            cycle_complete = False

        # If peak is in current month, allow incomplete
        if peak_day.month == latest_date.month and peak_day.year == latest_date.year:
            cycle_complete = False

        peak_strength = compute_peak_signal_strength(df, peak_day)
        gain_pct = round((peak_price - low_price) / low_price * 100, 3)

        if gain_pct > 0:
            results.append({
                "Cycle_Start_Month": month1.strftime("%Y-%m"),
                "Low_Date": low_day.strftime("%Y-%m-%d"),
                "Low": low_price,
                "Peak_Date": peak_day.strftime("%Y-%m-%d"),
                "Peak": peak_price,
                "Gain_%": gain_pct,
                "Cycle_Complete": cycle_complete,
                "Peak_Signal_Strength": peak_strength
            })

    return pd.DataFrame(results)




def main():

    """

    Main entry point to detect USFR full cycles and save to CSV.

    """

    df = load_usfr_data()

    full_cycles = detect_usfr_full_cycles(df)

    full_cycles.to_csv("signals/usfr_full_cycles.csv", index=False)

    print("✅ USFR full cycles saved to signals/usfr_full_cycles.csv")

def run_usfr_full_cycles():
    df = load_usfr_data()
    full_cycles = detect_usfr_full_cycles(df)
    full_cycles.to_csv("signals/usfr_full_cycles.csv", index=False)
    return full_cycles

if __name__ == "__main__":

    main()

