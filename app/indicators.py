import hashlib
from datetime import datetime
from app.config import CONFIDENCE_MIN, CONFIDENCE_MAX, PROFILES


def _deterministic_seed(symbol: str) -> float:
    h = hashlib.md5(symbol.encode()).hexdigest()
    return (int(h[:8], 16) % 1000) / 1000.0


def compute_confidence(change_1h, change_24h, profile):
    profile_cfg = PROFILES.get(profile, PROFILES["balanced"])

    alignment = abs(change_1h / change_24h) if change_24h != 0 else 0
    base = 50 + min(alignment * 30, 30)

    seed = _deterministic_seed(str(change_1h) + str(change_24h))
    noise = (seed - 0.5) * 10

    conf = base + noise + profile_cfg["confidence_bias"]
    return round(max(CONFIDENCE_MIN, min(CONFIDENCE_MAX, conf)), 1)


def build_chart(change_1h):
    step = change_1h / 12 if change_1h != 0 else 0
    return [round(step * i, 2) for i in range(1, 13)]


def tech_context(change_1h, change_24h):
    bias = "bullish" if change_24h > 0 else "bearish"

    strength = (
        "strong" if abs(change_24h) > 10 else
        "moderate" if abs(change_24h) > 5 else
        "weak"
    )

    outlook = (
        "Continuation likely if momentum holds."
        if abs(change_1h) > abs(change_24h) * 0.1
        else "Momentum fragile, watch for slowdown."
    )

    return {
        "bias": bias,
        "trend_strength": strength,
        "momentum_state": "stable",
        "risk_level": "medium",
        "outlook_2h": outlook
    }
