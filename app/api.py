from datetime import datetime, timezone, timedelta
from app.datasources import fetch_assets_snapshot
from app.indicators import compute_confidence, build_chart, tech_context

# VARIABILI DI CACHE GLOBALI
_cache = {}
CACHE_DURATION = timedelta(minutes=5)

def build_state(profile: str):
    global _cache
    now = datetime.now(timezone.utc)
    
    # Verifica se abbiamo dati freschi in cache per questo profilo
    if profile in _cache:
        data, expiry = _cache[profile]
        if now < expiry:
            return data

    assets = fetch_assets_snapshot()
    enriched = []
    
    for a in assets:
        conf = compute_confidence(a["change_1h"], a["change_24h"], profile)
        enriched.append({
            "symbol": a["symbol"],
            "name": a["name"],
            "change_1h": a["change_1h"],
            "change_24h": a["change_24h"],
            "probability": conf,
            "explanation": explain(a["change_1h"], a["change_24h"]),
            "chart_data": build_chart(a["change_1h"]),
            "tech": tech_context(a["change_1h"], a["change_24h"])
        })

    up = sorted([x for x in enriched if x["change_24h"] >= 0], key=lambda x: abs(x["change_24h"]), reverse=True)[:5]
    down = sorted([x for x in enriched if x["change_24h"] < 0], key=lambda x: abs(x["change_24h"]), reverse=True)[:5]

    result = {
        "profile": profile,
        "timestamp": now.isoformat(),
        "last_valid_up": up,
        "last_valid_down": down
    }
    
    # Aggiorna la cache
    _cache[profile] = (result, now + CACHE_DURATION)
    return result

def explain(c1h, c24h):
    if abs(c1h) > abs(c24h) * 0.4: return "Forte spinta nell'ultima ora."
    if abs(c24h) > 8: return "Trend consolidato nelle 24h."
    return "Movimento moderato."