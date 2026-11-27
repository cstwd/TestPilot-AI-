def diagonal_sum(matrix: list[list[int]]) -> int:
    """Sum the main diagonal of a square matrix."""
    return sum(row[i] for i, row in enumerate(matrix))

def multiply_vector(matrix: list[list[int]], vector: list[int]) -> list[int]:
    """Multiply a matrix by a column vector of matching width."""
    return [sum(a * b for a, b in zip(row, vector, strict=True)) for row in matrix]
