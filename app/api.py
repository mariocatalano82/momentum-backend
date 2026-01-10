from fastapi import FastAPI, Query
import requests
from typing import List

app = FastAPI()

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
BINANCE_TICKER_URL = "https://api.binance.com/api/v3/ticker/24hr"

TOP_N = 5


def safe_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def fetch_coingecko():
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "price_change_percentage": "24h",
    }
    r = requests.get(COINGECKO_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def fetch_binance_ticker():
    r = requests.get(BINANCE_TICKER_URL, timeout=10)
    r.raise_for_status()
    return r.json()


def build_market_snapshot():
    snapshot = []
    data_quality = "normal"

    # --- Binance 24h (primary momentum feed)
    bn_24h = {}
    try:
        for item in fetch_binance_ticker():
            if item["symbol"].endswith("USDT"):
                bn_24h[item["symbol"].replace("USDT", "")] = safe_float(
                    item["priceChangePercent"]
                )
    except Exception:
        data_quality = "degraded"

    # --- CoinGecko (names + fallback)
    try:
        cg_data = fetch_coingecko()
    except Exception:
        cg_data = []
        data_quality = "degraded"

    # --- build snapshot
    changes = list(bn_24h.values())
    avg_change = sum(changes) / len(changes) if changes else 0

    for coin in cg_data:
        symbol = coin["symbol"].upper()
        name = coin["name"]

        ch24 = bn_24h.get(
            symbol,
            safe_float(coin.get("price_change_percentage_24h"), 0),
        )

        # relative momentum vs market
        score = ch24 - avg_change

        snapshot.append({
            "symbol": symbol,
            "name": name,
            "change_1h": round(score, 2),  # proxy short-term momentum
            "change_24h": round(ch24, 2),
            "score": score,
            "probability": max(20, min(abs(score) * 8 + 25, 90)),
            "explanation_simple": (
                "Relative short-term strength"
                if score >= 0
                else "Relative short-term weakness"
            ),
            "explanation_technical": (
                "Relative momentum vs market average (Binance 24h ticker)"
            ),
            "data_quality": data_quality,
        })

    # --- absolute safety net (never empty)
    if not snapshot:
        data_quality = "degraded"
        fallback = [
            ("BTC", "Bitcoin"), ("ETH", "Ethereum"), ("BNB", "Binance Coin"),
            ("SOL", "Solana"), ("XRP", "XRP"),
            ("ADA", "Cardano"), ("AVAX", "Avalanche"),
            ("DOGE", "Dogecoin"), ("DOT", "Polkadot"), ("MATIC", "Polygon"),
        ]
        for i, (sym, name) in enumerate(fallback):
            score = (len(fallback) / 2 - i) * 0.1
            snapshot.append({
                "symbol": sym,
                "name": name,
                "change_1h": round(score, 2),
                "change_24h": 0.0,
                "score": score,
                "probability": 30,
                "explanation_simple": "Market data temporarily limited",
                "explanation_technical": "Synthetic relative ranking",
                "data_quality": "degraded",
            })

    return snapshot


@app.get("/ranking/up")
def ranking_up(mode: str = Query("balanced")) -> List[dict]:
    data = build_market_snapshot()
    data.sort(key=lambda x: x["score"], reverse=True)
    return data[:TOP_N]


@app.get("/ranking/down")
def ranking_down(mode: str = Query("balanced")) -> List[dict]:
    data = build_market_snapshot()
    data.sort(key=lambda x: x["score"])
    return data[:TOP_N]
