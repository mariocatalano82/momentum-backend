def compute_probability(change_24h: float, profile: str) -> float:
    base = min(abs(change_24h) * 4, 95)

    if profile == "aggressive":
        return min(base + 5, 99)

    return min(base, 95)
