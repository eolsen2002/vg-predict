#test_signal.py
# Let’s confirm that your signal checker function check_etf_signal_with_countdown is working correctly.
from scripts.analyze_signals import check_etf_signal_with_countdown

def test():
    etfs = ['USFR', 'SGOV']
    signals = ['Low', 'Peak']

    for etf in etfs:
        for signal in signals:
            result = check_etf_signal_with_countdown(etf, signal)
            print(f"ETF: {etf} Signal: {signal}")
            print("Message:", result['text'])
            print("Days until next:", result['days_until'])
            print("---")

if __name__ == "__main__":
    test()
