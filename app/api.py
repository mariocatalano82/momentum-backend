from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import time

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIG ---
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
VS_CURRENCY = "usd"
TOP_N = 5
TIMEOUT = 10

# --- GLOBAL STATE (CACHE) ---
last_valid_up = []
last_valid_down = []
last_update = None
market_state = "neutral"


# --- HELPERS ---
def fetch_market_data():
    params = {
        "vs_currency": VS_CURRENCY,
        "order": "market_cap_desc",
        "per_page": 100,        # ✅ whitelist TOP 100
        "page": 1,
        "price_change_percentage": "1h,24h",
    }
    r = requests.get(COINGECKO_URL, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def compute_rankings(data):
    ranked = []

    for coin in data:
        change_1h = coin.get("price_change_percentage_1h_in_currency") or 0.0
        change_24h = coin.get("price_change_percentage_24h_in_currency") or 0.0

        score = change_24h
        probability = min(90, max(30, abs(score)))

        ranked.append({
            "symbol": coin["symbol"].upper(),
            "name": coin["name"],
            "change_1h": round(change_1h, 2),
            "change_24h": round(change_24h, 2),
            "score": round(score, 2),
            "probability": round(probability, 2),
            "explanation_simple": (
                "Relative short-term strength" if score > 0
                else "Relative short-term weakness"
            ),
            "explanation_technical": "Relative strength vs broad crypto market",
            "data_quality": "normal"
        })

    ranked_up = sorted(ranked, key=lambda x: x["score"], reverse=True)[:TOP_N]
    ranked_down = sorted(ranked, key=lambda x: x["score"])[:TOP_N]

    return ranked_up, ranked_down


def update_global_state(up, down):
    global last_valid_up, last_valid_down, last_update, market_state

    # ✅ SEMPRE aggiornare la cache se i dati esistono
    if up or down:
        last_valid_up = up
        last_valid_down = down
        last_update = time.time()

    # market_state SOLO descrittivo
    strongest = max(
        [abs(x["score"]) for x in (up + down)],
        default=0
    )

    market_state = "active" if strongest >= 1.0 else "neutral"


# --- ENDPOINTS ---
@app.get("/ranking/up")
def ranking_up(mode: str = "balanced"):
    data = fetch_market_data()
    up, down = compute_rankings(data)
    update_global_state(up, down)
    return up


@app.get("/ranking/down")
def ranking_down(mode: str = "balanced"):
    data = fetch_market_data()
    up, down = compute_rankings(data)
    update_global_state(up, down)
    return down


@app.get("/ranking/state")
def ranking_state():
    return {
        "market_state": market_state,
        "last_valid_up": last_valid_up,
        "last_valid_down": last_valid_down,
        "last_update": last_update
    }
