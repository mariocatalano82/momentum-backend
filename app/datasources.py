import requests
import time

BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"

def fetch_binance():
    try:
        r = requests.get(BINANCE_URL, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("BINANCE ERROR:", e)
        return []
