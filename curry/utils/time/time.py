import datetime


def convert_period_to_wrapping_months(start_datetime: datetime.datetime, end_datetime: datetime.datetime):
    """Take a period (t0,t1) and return a list of months containing this period, [(m0,m1),(m1,m2),...(mn-1,mn)])"""
    periods = []
    current_datetime = start_datetime
    while current_datetime <= end_datetime:
        month_start = current_datetime.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (month_start + datetime.timedelta(days=32)).replace(day=1)

        periods.append((month_start, next_month))
        # Move to the next month
        current_datetime = next_month
    return periods


def convert_month_to_str(month_start: datetime.datetime):
    return f"{month_start.strftime('%Y-%m')}"
