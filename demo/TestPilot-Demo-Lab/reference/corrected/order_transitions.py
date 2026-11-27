def next_state(current: str, action: str, balance: int) -> str:
    """Accept dispatch only for packed and fully paid orders."""
    if action == 'dispatch' and current == 'packed' and balance == 0:
        return 'shipped'
    return current

def can_cancel(current: str, refunded: bool) -> bool:
    """Cancel new orders, or packed orders after refund."""
    return current == 'new' or (current == 'packed' and refunded)
