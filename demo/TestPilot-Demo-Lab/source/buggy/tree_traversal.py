def preorder(tree: list | None) -> list[int]:
    """Visit a nested value/left/right tree root first."""
    if tree is None:
        return []
    value, left, right = tree
    return [value] + preorder(right) + preorder(left)

def leaf_count(tree: list | None) -> int:
    """Count nodes with neither child."""
    if tree is None:
        return 0
    _, left, right = tree
    if left is None and right is None:
        return 1
    return max(leaf_count(left), leaf_count(right))
