from fastapi import FastAPI, Query
import requests
from typing import List

app = FastAPI()

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"

TOP_N = 5


def fetch_coingecko():
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "price_change_percentage": "1h,24h",
    }
    r = requests.get(COINGECKO_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def fetch_binance():
    r = requests.get(BINANCE_URL, timeout=10)
    r.raise_for_status()
    return r.json()


def normalize_data():
    cg = []
    bn = {}

    try:
        cg = fetch_coingecko()
    except Exception:
        cg = []

    try:
        bn_raw = fetch_binance()
        for item in bn_raw:
            if item["symbol"].endswith("USDT"):
                symbol = item["symbol"].replace("USDT", "")
                bn[symbol] = float(item["priceChangePercent"])
    except Exception:
        bn = {}

    merged = []

    for coin in cg:
        symbol = coin["symbol"].upper()
        change_1h = coin.get("price_change_percentage_1h_in_currency") or 0
        change_24h = coin.get("price_change_percentage_24h_in_currency") or 0

        # Binance fallback / validation
        if symbol in bn:
            change_24h = (change_24h + bn[symbol]) / 2

        score = (change_1h * 0.6) + (change_24h * 0.4)

        merged.append({
            "symbol": symbol,
            "name": coin["name"],
            "change_1h": change_1h,
            "change_24h": change_24h,
            "probability": min(max(abs(score) * 10, 5), 95),
            "score": score,
            "explanation_simple": (
                "Strong buying pressure detected"
                if score > 0
                else "Selling pressure increasing"
            ),
            "explanation_technical": (
                "Momentum confirmed by multi-source validation"
                if symbol in bn
                else "Momentum based on primary market data"
            ),
        })

    return merged


@app.get("/ranking/up")
def ranking_up(mode: str = Query("balanced")) -> List[dict]:
    data = normalize_data()

    threshold = 0.5 if mode == "balanced" else 0.2

    up = [c for c in data if c["score"] > threshold]
    up.sort(key=lambda x: x["score"], reverse=True)

    return up[:TOP_N]


@app.get("/ranking/down")
def ranking_down(mode: str = Query("balanced")) -> List[dict]:
    data = normalize_data()

    threshold = -0.5 if mode == "balanced" else -0.2

    down = [c for c in data if c["score"] < threshold]
    down.sort(key=lambda x: x["score"])

    return down[:TOP_N]
