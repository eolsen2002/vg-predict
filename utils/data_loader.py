# utils/data_loader.py 
# Create a helper module to load and preprocess ETF data

import pandas as pd

# Your load_etf_data() function reads the CSV and preprocesses 
# the DataFrame (including forward-filling and date parsing).
def load_etf_data(filepath):
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df = df.sort_index()
    df = df.asfreq('B')  # Optional: aligns index to business days
    df.ffill(inplace=True)
    return df
