def advance(status: str, event: str) -> str:
    """Apply pay, pack or deliver in the stated order."""
    transitions = {('new','pay'):'paid', ('paid','pack'):'packed', ('packed','deliver'):'delivered'}
    return transitions[(status,event)]

def replay(events: list[str]) -> str:
    """Replay events starting with a new order."""
    status = 'new'
    for event in events:
        status = advance(status, event)
    return status
