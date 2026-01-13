from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
from typing import List, Dict

app = FastAPI()

# --- CORS (necessario per Flutter Web / Android) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL STATE (ULTIMI SEGNALI VALIDI) ---
LAST_VALID_UP: List[Dict] = []
LAST_VALID_DOWN: List[Dict] = []
LAST_VALID_TIMESTAMP: float | None = None

# --- CONFIG ---
BINANCE_24H_API = "https://api.binance.com/api/v3/ticker/24hr"
TOP_LIMIT = 50
TOP_RESULT = 5


# --- MARKET DATA ---
def fetch_market_data() -> List[Dict]:
    r = requests.get(BINANCE_24H_API, timeout=10)
    r.raise_for_status()
    data = r.json()

    # prendiamo solo le top coin più comuni
    filtered = []
    for item in data:
        symbol = item.get("symbol", "")
        if symbol.endswith("USDT"):
            filtered.append({
                "symbol": symbol.replace("USDT", ""),
                "change_24h": float(item.get("priceChangePercent", 0.0))
            })

    return filtered[:TOP_LIMIT]


# --- MOMENTUM ENGINE ---
def compute_momentum(data: List[Dict]) -> Dict[str, List[Dict]]:
    ups = []
    downs = []

    for coin in data:
        change = coin["change_24h"]

        if change > 0:
            ups.append({
                "symbol": coin["symbol"],
                "name": coin["symbol"],
                "change_1h": round(change / 4, 2),   # proxy short-term
                "change_24h": round(change, 2),
                "score": change,
                "probability": min(90, max(30, abs(change) * 10)),
                "explanation_simple": "Relative short-term strength",
                "explanation_technical": "Relative momentum vs market average (Binance 24h ticker)",
                "data_quality": "normal"
            })
        elif change < 0:
            downs.append({
                "symbol": coin["symbol"],
                "name": coin["symbol"],
                "change_1h": round(change / 4, 2),
                "change_24h": round(change, 2),
                "score": change,
                "probability": min(90, max(30, abs(change) * 10)),
                "explanation_simple": "Relative short-term weakness",
                "explanation_technical": "Relative momentum vs market average (Binance 24h ticker)",
                "data_quality": "normal"
            })

    ups = sorted(ups, key=lambda x: x["score"], reverse=True)[:TOP_RESULT]
    downs = sorted(downs, key=lambda x: x["score"])[:TOP_RESULT]

    return {"up": ups, "down": downs}


# --- FALLBACK (DEGRADED DATA) ---
def degraded_fallback() -> Dict[str, List[Dict]]:
    fallback_up = [
        {"symbol": "BTC", "name": "Bitcoin", "change_1h": 0.0, "change_24h": 0.0, "score": 0.5,
         "probability": 30, "explanation_simple": "Market data temporarily degraded",
         "explanation_technical": "Synthetic relative ranking", "data_quality": "degraded"}
    ]

    fallback_down = [
        {"symbol": "ETH", "name": "Ethereum", "change_1h": 0.0, "change_24h": 0.0, "score": -0.5,
         "probability": 30, "explanation_simple": "Market data temporarily degraded",
         "explanation_technical": "Synthetic relative ranking", "data_quality": "degraded"}
    ]

    return {"up": fallback_up, "down": fallback_down}


# --- ENDPOINTS ---

@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/ranking/up")
def ranking_up(mode: str = Query("balanced")):
    global LAST_VALID_UP, LAST_VALID_DOWN, LAST_VALID_TIMESTAMP

    try:
        data = fetch_market_data()
        result = compute_momentum(data)

        if result["up"]:
            LAST_VALID_UP = result["up"]
            LAST_VALID_DOWN = result["down"]
            LAST_VALID_TIMESTAMP = time.time()
            return result["up"]

        # market neutral → ritorna ultimi segnali validi
        return LAST_VALID_UP

    except Exception:
        return degraded_fallback()["up"]


@app.get("/ranking/down")
def ranking_down(mode: str = Query("balanced")):
    global LAST_VALID_UP, LAST_VALID_DOWN, LAST_VALID_TIMESTAMP

    try:
        data = fetch_market_data()
        result = compute_momentum(data)

        if result["down"]:
            LAST_VALID_UP = result["up"]
            LAST_VALID_DOWN = result["down"]
            LAST_VALID_TIMESTAMP = time.time()
            return result["down"]

        # market neutral → ritorna ultimi segnali validi
        return LAST_VALID_DOWN

    except Exception:
        return degraded_fallback()["down"]


@app.get("/ranking/state")
def ranking_state():
    return {
        "market_state": "neutral" if not LAST_VALID_UP and not LAST_VALID_DOWN else "active",
        "last_valid_up": LAST_VALID_UP,
        "last_valid_down": LAST_VALID_DOWN,
        "last_update": LAST_VALID_TIMESTAMP
    }
