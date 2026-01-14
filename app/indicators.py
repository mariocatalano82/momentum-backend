def compute_probability(change_24h: float) -> float:
    val = abs(change_24h)
    if val >= 50:
        return 95.0
    if val >= 30:
        return 90.0
    if val >= 15:
        return 80.0
    return 65.0


def build_chart_data(change_1h: float):
    step = change_1h / 12
    return [step * i for i in range(1, 13)]
