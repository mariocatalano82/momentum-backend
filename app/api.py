from fastapi import FastAPI
import requests
import time

app = FastAPI()

# ======================
# CONFIG
# ======================
COINGECKO_TOP100_URL = (
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd&order=market_cap_desc&per_page=100&page=1"
    "&price_change_percentage=1h,24h"
)

BINANCE_24H_URL = "https://api.binance.com/api/v3/ticker/24hr"

# ======================
# STATE (in-memory)
# ======================
STATE = {
    "market_state": "neutral",
    "last_valid_up": [],
    "last_valid_down": [],
    "last_update": None,
}

# ======================
# HELPERS
# ======================
def normalize_probability(score: float) -> float:
    return max(30, min(90, abs(score)))

def fetch_coingecko_top100():
    r = requests.get(COINGECKO_TOP100_URL, timeout=10)
    r.raise_for_status()
    return r.json()

def fetch_binance_backup():
    r = requests.get(BINANCE_24H_URL, timeout=10)
    r.raise_for_status()
    return r.json()

# ======================
# CORE LOGIC
# ======================
def compute_from_coingecko():
    data = fetch_coingecko_top100()

    up, down = [], []

    for c in data:
        symbol = c["symbol"].upper()
        name = c["name"]
        ch1 = c.get("price_change_percentage_1h_in_currency") or 0
        ch24 = c.get("price_change_percentage_24h_in_currency") or 0
        score = ch1 + ch24

        entry = {
            "symbol": symbol,
            "name": name,
            "change_1h": round(ch1, 2),
            "change_24h": round(ch24, 2),
            "score": round(score, 2),
            "probability": round(normalize_probability(score), 2),
            "explanation_simple": "Relative short-term momentum",
            "explanation_technical": "Price acceleration vs top-100 crypto basket",
            "data_quality": "normal",
        }

        if score > 0:
            up.append(entry)
        elif score < 0:
            down.append(entry)

    return up[:5], down[:5]

def compute_from_binance_backup():
    data = fetch_binance_backup()

    up, down = [], []

    for c in data:
        if not c["symbol"].endswith("USDT"):
            continue

        symbol = c["symbol"].replace("USDT", "")
        try:
            ch24 = float(c["priceChangePercent"])
        except:
            continue

        entry = {
            "symbol": symbol,
            "name": symbol,  # Binance non fornisce full name
            "change_1h": 0.0,
            "change_24h": round(ch24, 2),
            "score": round(ch24, 2),
            "probability": round(normalize_probability(ch24), 2),
            "explanation_simple": "Relative short-term momentum (backup)",
            "explanation_technical": "Binance 24h ticker fallback",
            "data_quality": "degraded",
        }

        if ch24 > 0:
            up.append(entry)
        elif ch24 < 0:
            down.append(entry)

    return up[:5], down[:5]

def update_state():
    try:
        up, down = compute_from_coingecko()
        if up or down:
            STATE["market_state"] = "active"
            STATE["last_valid_up"] = up
            STATE["last_valid_down"] = down
            STATE["last_update"] = time.time()
            return
    except:
        pass

    try:
        up, down = compute_from_binance_backup()
        if up or down:
            STATE["market_state"] = "active"
            STATE["last_valid_up"] = up
            STATE["last_valid_down"] = down
            STATE["last_update"] = time.time()
            return
    except:
        pass

    STATE["market_state"] = "neutral"

# ======================
# API
# ======================
@app.get("/ranking/state")
def ranking_state():
    update_state()
    return STATE

@app.get("/ranking/up")
def ranking_up(mode: str = "balanced"):
    update_state()
    return STATE["last_valid_up"]

@app.get("/ranking/down")
def ranking_down(mode: str = "balanced"):
    update_state()
    return STATE["last_valid_down"]
