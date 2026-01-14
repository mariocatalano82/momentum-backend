def compute_probability(coin, profile):
    base = abs(coin["change_24h"]) * 2
    return min(95, base + (10 if profile == "aggressive" else 0))

def compute_acceleration(coin):
    return abs(coin["change_24h"] / 24) * 1.5
