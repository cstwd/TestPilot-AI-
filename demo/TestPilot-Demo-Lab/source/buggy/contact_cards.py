def extension_label(number: str, extension: str) -> str:
    """Render a contact number with an optional extension."""
    return f'{number} x{extension}'

def initial_badge(name: str) -> str:
    """Use the first visible character of the contact name."""
    return name[:1].upper()
