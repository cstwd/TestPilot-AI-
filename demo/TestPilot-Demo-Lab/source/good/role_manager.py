def active_labels(roles: dict[str, bool]) -> list[str]:
    """List labels marked active, in lexical order.

    >>> active_labels({'B': False, 'A': True})
    ['A']
    """
    return sorted(name for name, active in roles.items() if active)

def label_summary(roles: dict[str, bool]) -> str:
    """Render active role labels for display."""
    return ', '.join(active_labels(roles))
