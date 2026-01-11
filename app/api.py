from fastapi import FastAPI
import time
import requests

app = FastAPI()

CACHE_TTL = 120  # secondi
COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd&order=market_cap_desc&per_page=100&page=1"
    "&price_change_percentage=1h,24h"
)

STATE = {
    "market_state": "neutral",
    "last_valid_up": [],
    "last_valid_down": [],
    "last_update": 0,
}


def compute_rankings():
    try:
        r = requests.get(COINGECKO_URL, timeout=10)
        r.raise_for_status()
        data = r.json()

        scored = []
        for c in data:
            ch1 = c.get("price_change_percentage_1h_in_currency") or 0
            ch24 = c.get("price_change_percentage_24h_in_currency") or 0

            score = ch1 * 0.6 + ch24 * 0.4

            scored.append({
                "symbol": c["symbol"].upper(),
                "name": c["name"],
                "change_1h": round(ch1, 2),
                "change_24h": round(ch24, 2),
                "score": round(score, 2),
                "probability": min(90, max(30, abs(round(score * 2, 1)))),
                "explanation_simple": "Short-term momentum signal",
                "explanation_technical": (
                    "Position determined by recent 1h acceleration "
                    "combined with broader 24h trend context"
                ),
                "data_quality": "normal",
            })

        up = sorted(scored, key=lambda x: x["score"], reverse=True)[:5]
        down = sorted(scored, key=lambda x: x["score"])[:5]

        STATE["market_state"] = "active" if up or down else "neutral"
        STATE["last_valid_up"] = up
        STATE["last_valid_down"] = down
        STATE["last_update"] = time.time()

    except Exception:
        STATE["market_state"] = "neutral"


def ensure_fresh_data():
    if time.time() - STATE["last_update"] > CACHE_TTL:
        compute_rankings()


@app.get("/ranking/state")
def ranking_state():
    ensure_fresh_data()
    return STATE


@app.get("/ranking/up")
def ranking_up():
    ensure_fresh_data()
    return STATE["last_valid_up"]


@app.get("/ranking/down")
def ranking_down():
    ensure_fresh_data()
    return STATE["last_valid_down"]
