from fastapi import FastAPI, Query
import requests
from typing import List

app = FastAPI()

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"

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
        "price_change_percentage": "1h,24h",
    }
    r = requests.get(COINGECKO_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def fetch_binance():
    r = requests.get(BINANCE_URL, timeout=10)
    r.raise_for_status()
    return r.json()


def build_market_snapshot():
    cg_data = []
    bn_data = {}

    # --- CoinGecko (primary)
    try:
        cg_data = fetch_coingecko()
    except Exception:
        cg_data = []

    # --- Binance (secondary)
    try:
        bn_raw = fetch_binance()
        for item in bn_raw:
            if item["symbol"].endswith("USDT"):
                symbol = item["symbol"].replace("USDT", "")
                bn_data[symbol] = safe_float(item["priceChangePercent"])
    except Exception:
        bn_data = {}

    snapshot = []

    # --- NORMAL PATH
    for coin in cg_data:
        symbol = coin["symbol"].upper()
        name = coin["name"]

        ch1 = safe_float(
            coin.get("price_change_percentage_1h_in_currency"), 0
        )
        ch24 = safe_float(
            coin.get("price_change_percentage_24h_in_currency"), 0
        )

        if symbol in bn_data:
            ch24 = (ch24 + bn_data[symbol]) / 2

        score = (ch1 * 0.6) + (ch24 * 0.4)

        snapshot.append({
            "symbol": symbol,
            "name": name,
            "change_1h": round(ch1, 2),
            "change_24h": round(ch24, 2),
            "score": score,
            "probability": max(10, min(abs(score) * 8 + 20, 90)),
            "explanation_simple": (
                "Positive short-term momentum"
                if score >= 0 else "Negative short-term momentum"
            ),
            "explanation_technical": "Relative momentum ranking (multi-source)",
        })

    # --- ABSOLUTE FALLBACK (never empty)
    if not snapshot:
        # synthetic minimal dataset
        fallback_symbols = [
            ("BTC", "Bitcoin"),
            ("ETH", "Ethereum"),
            ("BNB", "Binance Coin"),
            ("SOL", "Solana"),
            ("XRP", "XRP"),
            ("ADA", "Cardano"),
            ("AVAX", "Avalanche"),
            ("DOGE", "Dogecoin"),
            ("DOT", "Polkadot"),
            ("MATIC", "Polygon"),
        ]

        for i, (sym, name) in enumerate(fallback_symbols):
            score = (len(fallback_symbols) / 2 - i) * 0.1
            snapshot.append({
                "symbol": sym,
                "name": name,
                "change_1h": 0.0,
                "change_24h": 0.0,
                "score": score,
                "probability": 30,
                "explanation_simple": "Market data temporarily degraded",
                "explanation_technical": "Fallback relative ranking",
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
