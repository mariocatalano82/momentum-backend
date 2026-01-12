import requests

COINGECKO_URL = "https://api.coingecko.com/api/v3"

def get_top_50():
    response = requests.get(
        f"{COINGECKO_URL}/coins/markets",
        params={
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 50,
            "page": 1,
            "price_change_percentage": "1h"
        },
        timeout=10
    )
    response.raise_for_status()
    return response.json()
