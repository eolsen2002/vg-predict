import pandas as pd

# Load backtest summary CSV
df = pd.read_csv("data/etf_rotation_backtest.csv")

etfs = ['SGOV', 'BIL', 'TFLO', 'SHV', 'ICSH']

# Calculate average post-USFR-peak returns per ETF
avg_returns = {etf: df[f"{etf}_Return%"].mean() for etf in etfs}

print("📈 Average ETF returns after USFR peak (monthly):")
for etf, avg_ret in avg_returns.items():
    print(f"{etf}: {avg_ret:.3f}%")

# Highlight months with any negative returns
df['Any_Negative_Return'] = df[[f"{etf}_Return%" for etf in etfs]].lt(0).any(axis=1)

neg_months = df[df['Any_Negative_Return']]

print("\n📉 Months with any ETF showing negative return post-USFR peak:")
print(neg_months[['Month'] + [f"{etf}_Return%" for etf in etfs]])

# Optional: Save this filtered analysis
df.to_csv("signals/etf_rotation_analysis_summary.csv", index=False)
print("\n✅ Analysis summary saved to signals/etf_rotation_analysis_summary.csv")
