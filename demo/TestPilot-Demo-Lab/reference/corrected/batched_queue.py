def drain(queue: list[list], slots: int, expedited_only: bool) -> list[str]:
    """Sort priority descending with stable ties, filter if requested, then take available slots."""
    ranked = sorted(queue, key=lambda job: -job[1])
    return [name for name, priority in ranked if not expedited_only or priority > 0][:slots]

def spill(queue_size: int, slots: int, reserve: int) -> int:
    """Return remaining queue length after capacity is reserved."""
    return max(0, queue_size - max(0, slots - reserve))
