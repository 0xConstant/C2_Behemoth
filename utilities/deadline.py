def format_date(expiration_date):
    # Convert the date to a human-readable format
    formatted_date = expiration_date.strftime('%I:%M %p - %B %d')
    formatted_date = formatted_date.replace(' 0', ' ') # Remove leading zeros from day

    # Add the ordinal suffix to the day
    day = expiration_date.day
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

    formatted_date = formatted_date.replace(str(day), f'{day}{suffix}')

    return formatted_date
