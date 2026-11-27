def choose_service(weight: int, rural: bool, express: bool) -> str:
    """Use air for eligible express parcels outside rural routes."""
    if express and not rural and weight <= 20:
        return 'air'
    return 'road'

def route_fee(weight: int, rural: bool, express: bool) -> int:
    """Use a service-specific base plus a rural surcharge."""
    service = choose_service(weight, rural, express)
    return (900 if service == 'air' else 400) + (300 if rural else 0)
