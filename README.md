# vg-predict

**ETF Swing Timing System for Treasury ETFs (USFR, SGOV, BIL, TFLO, SHV, ICSH)**

This project helps identify monthly **peak sell** and **post-peak low buy** opportunities for short-term Treasury ETFs. It combines historical price analysis, timing logic, and automated signals to support swing trading in tax-advantaged accounts.

---

## 🔁 Strategy Overview

The system targets predictable monthly price patterns:
- **USFR** usually peaks around the 22nd–25th, then drops into month-end.
- **SGOV, BIL, TFLO, SHV, ICSH** tend to peak on the last trading day of the month and bottom early the next month.
- Monthly swing trades rotate profits between these ETFs.

---

## 🧱 Project Structure
This repository is organized to keep data, analysis scripts, generated signals, and reports clearly separated for easy navigation and maintenance.

'data/' holds historical ETF price data in CSV and XLSX formats.

'reports/' contains generated analysis reports and summaries.

'scripts/' includes all core Python scripts for signal generation, rotation analysis, and utilities.

'signals/' stores auto-generated CSV files with ETF peak and low signals used for trading strategies.

Root files include main entry points for the GUI and program execution, along with configuration files like .gitignore and this README.md.

vg-predict/
│
├── data/                       # Historical ETF price data (CSV, XLSX)
│   ├── etf_prices_2023_2025.csv
│   ├── etf_prices_2023_2025.xlsx
│   ├── etf_rotation_backtest.csv
│   └── etf_rotation_backtest.xlsx
│
├── reports/                    # Generated analysis reports
│   └── usfr_report_2025-06-07.txt
│
├── scripts/                    # Core analysis and utility Python scripts
│   ├── analyze_lows.py
│   ├── analyze_peaks.py
│   ├── analyze_rotations.py
│   ├── analyze_signals.py
│   ├── daily_usfr_report.py
│   ├── etf_rotation_backtest.py
│   ├── fetch_etf_data.py
│   ├── generate_low_csvs.py
│   ├── generate_peak_csvs.py
│   ├── is_today_sgov_low.py
│   ├── is_today_usfr_low.py
│   ├── sgov_post_peak_lows.py
│   ├── usfr_post_peak_lows.py
│   └── __init__.py
│
├── signals/                    # Auto-generated ETF signal CSV files
│   ├── bil_post_peak_highs.csv
│   ├── bil_post_peak_lows.csv
│   ├── etf_rotation_analysis_summary.csv
│   ├── icsh_post_peak_highs.csv
│   ├── icsh_post_peak_lows.csv
│   ├── sgov_post_peak_highs.csv
│   ├── sgov_post_peak_lows.csv
│   ├── sgov_post_peak_lows_full.csv
│   ├── shv_post_peak_highs.csv
│   ├── shv_post_peak_lows.csv
│   ├── tflo_post_peak_highs.csv
│   ├── tflo_post_peak_lows.csv
│   ├── usfr_post_peak_highs.csv
│   └── usfr_post_peak_lows.csv
│
├── '.gitignore'                  # Git ignore file
├── 'etf_dashboard.py'            # Main GUI and strategy logic entry point (GUI entry point)
├── 'main.py'                     # Main execution script
├── 'README.md'                   # This README file


## ⚙️ Features

- Rotation performance analyzer (`analyze_rotations.py`)
- Signal generation for peaks and lows per ETF
- Modular design for adding new timing rules or ETFs
- GUI dashboard (WIP) to trigger checks and show signals

---

## 📈 Dependencies

- `pandas`
- `tkinter` (for GUI)
- `matplotlib` (optional for future visuals)

---

## 🗃️ GitHub Usage

This repo helps you:
- Keep files synced between computers
- Avoid USB transfer errors
- Document and evolve your ETF swing timing logic

---

## 🔒 Local Data Handling

Sensitive or local-only files are excluded via `.gitignore`. All trading-related logic and signals are fully reproducible with public ETF data.

---

## ✍️ Maintained by

**Erik Olsen**, investor & ETF strategy researcher  
Initial setup: June 2025

