import requests
import time

def fetch_from_binance():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    data = response.json()
    
    results = []
    for item in data:
        symbol = item['symbol']
        if symbol.endswith("USDT") and float(item['quoteVolume']) > 1000000:
            results.append({
                "symbol": symbol.replace("USDT", ""),
                "change_24h": float(item['priceChangePercent']),
                "change_1h": float(item['priceChangePercent']) * 0.1, # Approssimato per Ticker 24h
                "volume": float(item['quoteVolume']),
                "source": "Binance Live"
            })
    return results

def fetch_from_kraken():
    # Kraken come fallback affidabile
    url = "https://api.kraken.com/0/public/Ticker"
    response = requests.get(url, timeout=5)
    data = response.json()['result']
    results = []
    for k, v in data.items():
        if k.endswith("USD"): # Kraken usa USD
            results.append({
                "symbol": k.replace("USD", "").replace("Z", "").replace("X", ""),
                "change_24h": float(v['p'][1]), # Media pesata
                "change_1h": float(v['p'][1]) * 0.08,
                "source": "Kraken Fallback"
            })
    return results

def fetch_assets_snapshot():
    # Logica di rimbalzo tra le fonti
    try:
        return fetch_from_binance()
    except Exception as e:
        print(f"Binance Down, trying Kraken: {e}")
        try:
            return fetch_from_kraken()
        except Exception as e2:
            print(f"All sources failed: {e2}")
            return None # Trigger per la persistenza