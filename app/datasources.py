import requests
import time

# Simple in-memory cache
_LAST_MARKET_DATA = None
_LAST_TIMESTAMP = 0


def _fetch_binance():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    return r.json()


def _fetch_coinbase():
    url = "https://api.exchange.coinbase.com/products"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    products = r.json()

    result = []
    for p in products:
        if not p.get("id") or "-" not in p["id"]:
            continue
        result.append({
            "symbol": p["base_currency"],
            "name": p["base_currency"]
        })
    return result


def fetch_market_data():
    """
    Fetch market data with fallback and cache.
    """
    global _LAST_MARKET_DATA, _LAST_TIMESTAMP

    now = time.time()
    if _LAST_MARKET_DATA and now - _LAST_TIMESTAMP < 300:
        return _LAST_MARKET_DATA, False

    try:
        data = _fetch_binance()
        _LAST_MARKET_DATA = data
        _LAST_TIMESTAMP = now
        return data, False
    except Exception:
        if _LAST_MARKET_DATA:
            return _LAST_MARKET_DATA, True
        raise
