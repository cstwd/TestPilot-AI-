def reachable(edges: dict[str, list[str]], start: str) -> list[str]:
    """Return the sorted reachable vertex set including start."""
    seen, pending = {start}, [start]
    while pending:
        for node in edges.get(pending.pop(), []):
            if node not in seen:
                seen.add(node)
                pending.append(node)
    return sorted(seen)

def incoming(edges: dict[str, list[str]], target: str) -> int:
    """Count vertices with a direct edge incoming to target."""
    return sum(target in destinations for destinations in edges.values())
