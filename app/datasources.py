import requests

BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"


def get_crypto_data():
    try:
        r = requests.get(BINANCE_URL, timeout=10)
        r.raise_for_status()
        raw = r.json()

        data = []
        for c in raw:
            if c["symbol"].endswith("USDT"):
                data.append(
                    {
                        "symbol": c["symbol"].replace("USDT", ""),
                        "name": c["symbol"].replace("USDT", ""),
                        "change_24h": float(c["priceChangePercent"]),
                    }
                )
        return data

    except Exception:
        # fallback statico → l'app NON muore mai
        return [
            {"symbol": "BTC", "name": "Bitcoin", "change_24h": 1.2},
            {"symbol": "ETH", "name": "Ethereum", "change_24h": -0.8},
            {"symbol": "SOL", "name": "Solana", "change_24h": 2.4},
            {"symbol": "XRP", "name": "XRP", "change_24h": -1.1},
        ]
