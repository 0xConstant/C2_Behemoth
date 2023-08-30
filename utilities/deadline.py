def format_date(expiration_date):
    """
    This function returns a human readable date that's going to be used in Agent.
    :param expiration_date:
    :return:
    """
    formatted_date = expiration_date.strftime('%I:%M %p - %B %d')
    formatted_date = formatted_date.replace(' 0', ' ')
    day = expiration_date.day
    if 10 <= day % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

    formatted_date = formatted_date.replace(str(day), f'{day}{suffix}')

    return formatted_date
