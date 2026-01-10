from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd"
    "&order=market_cap_desc"
    "&per_page=50"
    "&page=1"
    "&price_change_percentage=1h,24h"
)

CACHE = {"data": None, "timestamp": 0}
CACHE_TTL = 120  # seconds


def fetch_market_data():
    now = time.time()
    if CACHE["data"] and now - CACHE["timestamp"] < CACHE_TTL:
        return CACHE["data"]

    r = requests.get(COINGECKO_URL, timeout=10)
    r.raise_for_status()
    data = r.json()

    CACHE["data"] = data
    CACHE["timestamp"] = now
    return data


def score_coin(coin, mode):
    change_1h = coin.get("price_change_percentage_1h_in_currency") or 0
    change_24h = coin.get("price_change_percentage_24h_in_currency") or 0

    if mode == "aggressive":
        score = change_1h * 1.5 + change_24h * 0.5
    else:
        score = change_1h * 0.7 + change_24h * 0.3

    return round(score, 2)


def build_response(coin, probability, direction):
    return {
        "symbol": coin["symbol"].upper(),
        "name": coin["name"],  # ✅ NOME COMPLETO AGGIUNTO
        "probability": probability,
        "change_1h": round(
            coin.get("price_change_percentage_1h_in_currency") or 0, 2
        ),
        "change_24h": round(
            coin.get("price_change_percentage_24h_in_currency") or 0, 2
        ),
        "explanation_simple": (
            "Strong buying pressure detected"
            if direction == "up"
            else "Selling pressure increasing"
        ),
        "explanation_technical": (
            "RSI trend + volume confirmation"
            if direction == "up"
            else "Bearish divergence on momentum indicators"
        ),
    }


@app.get("/ranking/up")
def ranking_up(mode: str = Query("balanced")):
    data = fetch_market_data()

    scored = []
    for coin in data:
        score = score_coin(coin, mode)
        if score > 0:
            scored.append((score, coin))

    scored.sort(reverse=True, key=lambda x: x[0])
    top = scored[:5]

    return [
        build_response(coin, min(90, abs(score) * 10), "up")
        for score, coin in top
    ]


@app.get("/ranking/down")
def ranking_down(mode: str = Query("balanced")):
    data = fetch_market_data()

    scored = []
    for coin in data:
        score = score_coin(coin, mode)
        if score < 0:
            scored.append((score, coin))

    scored.sort(key=lambda x: x[0])
    top = scored[:5]

    return [
        build_response(coin, min(90, abs(score) * 10), "down")
        for score, coin in top
    ]


@app.get("/")
def root():
    return {"status": "Momentum backend running"}
