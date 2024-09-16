import datetime

import babel.dates

# For Python 3.9+, use zoneinfo
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # For Python <3.9, use pytz
    import pytz


# Custom filter function
def format_datetime(value: datetime.datetime, desired_format="medium"):
    # Convert the datetime to Paris timezone
    try:
        paris_tz = ZoneInfo("Europe/Paris")
        value = value.astimezone(paris_tz)
    except NameError:
        # If zoneinfo is not available, use pytz
        paris_tz = pytz.timezone("Europe/Paris")
        value = value.astimezone(paris_tz)

    # Format the datetime using Babel with French locale
    return babel.dates.format_datetime(value, format=desired_format, locale="fr_FR")
