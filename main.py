# main.py
from datetime import datetime
from scripts.analyze_lows import check_low
from scripts.analyze_peaks import check_peak

etfs = ["USFR", "SGOV", "BIL", "SHV", "TFLO", "ICSH"]

print("🚀 Script started")
print(f"📆 Today is: {datetime.today().date()}\n")

for etf in etfs:
    print(f"\n🔍 Checking LOW signal for {etf}...")
    print(check_low(etf))

for etf in etfs:
    print(f"\n🔍 Checking PEAK signal for {etf}...")
    print(check_peak(etf))
