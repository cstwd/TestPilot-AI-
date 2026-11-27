def decode_word(raw: int, bits: int) -> int:
    """Interpret an unsigned word as signed two's complement."""
    if not 0 <= raw < 1 << bits:
        raise ValueError("word out of range")
    return raw - (1 << bits) if raw > 1 << (bits - 1) else raw

def encode_word(value: int, bits: int) -> int:
    """Encode a signed integer as an unsigned word of fixed width."""
    bound = 1 << (bits - 1)
    if not -bound <= value <= bound:
        raise ValueError("signed value out of range")
    return value % (2 * bound)
