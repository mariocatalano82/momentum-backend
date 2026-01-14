from fastapi import APIRouter, Query
from typing import List, Dict
from app.datasources import get_crypto_data
from app.indicators import compute_probability
import random

router = APIRouter(prefix="/ranking", tags=["ranking"])


def build_chart_data(change_24h: float) -> List[float]:
    # sparkline sintetica coerente (NO CoinGecko)
    base = max(min(change_24h / 10, 5), -5)
    return [round(base + random.uniform(-0.5, 0.5), 2) for _ in range(20)]


def build_payload(coin: Dict) -> Dict:
    probability = compute_probability(coin["change_24h"])
    return {
        "symbol": coin["symbol"],
        "name": coin.get("name", coin["symbol"]),
        "price_change_24h": round(coin["change_24h"], 2),
        "probability": probability,
        "explanation": "Relative momentum vs market average (Binance)",
        "chart_data": build_chart_data(coin["change_24h"]),
    }


@router.get("/state")
def ranking_state(profile: str = Query("balanced")):
    data = get_crypto_data()

    up = sorted(
        [c for c in data if c["change_24h"] > 0],
        key=lambda x: x["change_24h"],
        reverse=True,
    )[:5]

    down = sorted(
        [c for c in data if c["change_24h"] < 0],
        key=lambda x: x["change_24h"],
    )[:5]

    return {
        "profile": profile,
        "last_valid_up": [build_payload(c) for c in up],
        "last_valid_down": [build_payload(c) for c in down],
    }
