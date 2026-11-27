def classify_temperature(degrees: int) -> str:
    """Classify a Celsius reading into one of four temperature bands.

    >>> classify_temperature(-1)
    'freezing'
    >>> classify_temperature(0)
    'cold'
    >>> classify_temperature(15)
    'mild'
    >>> classify_temperature(30)
    'hot'
    """
    if degrees < 0:
        return "freezing"
    if degrees < 15:
        return "cold"
    if degrees < 30:
        return "mild"
    return "hot"
