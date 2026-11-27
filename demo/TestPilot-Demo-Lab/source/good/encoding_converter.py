def as_hex(text: str) -> str:
    """Encode text as UTF-8 and represent its bytes in lowercase hex."""
    return text.encode('utf-8').hex()

def from_hex(encoded: str) -> str:
    """Decode UTF-8 text from a hex representation."""
    return bytes.fromhex(encoded).decode('utf-8')
