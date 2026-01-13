from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
from typing import List, Dict

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CACHE ---
LAST_VALID_UP: List[Dict] = []
LAST_VALID_DOWN: List[Dict] = []

BINANCE_24H_API = "https://api.binance.com/api/v3/ticker/24hr"
TOP_LIMIT = 50
TOP_RESULT = 5


def fetch_market_data() -> List[Dict]:
    r = requests.get(BINANCE_24H_API, timeout=15)
    r.raise_for_status()
    data = r.json()

    filtered = []
    for item in data:
        symbol = item.get("symbol", "")
        if symbol.endswith("USDT"):
            filtered.append({
                "symbol": symbol.replace("USDT", ""),
                "change_24h": float(item.get("priceChangePercent", 0.0))
            })

    return filtered[:TOP_LIMIT]


def compute_momentum(data: List[Dict]) -> Dict[str, List[Dict]]:
    ups = []
    downs = []

    for coin in data:
        change = coin["change_24h"]

        payload = {
            "symbol": coin["symbol"],
            "name": coin["symbol"],
            "change_1h": round(change / 4, 2),
            "change_24h": round(change, 2),
            "probability": min(90, max(30, abs(change) * 10)),
            "explanation_simple": (
                "Relative short-term strength"
                if change > 0
                else "Relative short-term weakness"
            ),
            "explanation_technical": "Relative momentum vs market average (Binance)",
        }

        if change > 0:
            ups.append({**payload, "score": change})
        elif change < 0:
            downs.append({**payload, "score": change})

    ups = sorted(ups, key=lambda x: x["score"], reverse=True)[:TOP_RESULT]
    downs = sorted(downs, key=lambda x: x["score"])[:TOP_RESULT]

    return {"up": ups, "down": downs}


@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/ranking/up")
def ranking_up(mode: str = Query("balanced")):
    global LAST_VALID_UP, LAST_VALID_DOWN

    try:
        data = fetch_market_data()
        result = compute_momentum(data)

        if result["up"]:
            LAST_VALID_UP = result["up"]
            LAST_VALID_DOWN = result["down"]
            return result["up"]

        return LAST_VALID_UP
    except Exception:
        return LAST_VALID_UP


@app.get("/ranking/down")
def ranking_down(mode: str = Query("balanced")):
    global LAST_VALID_UP, LAST_VALID_DOWN

    try:
        data = fetch_market_data()
        result = compute_momentum(data)

        if result["down"]:
            LAST_VALID_UP = result["up"]
            LAST_VALID_DOWN = result["down"]
            return result["down"]

        return LAST_VALID_DOWN
    except Exception:
        return LAST_VALID_DOWN
