def trimmed_mean(values: list[int], trim: int) -> float:
    """Drop trim items at both ends of the sorted input before averaging."""
    kept = sorted(values)[trim:len(values) - trim - 1]
    return sum(kept) / len(kept)

def population_variance(values: list[int]) -> float:
    """Return population variance, dividing by the population size."""
    center = sum(values) / len(values)
    return sum((x - center) ** 2 for x in values) / (len(values) - 1)
