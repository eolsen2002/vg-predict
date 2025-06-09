# gui_dashboard.py
import tkinter as tk
from tkinter import ttk, messagebox
from scripts.analyze_signals import check_etf_signal
import datetime

ETFS = ['USFR', 'SGOV', 'BIL', 'SHV', 'TFLO', 'ICSH']
SIGNALS = ['Low', 'Peak', 'Both']

def run_analysis():
    selected_etfs = [etf for etf in ETFS if etf_vars[etf].get()]
    selected_signal = signal_type.get()
    output_text.delete("1.0", tk.END)

    if not selected_etfs:
        messagebox.showwarning("No ETF Selected", "Please select at least one ETF.")
        return

    today = datetime.date.today()
    output_text.insert(tk.END, f"📆 Today: {today}\n\n")

    for etf in selected_etfs:
        if selected_signal in ["Low", "Both"]:
            output_text.insert(tk.END, f"🔍 Checking LOW signal for {etf}...\n")
            result = check_etf_signal(etf, "Low")
            output_text.insert(tk.END, result + "\n\n")

        if selected_signal in ["Peak", "Both"]:
            output_text.insert(tk.END, f"🔍 Checking PEAK signal for {etf}...\n")
            result = check_etf_signal(etf, "Peak")
            output_text.insert(tk.END, result + "\n\n")

# GUI Layout
root = tk.Tk()
root.title("ETF Signal Dashboard")
root.geometry("800x600")

# ETF checkboxes
etf_frame = tk.LabelFrame(root, text="Select ETFs")
etf_frame.pack(fill="x", padx=10, pady=5)

etf_vars = {}
for etf in ETFS:
    etf_vars[etf] = tk.BooleanVar()
    tk.Checkbutton(etf_frame, text=etf, variable=etf_vars[etf]).pack(side="left", padx=5)

# Signal type radio buttons
signal_frame = tk.LabelFrame(root, text="Signal Type")
signal_frame.pack(fill="x", padx=10, pady=5)

signal_type = tk.StringVar(value="Both")
for sig in SIGNALS:
    tk.Radiobutton(signal_frame, text=sig, variable=signal_type, value=sig).pack(side="left", padx=5)

# Refresh button
tk.Button(root, text="🔄 Refresh Signals", command=run_analysis, bg="lightblue").pack(pady=10)

# Output Text Area
output_frame = tk.Frame(root)
output_frame.pack(fill="both", expand=True, padx=10, pady=5)

output_text = tk.Text(output_frame, wrap="word")
output_text.pack(fill="both", expand=True)

root.mainloop()

