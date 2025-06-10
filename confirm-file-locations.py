import os

required_paths = [
    "data/etf_prices_2023_2025.csv",
    "scripts/analyze_lows.py",
    "scripts/generate_low_csvs.py",
    "signals/usfr_post_peak_lows.csv",
    "main.py",
    "etf_dashboard.py"
]

missing = [f for f in required_paths if not os.path.exists(f)]
if missing:
    print("⚠️ Missing files:\n", "\n".join(missing))
else:
    print("✅ All critical files are in place.")
