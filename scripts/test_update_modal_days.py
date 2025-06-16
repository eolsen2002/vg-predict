# test_update_modal_days.py

from scripts.update_modal_days import update_peak_modal_day

if __name__ == "__main__":
    # Example ETFs to test
    etfs_to_test = ['USFR', 'SGOV', 'BIL']

    for etf in etfs_to_test:
        print(f"\nTesting update_peak_modal_day for ETF: {etf}")
        update_peak_modal_day(etf)
