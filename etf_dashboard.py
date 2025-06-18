
'''Here’s the updated etf_dashboard.py with the changes you requested:

Show only the last confirmed peak date (from CSV) — no extra intermediate peak lines

Show latest close date and price separately, for all ETFs

Keep countdown days to next peak/low with highlights for soonest signals

Green highlight on earliest peak and low days among selected ETFs, as before'''

# etf_dashboard.py, updated 6/15/25 with USFR post-peak low GUI integration
# etf_dashboard.py, updated 6/15/25 with requested enhancements
# added new helper function to silently run update_modal_days.py in the background, 
#   with "update_modal_days_background()" added just before "root.after(100, auto_refresh_on_startup)", 6/16/25, 1:10 pm
import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import csv
from datetime import datetime, date
from analysis.usfr_peak_signal import get_usfr_peak_signal
from scripts.peak_signal_score import get_all_peak_scores
from scripts.analyze_signals import check_etf_signal_with_countdown
from scripts.usfr_post_peak_lows import run_usfr_post_peak_lows
from analysis.usfr_full_cycles import run_usfr_full_cycles
from dateutil import parser
import pandas as pd


# Step 4 Debug — Preview USFR modal day data
try:
    df_usfr = pd.read_csv("signals/usfr_full_cycles.csv")
    print("✅ Step 4 Debug — USFR CSV HEAD:\n", df_usfr.head())
except Exception as e:
    print("❌ Error reading USFR CSV:", e)


SIGNALS = ['Low', 'Peak', 'Both']
# Make sure ETFS is defined
ETFS = ['USFR', 'SGOV', 'BIL', 'SHV', 'TFLO', 'ICSH']

for etf in ETFS:
    low_info = check_etf_signal_with_countdown(etf, "low")
    peak_info = check_etf_signal_with_countdown(etf, "peak")
    # Now display low_info["text"] and peak_info["text"] in your GUI labels
    print(low_info["text"])
    print(peak_info["text"])

def get_latest_price(etf):
    try:
        with open('data/etf_prices_2023_2025.csv', newline='') as f:
            reader = list(csv.DictReader(f))
            rows = [r for r in reader if r['Ticker'].upper() == etf]
            if not rows:
                return None
            latest = rows[-1]
            return {'date': latest['Date'], 'price': float(latest['Close'])}
    except Exception:
        return None

def find_last_valid_peak_from_csv(etf):
    csv_path = f"signals/{etf.lower()}_full_cycles.csv"
    try:
        with open(csv_path, newline='') as csvfile:
            reader = list(csv.DictReader(csvfile))
            
            # --- Fix for column rename if needed ---
            if reader:
                first_row = reader[0]
                if 'Cycle_Start_Month' in first_row and 'Cycle_Month' not in first_row:
                    for row in reader:
                        row['Cycle_Month'] = row.pop('Cycle_Start_Month')

            for row in reversed(reader):
                try:
                    if float(row['Gain_%']) > 0:
                        dt = parser.parse(row['Peak_Date'])
                        peak_date_fmt = dt.strftime('%-m/%-d/%y')
                        return {
                            'Cycle_Month': row['Cycle_Month'],
                            'Peak_Date': peak_date_fmt,
                            'Peak': row['Peak'],
                            'Gain_%': row['Gain_%']
                        }
                except:
                    continue
    except FileNotFoundError:
        return None
    return None

def format_date_dmy(dt):
    return dt.strftime('%a %m/%d/%y')

def convert_dates_in_text(text):
    import re
    def repl(match):
        y, m, d = match.groups()
        return f"{int(m)}/{int(d)}/{str(y)[2:]}"
    return re.sub(r'(\d{4})-(\d{2})-(\d{2})', repl, text)

"""
this is exactly the function we needed: run_analysis() is where 
the dashboard collects and formats everything including modal_day, days_until, and next_date.
"""

