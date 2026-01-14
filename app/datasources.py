import requests
from app.indicators import compute_probability

BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"

def get_market_snapshot(profile: str):
    try:
        r = requests.get(BINANCE_URL, timeout=10)
        r.raise_for_status()
        data = r.json()

        enriched = []
        for c in data:
            if not c.get("symbol", "").endswith("USDT"):
                continue

            change = float(c["priceChangePercent"])
            prob = compute_probability(change, profile)

            enriched.append({
                "symbol": c["symbol"].replace("USDT", ""),
                "price_change_24h": round(change, 1),
                "probability": round(prob, 1)
            })

        up = sorted(enriched, key=lambda x: -x["probability"])[:5]
        down = sorted(enriched, key=lambda x: x["probability"])[:5]

        return {
            "last_valid_up": up,
            "last_valid_down": down
        }

    except Exception as e:
        return {
            "error": "Market data unavailable"
        }
