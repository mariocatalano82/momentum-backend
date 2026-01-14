import requests
from typing import List, Dict


# ---------------- BINANCE (PRIMARY) ----------------

def fetch_binance() -> List[Dict]:
    url = "https://api.binance.com/api/v3/ticker/24hr"
    r = requests.get(url, timeout=8)
    r.raise_for_status()

    out = []
    for c in r.json():
        symbol = c["symbol"]
        if not symbol.endswith("USDT"):
            continue
        if any(x in symbol for x in ["UP", "DOWN", "BULL", "BEAR"]):
            continue

        out.append({
            "symbol": symbol.replace("USDT", ""),
            "name": symbol.replace("USDT", ""),
            "change_24h": float(c["priceChangePercent"]),
            "volume": float(c["quoteVolume"]),
        })
    return out


# ---------------- KUCOIN (FALLBACK 1) ----------------

def fetch_kucoin() -> List[Dict]:
    url = "https://api.kucoin.com/api/v1/market/allTickers"
    r = requests.get(url, timeout=8)
    r.raise_for_status()

    data = r.json()["data"]["ticker"]
    out = []

    for c in data:
        symbol = c["symbol"]
        if not symbol.endswith("-USDT"):
            continue

        out.append({
            "symbol": symbol.replace("-USDT", ""),
            "name": symbol.replace("-USDT", ""),
            "change_24h": float(c["changeRate"]) * 100,
            "volume": float(c["volValue"]),
        })
    return out


# ---------------- COINBASE (FALLBACK 2) ----------------

def fetch_coinbase() -> List[Dict]:
    url = "https://api.exchange.coinbase.com/products"
    products = requests.get(url, timeout=8).json()

    out = []
    for p in products:
        if not p["id"].endswith("-USD"):
            continue

        ticker_url = f"https://api.exchange.coinbase.com/products/{p['id']}/stats"
        stats = requests.get(ticker_url, timeout=6).json()

        try:
            open_p = float(stats["open"])
            last_p = float(stats["last"])
            volume = float(stats["volume"])

            change_24h = ((last_p - open_p) / open_p) * 100

            out.append({
                "symbol": p["base_currency"],
                "name": p["base_currency"],
                "change_24h": round(change_24h, 2),
                "volume": volume,
            })
        except Exception:
            continue

    return out


# ---------------- UNIFIED ENTRY ----------------

def get_crypto_data() -> List[Dict]:
    for source in (fetch_binance, fetch_kucoin, fetch_coinbase):
        try:
            data = source()
            if data:
                return data
        except Exception:
            continue

    return []
