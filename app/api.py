from datetime import datetime, timezone
from app.datasources import fetch_assets_snapshot
from app.indicators import compute_confidence, build_chart, tech_context
from app.config import TOP_N

def explain(change_1h, change_24h):
    if abs(change_1h) > abs(change_24h) * 0.4:
        return "Momentum is accelerating with increased short-term participation."
    if abs(change_24h) > 8:
        return "Trend remains well established, though volatility may rise."
    return "Momentum is present but lacks strong directional conviction."


def build_state(profile: str):
    assets = fetch_assets_snapshot()
    timestamp = datetime.now(timezone.utc).isoformat()

    enriched = []
    for a in assets:
        conf = compute_confidence(a["change_1h"], a["change_24h"], profile)

        enriched.append({
            "symbol": a["symbol"],
            "name": a["name"],
            "change_1h": a["change_1h"],
            "change_24h": a["change_24h"],
            "score": round(a["change_24h"], 1),
            "probability": conf,
            "chart_data": build_chart(a["change_1h"]),
            "explanation": explain(a["change_1h"], a["change_24h"]),
            "tech": tech_context(a["change_1h"], a["change_24h"]),
        })

    up = sorted([a for a in enriched if a["change_24h"] >= 0],
                key=lambda x: x["score"], reverse=True)[:TOP_N]

    down = sorted([a for a in enriched if a["change_24h"] < 0],
                  key=lambda x: x["score"])[:TOP_N]

    return {
        "profile": profile,
        "fallback": False,
        "timestamp": timestamp,
        "last_valid_up": up,
        "last_valid_down": down
    }
