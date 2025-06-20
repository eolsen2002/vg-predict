# utils/usfr_distribution.py
"""
Create a new file utils/usfr_distribution.py with functions:

download_usfr_distribution_pdf()

get_usfr_distribution_dates() (returns list of dicts with ex-date, record-date, payable-date)
"""
import requests
import pdfplumber
from datetime import datetime
import os

PDF_URL = "https://www.wisdomtree.com/investments/-/media/us-media-files/documents/resource-library/fund-reports-schedules/schedule/distribution-schedule.pdf"
LOCAL_PDF = "signals/usfr_distribution_schedule.pdf"  # make sure your folder structure allows this path


def download_usfr_distribution_pdf():
    print(f"Downloading USFR distribution schedule PDF from {PDF_URL} ...")
    r = requests.get(PDF_URL)
    r.raise_for_status()
    with open(LOCAL_PDF, "wb") as f:
        f.write(r.content)
    print(f"Saved PDF to {LOCAL_PDF}")


def safe_strip(val):
    if val is None:
        return ""
    return str(val).strip()


def get_usfr_distribution_dates(download_if_missing=True):
    """
    Returns a list of dicts with distribution dates for USFR:
    [{'ex_date': date, 'record_date': date, 'payable_date': date}, ...]
    """
    if not os.path.exists(LOCAL_PDF) and download_if_missing:
        download_usfr_distribution_pdf()

    dist_dates = []
    try:
        with pdfplumber.open(LOCAL_PDF) as pdf:
            page = pdf.pages[1]  # page 2 is index 1
            tables = page.extract_tables()

            for table in tables:
                if not table or not table[0]:
                    continue
                headers = [safe_strip(h).lower() for h in table[0]]
                if 'ex-date' in headers and 'record date' in headers and 'payable date' in headers:
                    for row in table[1:]:
                        if len(row) < 3:
                            continue
                        ex_str = safe_strip(row[0])
                        rec_str = safe_strip(row[1])
                        pay_str = safe_strip(row[2])
                        try:
                            ex_date = datetime.strptime(ex_str, "%m/%d/%Y").date()
                            record_date = datetime.strptime(rec_str, "%m/%d/%Y").date()
                            payable_date = datetime.strptime(pay_str, "%m/%d/%Y").date()
                            dist_dates.append({
                                "ex_date": ex_date,
                                "record_date": record_date,
                                "payable_date": payable_date
                            })
                        except Exception:
                            continue  # Skip malformed rows
                    break  # stop after first good match
    except Exception as e:
        print(f"Error reading distribution PDF: {e}")

    return dist_dates
