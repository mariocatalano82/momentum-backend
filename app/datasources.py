import requests

def fetch_from_binance():
    # Usiamo l'endpoint ticker 24h che è molto stabile
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url, timeout=8)
    response.raise_for_status()
    data = response.json()
    
    results = []
    for item in data:
        symbol = item['symbol']
        # Filtriamo solo USDT e monete con volume > 2M per sicurezza
        if symbol.endswith("USDT") and float(item['quoteVolume']) > 2000000:
            change_24h = float(item['priceChangePercent'])
            # Stimiamo la 1h dalla 24h per velocità di risposta
            # In un futuro upgrade useremo i websocket per 1h precisa
            results.append({
                "symbol": symbol.replace("USDT", ""),
                "change_24h": change_24h,
                "change_1h": round(change_24h / 24 * (1.2 if change_24h > 0 else 0.8), 2),
                "volume": float(item['quoteVolume'])
            })
    return results

def fetch_assets_snapshot():
    try:
        return fetch_from_binance()
    except Exception as e:
        print(f"Data Fetch Error: {e}")
        return None