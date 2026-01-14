from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import time
import math
from app import datasources

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CACHE_TTL = 120
_last_fetch = 0
_cache = {
    "balanced": {"up": [], "down": []},
    "aggressive": {"up": [], "down": []},
}

def momentum_score(c, profile):
    change_24h = c["change_24h"]
    change_1h = change_24h / 4
    volume = c.get("volume", 1)

    # pesi
    if profile == "aggressive":
        w24, w1, wv = 1.2, 1.5, 0.4
    else:
        w24, w1, wv = 1.0, 0.8, 0.2

    return (
        change_24h * w24 +
        change_1h * w1 +
        math.log(volume + 1) * wv
    )

def explanation(score, profile):
    if score > 0:
        return (
            "Strong momentum breakout"
            if profile == "aggressive"
            else "Sustained positive momentum"
        )
    return (
        "Sharp downside pressure"
        if profile == "aggressive"
        else "Weak momentum, consolidation risk"
    )

def refresh(profile):
    global _last_fetch, _cache
    now = time.time()
    if now - _last_fetch < CACHE_TTL:
        return

    raw = datasources.get_crypto_data()
    results = []

    for c in raw:
        score = momentum_score(c, profile)
        prob = min(95, max(30, abs(score)))

        results.append({
            "symbol": c["symbol"],
            "name": c["name"],
            "change_1h": round(c["change_24h"] / 4, 2),
            "change_24h": round(c["change_24h"], 2),
            "probability": round(prob, 1),
            "explanation_simple": explanation(score, profile),
            "explanation_technical":
                "Momentum score (1h + 24h + volume, Binance)",
            "score": round(score, 3),
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    _cache[profile]["up"] = [r for r in results if r["score"] > 0][:5]
    _cache[profile]["down"] = [r for r in results if r["score"] < 0][-5:]
    _last_fetch = now

@app.get("/ranking/up")
def ranking_up(profile: str = Query("balanced")):
    refresh(profile)
    return _cache[profile]["up"]

@app.get("/ranking/down")
def ranking_down(profile: str = Query("balanced")):
    refresh(profile)
    return _cache[profile]["down"]

@app.get("/healthz")
def healthz():
    return {"ok": True}
