import requests
from config import BINANCE_BASE_URL, REQUEST_TIMEOUT

def fetch_binance_tickers():
    """
    Fetch 24h ticker data from Binance
    """
    url = f"{BINANCE_BASE_URL}/api/v3/ticker/24hr"
    res = requests.get(url, timeout=REQUEST_TIMEOUT)
    res.raise_for_status()
    return res.json()
