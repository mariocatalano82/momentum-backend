import requests

def fetch_from_binance():
    url = "https://api.binance.com/api/3/ticker/24hr"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
    except: return None
    
    results = []
    for item in data:
        symbol = item['symbol']
        # Filtro Liquidità > 3M
        if symbol.endswith("USDT") and float(item['quoteVolume']) > 3000000:
            c24 = float(item['priceChangePercent'])
            # Calcolo volatilità High-Low per raffinare la spinta 1h
            vol = (float(item['highPrice']) - float(item['lowPrice'])) / float(item['lowPrice'])
            est_1h = (c24 / 24) * (1.1 + (vol * 6))
            
            results.append({
                "symbol": symbol.replace("USDT", ""),
                "change_24h": round(c24, 2),
                "change_1h": round(est_1h, 2),
                "volume": float(item['quoteVolume'])
            })
    return results

def fetch_assets_snapshot():
    return fetch_from_binance()