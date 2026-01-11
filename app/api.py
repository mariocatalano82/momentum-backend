from fastapi import FastAPI
import requests
import time

app = FastAPI()

# ==============================
# CONFIG
# ==============================
DATA_SOURCE_URL = "https://api.coingecko.com/api/v3/coins/markets"
VS_CURRENCY = "usd"
PER_PAGE = 100
TIMEOUT = 10

# ==============================
# GLOBAL STATE
# ==============================
last_valid_up = []
last_valid_down = []
last_update = None
market_state = "neutral"


# ==============================
# DATA FETCH
# ==============================
def fetch_market_data():
    params = {
        "vs_currency": VS_CURRENCY,
        "order": "market_cap_desc",
        "per_page": PER_PAGE,
        "page": 1,
        "price_change_percentage": "1h,24h",
    }
    r = requests.get(DATA_SOURCE_URL, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


# ==============================
# MOMENTUM CALCULATION (IDEMPOTENT)
# ==============================
def ensure_momentum_computed():
    global last_valid_up, last_valid_down, last_update, market_state

    # 🔒 Already computed and recent
    if last_update and (time.time() - last_update) < 120:
        return

    try:
        data = fetch_market_data()
        scored = []

        for coin in data:
            c1h = coin.get("price_change_percentage_1h_in_currency")
            c24h = coin.get("price_change_percentage_24h_in_currency")
            if c1h is None or c24h is None:
                continue

            score = (c1h * 0.6) + (c24h * 0.4)

            scored.append({
                "symbol": coin["symbol"].upper(),
                "name": coin["name"],
                "change_1h": round(c1h, 2),
                "change_24h": round(c24h, 2),
                "score": round(score, 2),
                "probability": min(95, max(5, abs(round(score * 3, 2)))),
                "explanation_simple": "Relative short-term momentum",
                "explanation_technical": (
                    "Position determined by recent acceleration (1h) "
                    "combined with broader 24h context."
                ),
                "data_quality": "normal",
            })

        up = sorted(scored, key=lambda x: x["score"], reverse=True)[:5]
        down = sorted(scored, key=lambda x: x["score"])[:5]

        if up or down:
            last_valid_up = up
            last_valid_down = down
            last_update = time.time()
            market_state = "active"
        else:
            market_state = "neutral"

    except Exception:
        # 🔥 NEVER wipe existing valid data
        if last_valid_up or last_valid_down:
            market_state = "active"
        else:
            market_state = "neutral"


# ==============================
# ENDPOINTS
# ==============================

@app.get("/ranking/state")
def ranking_state():
    ensure_momentum_computed()
    return {
        "market_state": market_state,
        "last_valid_up": last_valid_up,
        "last_valid_down": last_valid_down,
        "last_update": last_update,
    }


@app.get("/ranking/up")
def ranking_up():
    ensure_momentum_computed()
    return last_valid_up


@app.get("/ranking/down")
def ranking_down():
    ensure_momentum_computed()
    return last_valid_down