def run_analysis():
    selected_etfs = [etf for etf in ETFS if etf_vars[etf].get()]
    selected_signal = signal_type.get()

    left_text.delete("1.0", tk.END)
    right_text.delete("1.0", tk.END)

    if not selected_etfs:
        messagebox.showwarning("No ETF Selected", "Please select at least one ETF.")
        return

    today_str = format_date_dmy(date.today())
    left_text.insert(tk.END, f"📆 Today: {today_str}\n\n")

    low_days_list, peak_days_list = [], []
    low_info_dict, peak_info_dict = {}, {}

    for etf in selected_etfs:
        if selected_signal in ["Peak", "Both"]:
            peak_info = check_etf_signal_with_countdown(etf, "Peak")
            peak_info_dict[etf] = peak_info
            peak_days_list.append(peak_info.get('days_until', 9999))

        if selected_signal in ["Low", "Both"]:
            low_info = check_etf_signal_with_countdown(etf, "Low")
            low_info_dict[etf] = low_info
            low_days_list.append(low_info.get('days_until', 9999))

    min_peak_days = min([d for d in peak_days_list if d is not None], default=None)
    min_low_days = min([d for d in low_days_list if d is not None], default=None)

    for etf in selected_etfs:
        lines = []

        # Add a clear ETF header line here:
        lines.append(f"=== {etf} ===")  # Label ETF clearly

        # ----- PEAK BLOCK -----
        last_peak = find_last_valid_peak_from_csv(etf)
        if last_peak:
            lines.append(f"📄 last peak: {last_peak['Peak_Date']} @ ${float(last_peak['Peak']):.2f}")

        # Latest close price shown once per ETF here
        latest = get_latest_price(etf)
        if latest:
            lines.append(f"📊 Latest close: {latest['date']} @ ${latest['price']:.2f}")

        if selected_signal in ["Peak", "Both"]:
            peak_info = peak_info_dict.get(etf, {})
            print(f"DEBUG Peak info for {etf}: {peak_info}")  # DEBUG print peak_info
            # Defensive check: all keys present and values not None
            if all(k in peak_info and peak_info[k] is not None for k in ['modal_day', 'next_date', 'days_until']):
                lines.append(f"🧠 Next est. peak (modal {peak_info['modal_day']}): {peak_info['next_date']}")
                lines.append(f"     Days until peak: {peak_info['days_until']}")
            else:
                lines.append("🧠 Next est. peak: No data")

        # ----- LOW BLOCK -----
        if selected_signal in ["Low", "Both"]:
            low_info = low_info_dict.get(etf, {})
            print(f"DEBUG Low info for {etf}: {low_info}")  # DEBUG print low_info
            if all(k in low_info and low_info[k] is not None for k in ['modal_day', 'next_date', 'days_until']):
                lines.append(f"🧠 Next est. low (modal {low_info['modal_day']}): {low_info['next_date']}")
                lines.append(f"     Days until low: {low_info['days_until']}")
            else:
                lines.append("🧠 Next est. low: No data")

        # Insert all lines for this ETF at once, capture indexes for highlighting
        start_idx = left_text.index(tk.END)
        left_text.insert(tk.END, "\n".join(lines) + "\n\n")
        end_idx = left_text.index(tk.END)

        # Highlight ETF header line to be bold
        # The ETF header is the first line, so highlight just that line
        header_tag = f"{etf}_header"
        left_text.tag_add(header_tag, f"{start_idx} linestart", f"{start_idx} lineend")
        left_text.tag_configure(header_tag, font=("TkDefaultFont", 11, "bold"))

        # Highlight relevant lines, green background for soonest peak or low
        peak_days = peak_info_dict.get(etf, {}).get('days_until')
        low_days = low_info_dict.get(etf, {}).get('days_until')

        if selected_signal in ["Peak", "Both"] and peak_days == min_peak_days:
            tag_name = f"{etf}_peak"
            left_text.tag_add(tag_name, start_idx, end_idx)
            left_text.tag_configure(tag_name, background="green", foreground="white", font=("TkDefaultFont", 10, "bold"))

        elif selected_signal in ["Low", "Both"] and low_days == min_low_days:
            tag_name = f"{etf}_low"
            left_text.tag_add(tag_name, start_idx, end_idx)
            left_text.tag_configure(tag_name, background="green", foreground="white", font=("TkDefaultFont", 10, "bold"))


    # ----- RIGHT SIDE: Peak Scores -----
    right_text.insert(tk.END, "📈 Live ETF Peak Signal Scores:\n\n")

    usfr_score = get_usfr_peak_signal()
    if usfr_score:
        right_text.insert(tk.END, f"USFR — Score: {usfr_score['score']} | {usfr_score['message']} | {usfr_score['price']}\n\n")

    peak_scores = get_all_peak_scores()
    for etf in [e for e in ETFS if e != 'USFR']:
        data = peak_scores.get(etf)
        if data:
            right_text.insert(tk.END, f"{etf} — Score: {data['score']} | {data['message']} | {data['price']}\n\n")

