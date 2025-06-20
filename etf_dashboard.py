'''Here’s the updated etf_dashboard.py with the changes you requested:

Show only the last confirmed peak date (from CSV) — no extra intermediate peak lines

Show latest close date and price separately, for all ETFs

Keep countdown days to next peak/low with highlights for soonest signals

Green highlight on earliest peak and low days among selected ETFs, as before'''

# etf_dashboard.py, updated 6/15/25 with USFR post-peak low GUI integration
# etf_dashboard.py, updated 6/15/25 with requested enhancements
# added new helper function to silently run update_modal_days.py in the background, 
#   with "update_modal_days_background()" added just before "root.after(100, auto_refresh_on_startup)", 6/16/25, 1:10 pm
"""
etf_dashboard.py, updated 6/15/25 with USFR post-peak low GUI integration
etf_dashboard.py, updated 6/15/25 with requested enhancements
"""
# etf_dashboard.py, updated full script with green highlight ONLY on days until peak/low line
# etf_dashboard.py, updated full script with green highlight ONLY on days until peak/low line
# etf_dashboard.py, updated 6/20/25
# Includes aligned left-right ETF info and monospaced font for both Text widgets

import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import csv
from datetime import datetime, date
from dateutil import parser
from analysis.usfr_peak_signal import get_usfr_peak_signal
from scripts.peak_signal_score import get_all_peak_scores
from scripts.analyze_signals import check_etf_signal_with_countdown
from scripts.usfr_post_peak_lows import run_usfr_post_peak_lows
from analysis.usfr_full_cycles import run_usfr_full_cycles
from utils.usfr_estimate_peak_value import estimate_usfr_peak_value

ETFS = ['USFR', 'SGOV', 'BIL', 'SHV', 'TFLO', 'ICSH']
SIGNALS = ["Low", "Peak", "Both"]

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

    peak_scores = get_all_peak_scores()
    usfr_score = get_usfr_peak_signal()

    for etf in selected_etfs:
        peak_info = peak_info_dict.get(etf, {})
        low_info = low_info_dict.get(etf, {})
        score_info = usfr_score if etf == 'USFR' else peak_scores.get(etf, {})

        # Format text in two columns
        header = f"=== {etf} ==="
        peak_line = (
            f"🧠 Peak (modal {peak_info.get('modal_day', '?')}): "
            f"{peak_info.get('next_date', 'n/a'):<10}  "
            f"Days: {str(peak_info.get('days_until', '?')).ljust(3)}"
        )
        low_line = (
            f"🧠 Low  (modal {low_info.get('modal_day', '?')}): "
            f"{low_info.get('next_date', 'n/a'):<10}  "
            f"Days: {str(low_info.get('days_until', '?')).ljust(3)}"
        )
        score_line = (
            f"📊 Score: {score_info.get('score', '?')}  "
            f"{score_info.get('message', ''):<25}  "
            f"${score_info.get('price', '?')}"
        )

        left_text.insert(tk.END, f"{header}\n{peak_line}\n")
        right_text.insert(tk.END, f"{low_line}\n{score_line}\n\n")

    display_usfr_peak_estimate()

def display_usfr_peak_estimate():
    try:
        est = estimate_usfr_peak_value()
        if 'error' in est:
            right_text.insert(tk.END, f"\n[Estimation Error] {est['error']}\n")
            return

        msg = (
            "\n📈 USFR Peak Value Estimate:\n"
            f"From price slope:       ${est['est_peak_value_slope']}\n"
            f"From historical gains:  ${est['est_peak_value_hist']}\n"
            f"Days remaining:         {est['days_until_peak']} (to {est['expected_peak_date']})\n"
        )
        right_text.insert(tk.END, msg)
    except Exception as e:
        right_text.insert(tk.END, f"\n[Estimation Error] {e}\n")

def refresh_data():
    try:
        subprocess.run(["python", "scripts/fetch_etf_data.py"], check=True)
        timestamp = datetime.now().strftime("%a %m/%d/%y %H:%M:%S")
        last_updated_label.config(text=f"Last data refresh: {timestamp}")
        messagebox.showinfo("Success", "ETF data refreshed.")
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
            print(f"[Modal Update Error] {e}")
    threading.Thread(target=_update, daemon=True).start()

def auto_refresh_on_startup():
    def _refresh():
        try:
            subprocess.run(["python", "scripts/fetch_etf_data.py"], check=True)
            timestamp = datetime.now().strftime("%a %m/%d/%y %H:%M:%S")
            last_updated_label.config(text=f"Last data refresh: {timestamp}")
        except Exception as e:
            last_updated_label.config(text=f"Auto refresh failed: {e}")
    threading.Thread(target=_refresh, daemon=True).start()

# ---------- GUI SETUP ----------
root = tk.Tk()
root.title("ETF Signal Dashboard")
root.geometry("1100x650")

mono_font = ("Courier New", 10)

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

last_updated_label = tk.Label(root, text="Last data refresh: never")
last_updated_label.pack(pady=5)

output_frame = tk.Frame(root)
output_frame.pack(fill="both", expand=True, padx=10, pady=5)

left_text = tk.Text(output_frame, wrap="none", width=60, font=mono_font)
left_text.pack(side="left", fill="both", expand=True)

right_text = tk.Text(output_frame, wrap="none", width=60, font=mono_font, bg="#f5f5f5")
right_text.pack(side="right", fill="both", expand=True)

def main():
    update_modal_days_background()
    root.after(100, auto_refresh_on_startup)
    run_analysis()
    root.mainloop()

if __name__ == "__main__":
    main()
