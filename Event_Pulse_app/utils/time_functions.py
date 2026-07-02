from datetime import datetime, timedelta, date


def default_start_date() -> date:
    return datetime.today().date()

def default_end_date(start_date: date) -> date:
    return start_date + timedelta(days=365)

