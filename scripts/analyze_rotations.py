""" new file to analyze rotations 
analyze_rotations.py"""
import pandas as pd

# Load ETF price data and USFR peak dates
df = pd.read_csv("etf_prices_2023_2025.csv", index_col=0, parse_dates=True)
df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)

usfr_peaks_df = pd.read_csv("usfr_peaks.csv", parse_dates=["USFR_Peak_Date", "USFR_Low_Date"])
usfr_peaks_df["Month"] = usfr_peaks_df["USFR_Peak_Date"].dt.to_period("M")

# ETFs to evaluate
etfs = ['SGOV', 'BIL', 'TFLO', 'SHV', 'ICSH']
usfr = 'USFR'

results = []

for _, row in usfr_peaks_df.iterrows():
    peak_date = row["USFR_Peak_Date"]
    low_date = row["USFR_Low_Date"]
    month_str = row["Month"].strftime("%Y-%m")

    try:
        usfr_peak_price = df.loc[peak_date, usfr]
        usfr_low_price = df.loc[low_date, usfr]
        usfr_return = (usfr_peak_price - usfr_low_price) / usfr_low_price * 100
    except:
        usfr_return = None
        usfr_peak_price = None

    # End of month
    month_end = peak_date + pd.offsets.MonthEnd(0)
    df_eom = df[(df.index >= peak_date) & (df.index <= month_end)]

    result_row = {
        "Month": month_str,
        "USFR_Peak_Date": peak_date.strftime("%Y-%m-%d"),
        "USFR_Peak": round(usfr_peak_price, 5) if usfr_peak_price else None,
        "USFR_Return_Low_to_Peak%": round(usfr_return, 3) if usfr_return else None
    }

    for etf in etfs:
        try:
            price_on_peak = df.loc[peak_date, etf]
            price_eom = df_eom[etf].dropna().iloc[-1]
            pct_gain = (price_eom - price_on_peak) / price_on_peak * 100
            result_row[f"{etf}_Return%"] = round(pct_gain, 3)
        except:
            result_row[f"{etf}_Return%"] = None


    # Determine best ETF to rotate into
    rotation_candidates = {etf: result_row.get(f"{etf}_Return%") for etf in etfs}
    valid_returns = {k: v for k, v in rotation_candidates.items() if v is not None}

    if valid_returns:
        best_etf = max(valid_returns, key=valid_returns.get)
        result_row["Best_Rotation_ETF"] = best_etf
        result_row["Best_Rotation_Return%"] = valid_returns[best_etf]
    else:
        result_row["Best_Rotation_ETF"] = None
        result_row["Best_Rotation_Return%"] = None

    results.append(result_row)

# Export results
summary_df = pd.DataFrame(results)
summary_df.to_csv("etf_rotation_backtest.csv", index=False)

print("✅ Backtest complete. Output saved to etf_rotation_backtest.csv.")
