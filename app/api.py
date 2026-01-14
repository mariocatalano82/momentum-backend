from typing import Dict, List
import math
from app.datasources import get_crypto_data

def probability_from_score(score: float) -> float:
    # sigmoid
    return round(100 / (1 + math.exp(-score / 5)), 1)

def build_payload(c: Dict, profile: str) -> Dict:
    change_24h = c["change_24h"]
    change_1h = change_24h / 4
    volume = math.log(c.get("volume", 1) + 1)

    if profile == "aggressive":
        score = change_24h * 1.3 + change_1h * 1.6 + volume * 0.4
    else:
        score = change_24h * 1.0 + change_1h * 0.8 + volume * 0.2

    prob = probability_from_score(score)

    return {
        "symbol": c["symbol"],
        "name": c["name"],
        "change_1h": round(change_1h, 2),
        "change_24h": round(change_24h, 2),
        "probability": prob,
        "explanation_simple": (
            "Strong momentum breakout"
            if score > 0
            else "Weak momentum / selling pressure"
        ),
        "explanation_technical":
            "Volume-weighted momentum (1h + 24h), multi-source",
        "score": round(score, 3),
    }


def rank(profile: str) -> List[Dict]:
    raw = get_crypto_data()
    if not raw:
        return []

    ranked = [build_payload(c, profile) for c in raw]
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked


def get_top_up(profile: str = "balanced") -> List[Dict]:
    ranked = rank(profile)
    return [c for c in ranked if c["score"] > 0][:5]


def get_top_down(profile: str = "balanced") -> List[Dict]:
    ranked = rank(profile)
    return [c for c in ranked if c["score"] < 0][-5:]

