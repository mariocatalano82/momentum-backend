from typing import Dict, List
from app.datasources import get_market_snapshot
from app.indicators import compute_probability, compute_acceleration

def enrich_coin(coin: Dict, profile: str) -> Dict:
    prob = compute_probability(coin, profile)
    accel = compute_acceleration(coin)

    explanation = (
        "High probability of trend continuation in the next 2 hours."
        if prob > 80 else
        "Momentum weakening, consolidation likely."
    )

    return {
        "symbol": coin["symbol"],
        "name": coin["name"],
        "price_change_1h": coin["change_1h"],
        "price_change_24h": coin["change_24h"],
        "probability": round(prob, 2),
        "acceleration": round(accel, 2),
        "explanation": explanation,
        "chart_data": coin.get("chart_data", []),
    }

def build_market_state(profile: str) -> Dict:
    up, down = get_market_snapshot()

    return {
        "profile": profile,
        "last_valid_up": [enrich_coin(c, profile) for c in up],
        "last_valid_down": [enrich_coin(c, profile) for c in down],
    }
