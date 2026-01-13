import time
import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# =========================================================
# APP
# =========================================================
app = FastAPI(
    title="Momentum Backend",
    version="1.3.1",
    description="Short-term crypto momentum (1–2h, cached & safe)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# CONFIG
# =========================================================
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
CACHE_TTL = 60  # seconds

# =========================================================
# CACHE
# =========================================================
_market_cache = {
    "timestamp": 0,
    "data": []
}

# =========================================================
# HELPERS
# =========================================================
def safe_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def fetch_market_data():
    now = time.time()

    if now - _market_cache["timestamp"] < CACHE_TTL:
        return _market_cache["data"]

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "price_change_percentage": "1h,24h",
    }

    r = requests.get(COINGECKO_URL, params=params, timeout=10)

    if r.status_code != 200:
        if _market_cache["data"]:
            return _market_cache["data"]
        r.raise_for_status()

    data = r.json()

    _market_cache["timestamp"] = now
    _market_cache["data"] = data

    return data


def compute_short_term_score(change_1h: float, change_24h: float) -> float:
    context = max(min(change_24h, 5), -5)
    return (change_1h * 0.8) + (context * 0.2)


def probability_from_score(score: float) -> float:
    base = min(abs(score) * 6, 20)
    return round(55 + base, 1)


def format_coin(coin, score, c1h, c24h):
    direction = "up" if score >= 0 else "down"

    return {
        "symbol": coin.get("symbol", "").upper(),
        "price": round(safe_float(coin.get("current_price")), 4),
        "probability": probability_from_score(score),
        "change_1h": round(c1h, 2),
        "change_24h": round(c24h, 2),
        "explanation_simple": (
            "Accelerazione oraria positiva con contesto favorevole"
            if direction == "up"
            else "Indebolimento orario con pressione recente"
        ),
        "explanation_technical": (
            "Variazione 1h dominante, trend 24h di supporto"
            if direction == "up"
            else "Movimento 1h negativo rafforzato dal contesto"
        ),
    }

# =========================================================
# HEALTH
# =========================================================
@app.get("/")
def root():
    return {
        "status": "Momentum backend running",
        "focus": "Short-term probability (1–2h)",
        "cache_ttl_sec": CACHE_TTL
    }

# =========================================================
# RANKING
# =========================================================
@app.get("/ranking/up")
def ranking_up(mode: str = Query("balanced")):
    try:
        data = fetch_market_data()
        results = []

        for coin in data:
            c1h = safe_float(coin.get("price_change_percentage_1h_in_currency"))
            c24h = safe_float(coin.get("price_change_percentage_24h_in_currency"))
            score = compute_short_term_score(c1h, c24h)

            if score > 0:
                results.append(format_coin(coin, score, c1h, c24h))

        results.sort(key=lambda x: x["probability"], reverse=True)
        limit = 5 if mode == "balanced" else 3
        return results[:limit]

    except Exception:
        return []


@app.get("/ranking/down")
def ranking_down(mode: str = Query("balanced")):
    try:
        data = fetch_market_data()
        results = []

        for coin in data:
            c1h = safe_float(coin.get("price_change_percentage_1h_in_currency"))
            c24h = safe_float(coin.get("price_change_percentage_24h_in_currency"))
            score = compute_short_term_score(c1h, c24h)

            if score < 0:
                results.append(format_coin(coin, score, c1h, c24h))

        results.sort(key=lambda x: x["probability"], reverse=True)
        limit = 5 if mode == "balanced" else 3
        return results[:limit]

    except Exception:
        return []
