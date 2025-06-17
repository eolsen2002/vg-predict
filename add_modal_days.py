'''
✅ Step 1 Fix: Add Low_Modal_Day and Peak_Modal_Day Columns
Let’s add them programmatically using a quick Python script.

🛠 Script: Add Modal Day Columns to All Full-Cycle Files
6/16/25, 12:42 pm
'''


import pandas as pd
import os

# List of ETFs and paths
etfs = ['sgov', 'bil', 'shv', 'tflo', 'icsh']
input_dir = 'signals/'
output_dir = 'signals/'  # overwrite or change if desired

for etf in etfs:
    file_path = os.path.join(input_dir, f"{etf}_full_cycles.csv")

    if not os.path.exists(file_path):
        print(f"[WARN] File not found: {file_path}")
        continue

    df = pd.read_csv(file_path)

    # Add modal columns by copying values from Low_Date and Peak_Date
    df['Low_Modal_Day'] = df['Low_Date']
    df['Peak_Modal_Day'] = df['Peak_Date']

    # Save back to CSV (overwrite)
    df.to_csv(os.path.join(output_dir, f"{etf}_full_cycles.csv"), index=False)
    print(f"[OK] Modal columns added to: {etf}_full_cycles.csv")
