from fastapi import FastAPI, Query
import requests
from typing import List
from statistics import mean

app = FastAPI()

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
BINANCE_TICKER_URL = "https://api.binance.com/api/v3/ticker/24hr"
BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"

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


def fetch_binance_intraday(symbol: str):
    params = {
        "symbol": f"{symbol}USDT",
        "interval": "15m",
        "limit": 8,  # last 2 hours
    }
    r = requests.get(BINANCE_KLINES_URL, params=params, timeout=10)
    r.raise_for_status()
    closes = [safe_float(k[4]) for k in r.json()]
    if len(closes) < 2:
        return 0.0
    returns = [(closes[i] - closes[i - 1]) / closes[i - 1] * 100 for i in range(1, len(closes))]
    return mean(returns)


def build_market_snapshot():
    snapshot = []
    data_quality = "normal"

    # --- CoinGecko (structure + names)
    try:
        cg_data = fetch_coingecko()
    except Exception:
        cg_data = []
        data_quality = "degraded"

    # --- Binance ticker (24h)
    bn_24h = {}
    try:
        for item in fetch_binance_ticker():
            if item["symbol"].endswith("USDT"):
                bn_24h[item["symbol"].replace("USDT", "")] = safe_float(item["priceChangePercent"])
    except Exception:
        data_quality = "degraded"

    for coin in cg_data:
        symbol = coin["symbol"].upper()
        name = coin["name"]

        # --- intraday momentum (real)
        try:
            intraday = fetch_binance_intraday(symbol)
        except Exception:
            intraday = 0.0
            data_quality = "degraded"

        ch24 = bn_24h.get(symbol, safe_float(coin.get("price_change_percentage_24h"), 0))

        score = (intraday * 0.7) + (ch24 * 0.3)

        snapshot.append({
            "symbol": symbol,
            "name": name,
            "change_1h": round(intraday, 2),
            "change_24h": round(ch24, 2),
            "score": score,
            "probability": max(15, min(abs(score) * 10 + 20, 90)),
            "explanation_simple": (
                "Short-term momentum building"
                if score >= 0
                else "Short-term weakness detected"
            ),
            "explanation_technical": (
                "Intraday momentum from 15m price action (Binance)"
                if intraday != 0
                else "Limited intraday data, fallback to broader signals"
            ),
            "data_quality": data_quality,
        })

    # --- absolute fallback (never empty)
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
                "change_1h": 0.0,
                "change_24h": 0.0,
                "score": score,
                "probability": 30,
                "explanation_simple": "Market data temporarily degraded",
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
