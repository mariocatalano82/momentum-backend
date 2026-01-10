from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
VS = "usd"
TOP_N = 5

last_valid_up = []
last_valid_down = []
last_update = None
market_state = "neutral"


def fetch_and_compute():
    global last_valid_up, last_valid_down, last_update, market_state

    params = {
        "vs_currency": VS,
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "price_change_percentage": "1h,24h",
    }

    r = requests.get(COINGECKO_URL, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()

    ranked = []
    for c in data:
        ch1 = c.get("price_change_percentage_1h_in_currency") or 0
        ch24 = c.get("price_change_percentage_24h_in_currency") or 0
        score = ch24
        ranked.append({
            "symbol": c["symbol"].upper(),
            "name": c["name"],
            "change_1h": round(ch1, 2),
            "change_24h": round(ch24, 2),
            "score": round(score, 2),
            "probability": min(90, max(30, abs(round(score, 2)))),
            "explanation_simple": "Relative short-term strength" if score > 0 else "Relative short-term weakness",
            "explanation_technical": "Relative strength vs broad crypto market",
            "data_quality": "normal"
        })

    up = sorted(ranked, key=lambda x: x["score"], reverse=True)[:TOP_N]
    down = sorted(ranked, key=lambda x: x["score"])[:TOP_N]

    last_valid_up = up
    last_valid_down = down
    last_update = time.time()

    strongest = max([abs(x["score"]) for x in up + down], default=0)
    market_state = "active" if strongest >= 1 else "neutral"

    return up, down


@app.get("/ranking/up")
def ranking_up():
    up, _ = fetch_and_compute()
    return up


@app.get("/ranking/down")
def ranking_down():
    _, down = fetch_and_compute()
    return down


@app.get("/ranking/state")
def ranking_state():
    fetch_and_compute()
    return {
        "market_state": market_state,
        "last_valid_up": last_valid_up,
        "last_valid_down": last_valid_down,
        "last_update": last_update
    }
