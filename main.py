from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import time
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
_cached = {
    "balanced": {"up": [], "down": []},
    "aggressive": {"up": [], "down": []},
}

def explain(change, profile):
    if profile == "aggressive":
        return (
            "High momentum breakout with elevated volatility"
            if change > 0
            else "Sharp downside momentum, risk-heavy move"
        )
    return (
        "Sustained positive momentum trend"
        if change > 0
        else "Weak momentum, potential consolidation"
    )

def refresh(profile):
    global _last_fetch, _cached
    now = time.time()
    if now - _last_fetch < CACHE_TTL:
        return

    data = datasources.get_crypto_data()
    results = []

    for c in data:
        score = c["change_24h"]
        prob = min(95, max(30, abs(score) * (12 if profile == "aggressive" else 8)))

        results.append({
            "symbol": c["symbol"],
            "name": c["name"],
            "change_1h": round(score / 4, 2),
            "change_24h": round(score, 2),
            "probability": round(prob, 1),
            "explanation_simple": explain(score, profile),
            "explanation_technical": "Relative momentum vs market average (Binance)",
            "score": score,
        })

    ups = [x for x in results if x["score"] > 0][:5]
    downs = [x for x in results if x["score"] < 0][-5:]

    _cached[profile]["up"] = ups
    _cached[profile]["down"] = downs
    _last_fetch = now

@app.get("/ranking/up")
def ranking_up(profile: str = Query("balanced")):
    refresh(profile)
    return _cached[profile]["up"]

@app.get("/ranking/down")
def ranking_down(profile: str = Query("balanced")):
    refresh(profile)
    return _cached[profile]["down"]

@app.get("/healthz")
def healthz():
    return {"ok": True}
