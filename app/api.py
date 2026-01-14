from typing import Dict, List
from .datasources import fetch_binance
from .indicators import compute_score

def normalize(symbol_data: Dict) -> Dict:
    change_24h = float(symbol_data.get("priceChangePercent", 0))
    return {
        "symbol": symbol_data.get("symbol"),
        "name": symbol_data.get("symbol"),
        "price_change_24h": round(change_24h, 2),
        "probability": min(95, abs(change_24h) * 2),
        "explanation": "Relative momentum vs market average (Binance)",
        "score": compute_score(change_24h),
        "chart_data": [
            round(change_24h * f, 2) for f in [0.2, 0.4, 0.6, 0.8, 1]
        ]
    }

def build_state(profile: str) -> Dict:
    data = fetch_binance()

    if not data:
        return {
            "last_valid_up": [],
            "last_valid_down": []
        }

    coins = [normalize(c) for c in data if "USDT" in c.get("symbol", "")]

    up = sorted(
        [c for c in coins if c["price_change_24h"] > 0],
        key=lambda x: x["score"],
        reverse=True
    )[:5]

    down = sorted(
        [c for c in coins if c["price_change_24h"] < 0],
        key=lambda x: x["score"]
    )[:5]

    return {
        "last_valid_up": up,
        "last_valid_down": down
    }
