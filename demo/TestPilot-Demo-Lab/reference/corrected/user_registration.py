def pending_labels(names: list[str]) -> list[str]:
    """Deduplicate synthetic signup names while preserving first appearance."""
    return list(dict.fromkeys(names))

def invitation_slots(limit: int, pending: int) -> int:
    """Return nonnegative unreserved invitation slots."""
    return max(0, limit - pending)
