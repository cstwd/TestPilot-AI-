def pack(values: list[int]) -> list[list[int]]:
    """Encode adjacent equal values as value/count records."""
    packed = []
    for value in values:
        if packed and packed[-1][0] == value:
            packed[-1][1] += 1
        else:
            packed.append([value, 1])
    return packed

def unpack(records: list[list[int]]) -> list[int]:
    """Expand value/count records into the corresponding sequence."""
    return [value for value, count in records for _ in range(count)]
