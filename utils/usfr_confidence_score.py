# utils/usfr_peak_confidence_score.py
def check_against_ex_date(modal_peak_date, distribution_dates):
    """
    Compares the modal peak date (from price history) against ex-dates from PDF.
    Returns one of: "GREEN", "YELLOW", "RED"
    """
    if not modal_peak_date or not distribution_dates:
        return "RED"

    modal_month = modal_peak_date.month
    modal_day = modal_peak_date.day

    for dist in distribution_dates:
        if dist["ex_date"].month == modal_month:
            delta = abs((dist["ex_date"] - modal_peak_date).days)
            if delta <= 1:
                return "GREEN"
            elif delta <= 3:
                return "YELLOW"
            else:
                return "RED"

    return "RED"
