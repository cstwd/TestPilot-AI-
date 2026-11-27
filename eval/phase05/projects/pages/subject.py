from limits import PAGE_SIZE

def page_count(items: int) -> int:
    """Return the number of nonempty pages needed. Zero items need zero pages.

    >>> page_count(9)
    1
    """
    return items // PAGE_SIZE + 1
