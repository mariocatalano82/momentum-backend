import requests

def fetch_from_binance():
    # Usiamo l'endpoint 24h ticker
    url = "https://api.binance.com/api/v3/ticker/24hr"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Connection Error: {e}")
        return []
    
    results = []
    for item in data:
        symbol = item['symbol']
        # Filtro: Solo USDT e Volume > 3M per evitare "shitcoins" illiquide
        if symbol.endswith("USDT") and float(item['quoteVolume']) > 3000000:
            c24 = float(item['priceChangePercent'])
            
            # --- MIGLIORIA CALCOLO ---
            # Calcoliamo la volatilità intraday (High - Low) / Low
            high = float(item['highPrice'])
            low = float(item['lowPrice'])
            volatility_factor = (high - low) / low if low > 0 else 0
            
            # Stima 1H migliorata: Amplifica la stima in base alla volatilità reale
            raw_1h = (c24 / 24)
            amplified_1h = raw_1h * (1.0 + (volatility_factor * 8.0))
            
            results.append({
                "symbol": symbol.replace("USDT", ""),
                "change_24h": round(c24, 2),
                "change_1h": round(amplified_1h, 2),
                "volume": float(item['quoteVolume'])
            })
    return results

def fetch_assets_snapshot():
    return fetch_from_binance()