
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
                # Fix for older files with 'Cycle_Start_Month' but no 'Cycle_Month'
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

def display_usfr_peak_estimate():
    ex_div_date = "2025-06-25"  # Update this dynamically if you want
    result = estimate_usfr_peak_value(ex_div_date=ex_div_date)
    if "error" in result:
        right_text.insert(tk.END, "\nUSFR Peak Estimate: Error - " + result["error"] + "\n")
    else:
        msg = (
            f"\n🔮 USFR Estimated Peak Value on {result['expected_peak_date']}:\n"
            f"Last Price: ${result['last_price']}\n"
            f"Recent Slope: {result['recent_slope']}\n"
            f"Days until peak: {result['days_until_peak']}\n"
            f"Est. Peak (Slope): ${result['est_peak_value_slope']}\n"
            f"Est. Peak (Historical Avg Gain): ${result['est_peak_value_hist']}\n"
        )
        right_text.insert(tk.END, msg)

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

    # Collect days_until for min calculation
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
        # ETF header line
        lines.append(f"=== {etf} ===")

        # Last peak from CSV (confirmed)
        last_peak = find_last_valid_peak_from_csv(etf)
        if last_peak:
            lines.append(f"📄 last peak: {last_peak['Peak_Date']} @ ${float(last_peak['Peak']):.2f}")

        # Latest close price separately
        latest = get_latest_price(etf)
        if latest:
            lines.append(f"📊 Latest close: {latest['date']} @ ${latest['price']:.2f}")

        # Insert header, peak, price info first
        start_idx = left_text.index(tk.END)
        left_text.insert(tk.END, "\n".join(lines) + "\n")
        end_idx = left_text.index(tk.END)
        # Header bold
        left_text.tag_add(f"{etf}_header", f"{start_idx} linestart", f"{start_idx} lineend")
        left_text.tag_configure(f"{etf}_header", font=("TkDefaultFont", 11, "bold"))

        # Peak lines and possible highlight on days_until only
        peak_info = peak_info_dict.get(etf, {})
        if selected_signal in ["Peak", "Both"] and all(k in peak_info for k in ['modal_day', 'next_date', 'days_until']):
            peak_line_1 = f"🧠 Next est. peak (modal {peak_info['modal_day']}): {peak_info['next_date']}"
            peak_line_2 = f"     Days until peak: {peak_info['days_until']}"

            start_peak_idx = left_text.index(tk.END)
            left_text.insert(tk.END, peak_line_1 + "\n")
            end_peak_idx = left_text.index(tk.END)
            left_text.insert(tk.END, peak_line_2 + "\n")
            end_peak_days_idx = left_text.index(tk.END)

            if peak_info['days_until'] == min_peak_days:
                end_peak_days_adj = left_text.index(f"{end_peak_days_idx} -1c")
                left_text.tag_add(f"{etf}_peak", start_peak_idx, end_peak_days_adj)
                left_text.tag_configure(f"{etf}_peak", background="green", foreground="white", font=("TkDefaultFont", 10, "bold"))

        # Low lines and possible highlight on days_until only
        low_info = low_info_dict.get(etf, {})
        if selected_signal in ["Low", "Both"] and all(k in low_info and low_info[k] is not None for k in ['modal_day', 'next_date', 'days_until']):
            low_line_1 = f"🧠 Next est. low (modal {low_info['modal_day']}): {low_info['next_date']}"
            low_line_2 = f"     Days until low: {low_info['days_until']}"

            start_low_idx = left_text.index(tk.END)
            left_text.insert(tk.END, low_line_1 + "\n")
            end_low_idx = left_text.index(tk.END)
            left_text.insert(tk.END, low_line_2 + "\n")
            end_low_days_idx = left_text.index(tk.END)

            if low_info['days_until'] == min_low_days:
                end_low_days_adj = left_text.index(f"{end_low_days_idx} -1c")
                left_text.tag_add(f"{etf}_low", start_low_idx, end_low_days_adj)
                left_text.tag_configure(f"{etf}_low", background="green", foreground="white", font=("TkDefaultFont", 10, "bold"))

        left_text.insert(tk.END, "\n")

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

    # Add USFR peak estimate output
    display_usfr_peak_estimate()

def run_usfr_low_summary():
    try:
        df = run_usfr_post_peak_lows()
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

def run_usfr_full_cycles_gui():
    try:
        df = run_usfr_full_cycles()
        if df.empty:
            messagebox.showinfo("No Data", "No valid USFR full cycles found.")
            return
        row = df.iloc[-1]
        msg = (
            f"📈 USFR Full Cycle:\n"
            f"Low Date: {row['Low_Date']} @ ${row['Low']:.2f}\n"
            f"Peak Date: {row['Peak_Date']} @ ${row['Peak']:.2f}\n"
            f"Gain: {row['Gain_%']}%\n"
            f"Signal Strength: {row.get('Peak_Signal_Strength', 'N/A')}%\n"
            f"Cycle Complete: {row['Cycle_Complete']}"
        )
        right_text.insert(tk.END, "\n" + msg + "\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run USFR full cycle analysis:\n{e}")

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
tk.Button(button_frame, text="📈 USFR Full Cycles", command=run_usfr_full_cycles_gui, bg="lavender").pack(side="left", padx=5)

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
    main()
