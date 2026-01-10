from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
import requests

app = FastAPI()

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# CONFIG
# =========================
BINANCE_TICKER_URL = "https://api.binance.com/api/v3/ticker/24hr"
TOP_N = 5

# =========================
# IN-MEMORY STATE
# =========================
LAST_VALID_UP = []
LAST_VALID_DOWN = []
LAST_UPDATE_TS = None

# =========================
# INITIAL SEED (REFERENCE)
# =========================
SEED_UP = [
    {
        "symbol": "BTC",
        "name": "Bitcoin",
        "change_1h": 0.6,
        "change_24h": 1.2,
        "score": 1.2,
        "probability": 55,
        "explanation_simple": "Initial reference momentum",
        "explanation_technical": "Synthetic baseline used before live signals",
        "data_quality": "initial",
    },
    {
        "symbol": "ETH",
        "name": "Ethereum",
        "change_1h": 0.5,
        "change_24h": 1.0,
        "score": 1.0,
        "probability": 52,
        "explanation_simple": "Initial reference momentum",
        "explanation_technical": "Synthetic baseline used before live signals",
        "data_quality": "initial",
    },
    {
        "symbol": "SOL",
        "name": "Solana",
        "change_1h": 0.4,
        "change_24h": 0.9,
        "score": 0.9,
        "probability": 50,
        "explanation_simple": "Initial reference momentum",
        "explanation_technical": "Synthetic baseline used before live signals",
        "data_quality": "initial",
    },
    {
        "symbol": "BNB",
        "name": "BNB",
        "change_1h": 0.3,
        "change_24h": 0.7,
        "score": 0.7,
        "probability": 48,
        "explanation_simple": "Initial reference momentum",
        "explanation_technical": "Synthetic baseline used before live signals",
        "data_quality": "initial",
    },
    {
        "symbol": "XRP",
        "name": "XRP",
        "change_1h": 0.2,
        "change_24h": 0.5,
        "score": 0.5,
        "probability": 45,
        "explanation_simple": "Initial reference momentum",
        "explanation_technical": "Synthetic baseline used before live signals",
        "data_quality": "initial",
    },
]

SEED_DOWN = [
    {
        "symbol": "ADA",
        "name": "Cardano",
        "change_1h": -0.4,
        "change_24h": -1.1,
        "score": -1.1,
        "probability": 55,
        "explanation_simple": "Initial reference weakness",
        "explanation_technical": "Synthetic baseline used before live signals",
        "data_quality": "initial",
    },
    {
        "symbol": "DOGE",
        "name": "Dogecoin",
        "change_1h": -0.3,
        "change_24h": -0.9,
        "score": -0.9,
        "probability": 52,
        "explanation_simple": "Initial reference weakness",
        "explanation_technical": "Synthetic baseline used before live signals",
        "data_quality": "initial",
    },
    {
        "symbol": "DOT",
        "name": "Polkadot",
        "change_1h": -0.2,
        "change_24h": -0.7,
        "score": -0.7,
        "probability": 50,
        "explanation_simple": "Initial reference weakness",
        "explanation_technical": "Synthetic baseline used before live signals",
        "data_quality": "initial",
    },
    {
        "symbol": "AVAX",
        "name": "Avalanche",
        "change_1h": -0.1,
        "change_24h": -0.6,
        "score": -0.6,
        "probability": 48,
        "explanation_simple": "Initial reference weakness",
        "explanation_technical": "Synthetic baseline used before live signals",
        "data_quality": "initial",
    },
    {
        "symbol": "MATIC",
        "name": "Polygon",
        "change_1h": -0.05,
        "change_24h": -0.4,
        "score": -0.4,
        "probability": 45,
        "explanation_simple": "Initial reference weakness",
        "explanation_technical": "Synthetic baseline used before live signals",
        "data_quality": "initial",
    },
]

# =========================
# HELPERS
# =========================
def fetch_binance_data():
    r = requests.get(BINANCE_TICKER_URL, timeout=10)
    r.raise_for_status()
    return r.json()


def compute_rankings():
    global LAST_VALID_UP, LAST_VALID_DOWN, LAST_UPDATE_TS

    data = fetch_binance_data()

    scored = []
    for item in data:
        try:
            change_1h = float(item.get("priceChangePercent", 0)) / 24
            change_24h = float(item.get("priceChangePercent", 0))
            score = change_24h

            scored.append({
                "symbol": item["symbol"].replace("USDT", ""),
                "name": item["symbol"].replace("USDT", ""),
                "change_1h": round(change_1h, 2),
                "change_24h": round(change_24h, 2),
                "score": round(score, 2),
                "probability": min(90, max(30, abs(round(score * 5, 2)))),
                "explanation_simple": "Relative short-term momentum",
                "explanation_technical": "Relative strength vs market average",
                "data_quality": "normal",
            })
        except Exception:
            continue

    ups = sorted(scored, key=lambda x: x["score"], reverse=True)[:TOP_N]
    downs = sorted(scored, key=lambda x: x["score"])[:TOP_N]

    # consider market active only if meaningful dispersion exists
    if ups and downs and ups[0]["score"] > 1.0:
        LAST_VALID_UP = ups
        LAST_VALID_DOWN = downs
        LAST_UPDATE_TS = time.time()
        return True

    return False

# =========================
# ENDPOINTS
# =========================
@app.get("/ranking/state")
def ranking_state():
    global LAST_VALID_UP, LAST_VALID_DOWN, LAST_UPDATE_TS

    try:
        market_active = compute_rankings()
    except Exception:
        market_active = False

    # SEED if nothing exists yet
    if not LAST_VALID_UP and not LAST_VALID_DOWN:
        LAST_VALID_UP = SEED_UP
        LAST_VALID_DOWN = SEED_DOWN
        LAST_UPDATE_TS = time.time()

    return {
        "market_state": "active" if market_active else "neutral",
        "last_valid_up": LAST_VALID_UP,
        "last_valid_down": LAST_VALID_DOWN,
        "last_update": LAST_UPDATE_TS,
    }


@app.get("/ranking/up")
def ranking_up():
    return LAST_VALID_UP


@app.get("/ranking/down")
def ranking_down():
    return LAST_VALID_DOWN
