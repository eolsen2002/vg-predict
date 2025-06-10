import pandas as pd
import os

signals_dir = "signals"
file_suffix = "_post_peak_highs.csv"
etfs = ["SGOV", "BIL", "SHV", "TFLO", "ICSH"]

for etf in etfs:
    file_path = os.path.join(signals_dir, f"{etf.lower()}{file_suffix}")
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        continue

    try:
        df = pd.read_csv(file_path)

        # Rename all ETF-specific columns to standard ones
        rename_map = {
            f"{etf}_Peak_Date": "Peak_Date",
            f"{etf}_Peak": "Peak",
            f"{etf}_Low_Date": "Low_Date",
            f"{etf}_Low": "Low"
        }
        df.rename(columns=rename_map, inplace=True)

        # Save it back
        df.to_csv(file_path, index=False)
        print(f"✅ Standardized: {file_path}")
    except Exception as e:
        print(f"⚠️ Error processing {file_path}: {e}")