# ----- ✅ USFR Post-Peak Low -----
def run_usfr_low_summary():
    try:
        df = run_usfr_full_cycles()
        if df.empty:
            messagebox.showinfo("No Data", "No valid USFR post-peak lows found.")
            return
        last_row = df.iloc[-1]
        msg = (
            f"📉 USFR Last Post-Peak Low:\n"
            f"Peak Date: {last_row['USFR_Peak_Date']} @ ${last_row['USFR_Peak']:.2f}\n"
            f"Low Date: {last_row['USFR_Low_Date']} @ ${last_row['USFR_Low']:.2f}\n"
            f"Drop: {last_row['Drop_%']:.2f}%\n"
        )
        right_text.insert(tk.END, "\n" + msg + "\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run USFR low analysis:\n{e}")

def refresh_data():
    try:
        subprocess.run(["python", "scripts/fetch_etf_data.py"], check=True)
        timestamp = datetime.now().strftime("%a %m/%d/%y %H:%M:%S")
        last_updated_label.config(text=f"Last data refresh: {timestamp} (latest data available)")
        messagebox.showinfo("Success", "ETF data refreshed successfully.")
    except Exception as e:
        last_updated_label.config(text=f"Last data refresh failed: {e}")
        messagebox.showerror("Error", f"Failed to refresh data:\n{e}")

def refresh_data_background():
    threading.Thread(target=refresh_data, daemon=True).start()

def update_modal_days_background():
    def _update():
        try:
            subprocess.run(["python", "scripts/update_modal_days.py"], check=True)
        except Exception as e:
            print(f"[Warning] Failed to update modal days: {e}")
    threading.Thread(target=_update, daemon=True).start()

def auto_refresh_on_startup():
    def _refresh_and_update_label():
        try:
            subprocess.run(["python", "scripts/fetch_etf_data.py"], check=True)
            timestamp = datetime.now().strftime("%a %m/%d/%y %H:%M:%S")
            last_updated_label.config(text=f"Last data refresh: {timestamp} (latest data available)")
        except Exception as e:
            last_updated_label.config(text=f"Auto refresh failed: {e}")
    threading.Thread(target=_refresh_and_update_label, daemon=True).start()

# ----- GUI SETUP -----
root = tk.Tk()
root.title("ETF Signal Dashboard")
root.geometry("1000x600")

etf_frame = tk.LabelFrame(root, text="Select ETFs")
etf_frame.pack(fill="x", padx=10, pady=5)
etf_vars = {}
for etf in ETFS:
    var = tk.BooleanVar(value=True)
    etf_vars[etf] = var
    tk.Checkbutton(etf_frame, text=etf, variable=var).pack(side="left", padx=5)

signal_frame = tk.LabelFrame(root, text="Signal Type")
signal_frame.pack(fill="x", padx=10, pady=5)
signal_type = tk.StringVar(value="Both")
for sig in SIGNALS:
    tk.Radiobutton(signal_frame, text=sig, variable=signal_type, value=sig).pack(side="left", padx=5)

button_frame = tk.Frame(root)
button_frame.pack(fill="x", padx=10, pady=5)
tk.Button(button_frame, text="🔄 Refresh Data", command=refresh_data_background, bg="lightgreen").pack(side="left", padx=5)
tk.Button(button_frame, text="🔄 Refresh Signals", command=run_analysis, bg="lightblue").pack(side="left", padx=5)
tk.Button(button_frame, text="🔎 USFR Post-Peak Lows", command=run_usfr_low_summary, bg="lightyellow").pack(side="left", padx=5)

last_updated_label = tk.Label(root, text="Last data refresh: never")
last_updated_label.pack(pady=5)

output_frame = tk.Frame(root)
output_frame.pack(fill="both", expand=True, padx=10, pady=5)

left_text = tk.Text(output_frame, wrap="word", width=60)
left_text.pack(side="left", fill="both", expand=True)

right_text = tk.Text(output_frame, wrap="word", width=40, bg="#f5f5f5")
right_text.pack(side="right", fill="both", expand=False)

def main():
    update_modal_days_background()
    root.after(100, auto_refresh_on_startup)
    run_analysis()  # display data on startup
    root.mainloop()

if __name__ == "__main__":
    # Debug print for console
    for etf in ETFS:
        low_info = check_etf_signal_with_countdown(etf, "Low")
        peak_info = check_etf_signal_with_countdown(etf, "Peak")
        print(low_info["text"])
        print(peak_info["text"])
        print("-" * 40)

main()
