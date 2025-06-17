# scripts/test_update_modal_days_full.py
# scripts/test_update_modal_days_full.py
from scripts.update_modal_days import update_peak_modal_day
import pandas as pd

def test_update_modal_days():
    etfs = ['USFR', 'SGOV', 'BIL', 'SHV', 'TFLO', 'ICSH']

    for etf in etfs:
        print(f"\nTesting update_peak_modal_day for ETF: {etf}")
        update_peak_modal_day(etf)

        # Load updated cycles CSV to verify Peak_Modal_Day
        cycles_path = f'signals/{etf.lower()}_full_cycles.csv'
        try:
            cycles = pd.read_csv(cycles_path)
        except FileNotFoundError:
            print(f"[ERROR] Missing {cycles_path}")
            continue

        # Now no rename needed here

        # Print last few rows to check Peak_Modal_Day was updated
        if 'Cycle_Month' in cycles.columns:
            print(cycles.tail(3)[['Cycle_Month', 'Peak_Modal_Day']])
        else:
            print(f"[WARN] 'Cycle_Month' column missing in {etf} full cycles")
            print(cycles.tail(3))

if __name__ == "__main__":
    test_update_modal_days()
