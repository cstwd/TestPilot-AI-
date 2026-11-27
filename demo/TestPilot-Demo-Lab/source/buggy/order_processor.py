def packing_slip(lines: list[list]) -> list[str]:
    """List SKUs for all positive quantity lines in source order."""
    return [sku for sku, quantity in lines if quantity >= 0]

def parcel_count(total_items: int, capacity: int) -> int:
    """Use as many full or partial parcels as needed."""
    return total_items // capacity
