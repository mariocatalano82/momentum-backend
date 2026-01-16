from datetime import datetime, timezone
from app.datasources import fetch_market_data
from app.indicators import compute_confidence, build_chart, tech_context


_LAST_VALID_STATE = None


def build_state(profile: str):
    global _LAST_VALID_STATE

    try:
        raw, fallback = fetch_market_data()
    except Exception:
        if _LAST_VALID_STATE:
            return {**_LAST_VALID_STATE, "fallback": True}
        raise

    assets = []
    for a in raw:
        try:
            symbol = a["symbol"]
            name = a.get("symbol")
            ch1 = float(a.get("priceChangePercent", 0)) / 24
            ch24 = float(a.get("priceChangePercent", 0))

            conf = compute_confidence(ch1, ch24, profile)

            assets.append({
                "symbol": symbol,
                "name": name,
                "change_1h": round(ch1, 1),
                "change_24h": round(ch24, 1),
                "score": round(ch24, 1),
                "probability": conf,
                "chart_data": build_chart(ch1),
                "explanation": (
                    "Momentum remains constructive, though volatility may rise."
                    if conf > 55 else
                    "Momentum is present but lacks strong conviction."
                ),
                "tech": tech_context(ch1, ch24)
            })
        except Exception:
            continue

    ups = sorted(assets, key=lambda x: x["score"], reverse=True)[:5]
    downs = sorted(assets, key=lambda x: x["score"])[:5]

    state = {
        "profile": profile,
        "fallback": fallback,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "last_valid_up": ups,
        "last_valid_down": downs
    }

    _LAST_VALID_STATE = state
    return state
