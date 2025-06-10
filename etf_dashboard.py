""""
etf_dashboard.py

A Tkinter-based GUI application to monitor selected Treasury ETFs and their
upcoming Low and Peak signals. Allows users to refresh ETF price data,
select ETFs and signal types (Low, Peak, or Both), and view countdowns to
the next significant signal date with visual highlights. Supports
background data fetching and provides real-time status updates.
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import calendar
from datetime import datetime, date  # clean import

from scripts.analyze_signals import check_etf_signal_with_countdown, get_valid_peak_date

ETFS = ['USFR', 'SGOV', 'BIL', 'SHV', 'TFLO', 'ICSH']
SIGNALS = ['Low', 'Peak', 'Both']

def run_analysis():
    selected_etfs = [etf for etf in ETFS if etf_vars[etf].get()]
    selected_signal = signal_type.get()
    output_text.delete("1.0", tk.END)

    if not selected_etfs:
        messagebox.showwarning("No ETF Selected", "Please select at least one ETF.")
        return

    today = date.today()
    output_text.insert(tk.END, f"📆 Today: {today}\n\n")

    low_days_list = []
    peak_days_list = []
    low_info_dict = {}
    peak_info_dict = {}

    for etf in selected_etfs:
        if selected_signal in ["Low", "Both"]:
            low_info = check_etf_signal_with_countdown(etf, "Low")
            low_info_dict[etf] = low_info
            low_days_list.append(low_info['days_until'])
        if selected_signal in ["Peak", "Both"]:
            peak_info = check_etf_signal_with_countdown(etf, "Peak")
            peak_info_dict[etf] = peak_info
            peak_days_list.append(peak_info['days_until'])

    min_low_days = min(low_days_list) if low_days_list else None
    min_peak_days = min(peak_days_list) if peak_days_list else None

    for etf in selected_etfs:
        if selected_signal in ["Low", "Both"]:
            low_info = low_info_dict.get(etf)
            if low_info:
                output_text.insert(tk.END, f"🔍 Checking LOW signal for {etf}...\n")
                output_text.insert(tk.END, low_info['text'] + "\n")
                tag = f"{etf}_low"
                output_text.insert(tk.END, f"Days until next low: {low_info['days_until']}\n\n", tag)
                if low_info['days_until'] == min_low_days:
                    output_text.tag_configure(tag, foreground="white", background="green", font=("TkDefaultFont", 10, "bold"))
                else:
                    output_text.tag_configure(tag, foreground="black", background="white", font=("TkDefaultFont", 10, "normal"))

        if selected_signal in ["Peak", "Both"]:
            peak_info = peak_info_dict.get(etf)
            if peak_info:
                output_text.insert(tk.END, f"🔍 Checking PEAK signal for {etf}...\n")
                output_text.insert(tk.END, peak_info['text'] + "\n")
                tag = f"{etf}_peak"
                output_text.insert(tk.END, f"Days until next peak: {peak_info['days_until']}\n\n", tag)
                if peak_info['days_until'] == min_peak_days:
                    output_text.tag_configure(tag, foreground="white", background="green", font=("TkDefaultFont", 10, "bold"))
                else:
                    output_text.tag_configure(tag, foreground="black", background="white", font=("TkDefaultFont", 10, "normal"))

def refresh_data():
    try:
        subprocess.run(["python", "scripts/fetch_etf_data.py"], check=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_updated_label.config(text=f"Last data refresh: {timestamp} (latest data available)")
        messagebox.showinfo("Success", "ETF data refreshed successfully.")
    except Exception as e:
        last_updated_label.config(text=f"Last data refresh failed: {e}")
        messagebox.showerror("Error", f"Failed to refresh data:\n{e}")

def refresh_data_background():
    threading.Thread(target=refresh_data, daemon=True).start()

def auto_refresh_on_startup():
    def _refresh_and_update_label():
        try:
            subprocess.run(["python", "scripts/fetch_etf_data.py"], check=True)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_updated_label.config(text=f"Last data refresh: {timestamp} (latest data available)")
        except Exception as e:
            last_updated_label.config(text=f"Auto refresh failed: {e}")
    threading.Thread(target=_refresh_and_update_label, daemon=True).start()

# ========== GUI Setup ==========
root = tk.Tk()
root.title("ETF Signal Dashboard")
root.geometry("800x600")

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

refresh_data_btn = tk.Button(button_frame, text="🔄 Refresh Data", command=refresh_data_background, bg="lightgreen")
refresh_data_btn.pack(side="left", padx=5)

refresh_signals_btn = tk.Button(button_frame, text="🔄 Refresh Signals", command=run_analysis, bg="lightblue")
refresh_signals_btn.pack(side="left", padx=5)

last_updated_label = tk.Label(root, text="Last data refresh: never")
last_updated_label.pack(pady=5)

output_frame = tk.Frame(root)
output_frame.pack(fill="both", expand=True, padx=10, pady=5)

output_text = tk.Text(output_frame, wrap="word")
output_text.pack(fill="both", expand=True)

root.after(100, auto_refresh_on_startup)

root.mainloop()
