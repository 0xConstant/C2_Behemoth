import datetime

def human_readable_date(dt):
    # Get the current date and time
    now = datetime.datetime.now(dt.tzinfo)

    # Find the difference between now and the provided datetime
    diff = now - dt

    # Calculate the time difference
    minutes_diff = diff.total_seconds() / 60

    if minutes_diff < 1:
        time_ago = "just now"
    elif minutes_diff < 60:
        time_ago = f"{int(minutes_diff)} minute{'s' if int(minutes_diff) != 1 else ''} ago"
    elif minutes_diff < 1440:
        time_ago = f"{int(minutes_diff / 60)} hour{'s' if int(minutes_diff / 60) != 1 else ''} ago"
    else:
        time_ago = f"{int(minutes_diff / 1440)} day{'s' if int(minutes_diff / 1440) != 1 else ''} ago"

    # Formatting the day with suffix (1st, 2nd, 3rd, etc.)
    day = dt.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]

    formatted_date = dt.strftime(f"%A, %B {day}{suffix}, %Y")

    return f"{formatted_date} ({time_ago})"
