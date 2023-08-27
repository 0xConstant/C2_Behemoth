import datetime


def human_readable_date(dt):
    now = datetime.datetime.now(dt.tzinfo)
    diff = now - dt
    minutes_diff = diff.total_seconds() / 60

    if minutes_diff < 1:
        time_ago = "just now"
    elif minutes_diff < 60:
        time_ago = f"{int(minutes_diff)} minute{'s' if int(minutes_diff) != 1 else ''} ago"
    elif minutes_diff < 1440:
        time_ago = f"{int(minutes_diff / 60)} hour{'s' if int(minutes_diff / 60) != 1 else ''} ago"
    else:
        time_ago = f"{int(minutes_diff / 1440)} day{'s' if int(minutes_diff / 1440) != 1 else ''} ago"

    day = dt.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]

    formatted_date = dt.strftime(f"%A, %B {day}{suffix}, %Y")

    return f"{formatted_date} ({time_ago})"
