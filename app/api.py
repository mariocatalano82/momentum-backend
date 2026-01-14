from typing import Dict, List
from app.datasources import get_crypto_data

def build_payload(coin: Dict) -> Dict:
    return {
        "symbol": coin["symbol"],
        "name": coin["name"],
        "change_1h": coin["change_1h"],
        "change_24h": coin["change_24h"],
        "probability": coin["probability"],
        "explanation_simple": coin["explanation_simple"],
        "explanation_technical": coin["explanation_technical"],
        "score": coin["score"],
    }

def get_top_up() -> List[Dict]:
    data = get_crypto_data()
    up = [build_payload(c) for c in data if c["change_24h"] > 0]
    up.sort(key=lambda x: x["score"], reverse=True)
    return up[:5]

def get_top_down() -> List[Dict]:
    data = get_crypto_data()
    down = [build_payload(c) for c in data if c["change_24h"] < 0]
    down.sort(key=lambda x: x["score"])
    return down[:5]
