from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from typing import List, Dict
import time

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- CACHE ----------------
CACHE_TTL = 120  # secondi
_last_fetch = 0
_cached_up: List[Dict] = []
_cached_down: List[Dict] = []

BINANCE_API = "https://api.binance.com/api/v3/ticker/24hr"


# ---------------- HELPERS ----------------

def fetch_binance_data() -> List[Dict]:
    response = requests.get(BINANCE_API, timeout=10)
    response.raise_for_status()
    data = response.json()

    coins = []
    for item in data:
        symbol = item["symbol"]
        if (
            symbol.endswith("USDT")
            and not any(x in symbol for x in ["UP", "DOWN", "BEAR", "BULL"])
        ):
            coins.append({
                "symbol": symbol.replace("USDT", ""),
                "change_24h": float(item.get("priceChangePercent", 0.0)),
                "volume": float(item.get("quoteVolume", 0.0)),
            })
    return coins


def build_payload(coin: Dict) -> Dict:
    change_24h = coin["change_24h"]
    change_1h = round(change_24h / 4, 2)

    probability = min(90, max(30, abs(change_24h) * 10))

    return {
        "symbol": coin["symbol"],
        "name": coin["symbol"],
        "change_1h": change_1h,
        "change_24h": round(change_24h, 2),
        "probability": probability,
        "explanation_simple": (
            "Relative short-term strength"
            if change_24h > 0
            else "Relative short-term weakness"
        ),
        "explanation_technical": "Relative momentum vs market average (Binance)",
    }


def refresh_cache():
    global _last_fetch, _cached_up, _cached_down

    now = time.time()
    if now - _last_fetch < CACHE_TTL:
        return

    try:
        data = fetch_binance_data()
        data.sort(key=lambda x: x["change_24h"], reverse=True)

        ups = [build_payload(c) for c in data if c["change_24h"] > 0][:5]
        downs = [build_payload(c) for c in data if c["change_24h"] < 0][-5:]

        if ups:
            _cached_up = ups
        if downs:
            _cached_down = downs

        _last_fetch = now

    except Exception:
        # fallback silenzioso su cache precedente
        pass


# ---------------- ENDPOINTS ----------------

@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/ranking/up")
def ranking_up(mode: str = Query("balanced")):
    refresh_cache()
    return _cached_up


@app.get("/ranking/down")
def ranking_down(mode: str = Query("balanced")):
    refresh_cache()
    return _cached_down
