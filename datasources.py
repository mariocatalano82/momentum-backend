import requests

def get_crypto_data():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    try:
        response = requests.get(url, timeout=10)
        all_tickers = response.json()

        data = []
        for item in all_tickers:
            symbol = item["symbol"]
            if symbol.endswith("USDT") and not any(x in symbol for x in ["UP", "DOWN", "BEAR", "BULL"]):
                data.append({
                    "symbol": symbol.replace("USDT", ""),
                    "name": symbol.replace("USDT", ""),
                    "change_24h": float(item["priceChangePercent"]),
                    "volume": float(item["quoteVolume"]),
                })

        data.sort(key=lambda x: x["change_24h"], reverse=True)
        return data

    except Exception:
        return []
