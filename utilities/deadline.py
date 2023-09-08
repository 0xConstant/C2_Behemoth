def format_date(expiration_date):
    """
    This function returns a human-readable date that's going to be used to show the deadline.
    :param expiration_date:
    :return:
    """
    day_str = expiration_date.strftime('%d').lstrip('0')  # Extract day without leading zero
    time_str = expiration_date.strftime('%I:%M %p')  # Extract time
    rest_of_date = expiration_date.strftime('%A - %B')  # Extract day name and month

    # Append the correct ordinal suffix to the day
    day = int(day_str)
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

    day_str += suffix
    year = expiration_date.strftime('%Y')  # Extract year

    return f"{time_str}, {rest_of_date} {day_str} {year}"
