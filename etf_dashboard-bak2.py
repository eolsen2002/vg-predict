"""
etf_dashboard.py

A Tkinter-based GUI application to monitor selected Treasury ETFs and their
upcoming Peak and Low signals. Includes data refresh capability, countdowns,
and live peak signal scores for 6 ETFs (USFR, SGOV, TFLO, BIL, SHV, ICSH).

Updated 6/14/25,7:45 am
- Peak info now displayed before Low info
- All ETF peak signal scores shown on right
- Refined green highlight formatting
"""

import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
from datetime import datetime, date

from analysis.usfr_peak_signal import get_usfr_peak_signal
from scripts.peak_signal_score import get_all_peak_scores
from scripts.analyze_signals import check_etf_signal_with_countdown

ETFS = ['USFR', 'SGOV', 'BIL', 'SHV', 'TFLO', 'ICSH']
SIGNALS = ['Low', 'Peak', 'Both']

def run_analysis():
    selected_etfs = [etf for etf in ETFS if etf_vars[etf].get()]
    selected_signal = signal_type.get()
    left_text.delete("1.0", tk.END)
    right_text.delete("1.0", tk.END)

    if not selected_etfs:
        messagebox.showwarning("No ETF Selected", "Please select at least one ETF.")
        return

    today = date.today()
    left_text.insert(tk.END, f"\U0001F4C6 Today: {today}\n\n")

    low_days_list = []
    peak_days_list = []
    low_info_dict = {}
    peak_info_dict = {}

    for etf in selected_etfs:
        if selected_signal in ["Peak", "Both"]:
            peak_info = check_etf_signal_with_countdown(etf, "Peak")
            peak_info_dict[etf] = peak_info
            peak_days_list.append(peak_info['days_until'])
        if selected_signal in ["Low", "Both"]:
            low_info = check_etf_signal_with_countdown(etf, "Low")
            low_info_dict[etf] = low_info
            low_days_list.append(low_info['days_until'])

    min_peak_days = min(peak_days_list) if peak_days_list else None
    min_low_days = min(low_days_list) if low_days_list else None

    for etf in selected_etfs:
        # PEAK info first
        if selected_signal in ["Peak", "Both"]:
            peak_info = peak_info_dict.get(etf)
            if peak_info:
                left_text.insert(tk.END, f"\U0001F50D Checking PEAK signal for {etf}...\n")
                left_text.insert(tk.END, peak_info['text'] + "\n")
                tag = f"{etf}_peak"
                left_text.insert(tk.END, f"Days until next peak: {peak_info['days_until']}\n", tag)
                left_text.insert(tk.END, "\n")  # spacing
                if peak_info['days_until'] == min_peak_days:
                    left_text.tag_configure(tag, background="green", foreground="white", font=("TkDefaultFont", 10, "bold"))
                else:
                    left_text.tag_configure(tag, background="white", foreground="black", font=("TkDefaultFont", 10, "normal"))

        # LOW info second
        if selected_signal in ["Low", "Both"]:
            low_info = low_info_dict.get(etf)
            if low_info:
                left_text.insert(tk.END, f"\U0001F50D Checking LOW signal for {etf}...\n")
                left_text.insert(tk.END, low_info['text'] + "\n")
                tag = f"{etf}_low"
                left_text.insert(tk.END, f"Days until next low: {low_info['days_until']}\n", tag)
                left_text.insert(tk.END, "\n")  # spacing
                if low_info['days_until'] == min_low_days:
                    left_text.tag_configure(tag, background="green", foreground="white", font=("TkDefaultFont", 10, "bold"))
                else:
                    left_text.tag_configure(tag, background="white", foreground="black", font=("TkDefaultFont", 10, "normal"))

    # Right side: Live peak signal scores
    right_text.insert(tk.END, "\U0001F4C8 Live ETF Peak Signal Scores:\n\n")
    peak_scores = get_all_peak_scores()

    for etf in ['USFR'] + [e for e in ETFS if e != 'USFR']:
        if etf == "USFR":
            usfr_score = get_usfr_peak_signal()
            if usfr_score:
                right_text.insert(tk.END, f"{etf} — Score: {usfr_score['score']} | {usfr_score['message']} | {usfr_score['price']}\n")
        else:
            data = peak_scores.get(etf)
            if data:
                right_text.insert(tk.END, f"{etf} — Score: {data['score']} | {data['message']} | {data['price']}\n")

def refresh_data():
    """Runs ETF data fetch script and updates timestamp."""
    try:
        subprocess.run(["python", "scripts/fetch_etf_data.py"], check=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_updated_label.config(text=f"Last data refresh: {timestamp} (latest data available)")
        messagebox.showinfo("Success", "ETF data refreshed successfully.")
    except Exception as e:
        last_updated_label.config(text=f"Last data refresh failed: {e}")
        messagebox.showerror("Error", f"Failed to refresh data:\n{e}")

def refresh_data_background():
    """Runs refresh_data() in a background thread."""
    threading.Thread(target=refresh_data, daemon=True).start()

def auto_refresh_on_startup():
    """Refresh data automatically on GUI launch."""
    def _refresh_and_update_label():
        try:
            subprocess.run(["python", "scripts/fetch_etf_data.py"], check=True)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            last_updated_label.config(text=f"Last data refresh: {timestamp} (latest data available)")
        except Exception as e:
            last_updated_label.config(text=f"Auto refresh failed: {e}")
    threading.Thread(target=_refresh_and_update_label, daemon=True).start()

# ===== GUI Layout =====
root = tk.Tk()
root.title("ETF Signal Dashboard")
root.geometry("1000x600")

# ETF checkbox panel
etf_frame = tk.LabelFrame(root, text="Select ETFs")
etf_frame.pack(fill="x", padx=10, pady=5)

etf_vars = {}
for etf in ETFS:
    var = tk.BooleanVar(value=True)
    etf_vars[etf] = var
    tk.Checkbutton(etf_frame, text=etf, variable=var).pack(side="left", padx=5)

# Signal type radio buttons
signal_frame = tk.LabelFrame(root, text="Signal Type")
signal_frame.pack(fill="x", padx=10, pady=5)

signal_type = tk.StringVar(value="Both")
for sig in SIGNALS:
    tk.Radiobutton(signal_frame, text=sig, variable=signal_type, value=sig).pack(side="left", padx=5)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(fill="x", padx=10, pady=5)

tk.Button(button_frame, text="\U0001F504 Refresh Data", command=refresh_data_background, bg="lightgreen").pack(side="left", padx=5)
tk.Button(button_frame, text="\U0001F504 Refresh Signals", command=run_analysis, bg="lightblue").pack(side="left", padx=5)

# Timestamp
last_updated_label = tk.Label(root, text="Last data refresh: never")
last_updated_label.pack(pady=5)

# Output split pane
output_frame = tk.Frame(root)
output_frame.pack(fill="both", expand=True, padx=10, pady=5)

left_text = tk.Text(output_frame, wrap="word", width=50)
left_text.pack(side="left", fill="both", expand=True)

right_text = tk.Text(output_frame, wrap="word", width=50, bg="#f0f8ff")
right_text.pack(side="right", fill="both")

root.after(100, auto_refresh_on_startup)
root.mainloop()
