from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BINANCE_TICKER_24H = "https://api.binance.com/api/v3/ticker/24hr"
COINGECKO_TOP100 = "https://api.coingecko.com/api/v3/coins/markets"

VS_CURRENCY = "usd"
TOP_LIMIT = 100
TOP_SHOW = 5

# Stato globale
STATE = {
    "market_state": "neutral",
    "last_valid_up": [],
    "last_valid_down": [],
    "last_update": None,
}


# ---------- UTILITIES ----------

def fetch_binance():
    r = requests.get(BINANCE_TICKER_24H, timeout=10)
    r.raise_for_status()
    return r.json()


def fetch_coingecko_names():
    r = requests.get(
        COINGECKO_TOP100,
        params={
            "vs_currency": VS_CURRENCY,
            "order": "market_cap_desc",
            "per_page": TOP_LIMIT,
            "page": 1,
        },
        timeout=10,
    )
    r.raise_for_status()
    return {c["symbol"].upper(): c["name"] for c in r.json()}


def normalize(entry, names):
    symbol = entry["symbol"].replace("USDT", "")
    change_24h = float(entry.get("priceChangePercent", 0.0))
    change_1h = 0.0  # Binance non fornisce 1h diretto → coerente con decisioni

    score = change_24h
    probability = min(90, max(30, abs(change_24h)))

    return {
        "symbol": symbol,
        "name": names.get(symbol, symbol),
        "change_1h": round(change_1h, 2),
        "change_24h": round(change_24h, 2),
        "score": round(score, 2),
        "probability": round(probability, 2),
        "explanation_simple": "Relative short-term momentum",
        "explanation_technical": (
            "Momentum derived from recent relative performance versus the broader crypto market"
        ),
        "data_quality": "normal",
    }


def compute_rankings():
    global STATE

    try:
        binance = fetch_binance()
        names = fetch_coingecko_names()

        filtered = [
            e for e in binance
            if e["symbol"].endswith("USDT")
            and e["symbol"].replace("USDT", "") in names
        ]

        normalized = [normalize(e, names) for e in filtered]

        ups = sorted(normalized, key=lambda x: x["score"], reverse=True)
        downs = sorted(normalized, key=lambda x: x["score"])

        top_up = ups[:TOP_SHOW]
        top_down = downs[:TOP_SHOW]

        dominance = max(
            abs(top_up[0]["score"]) if top_up else 0,
            abs(top_down[0]["score"]) if top_down else 0,
        )

        if dominance < 1.0:
            STATE["market_state"] = "neutral"
        else:
            STATE["market_state"] = "active"
            STATE["last_valid_up"] = top_up
            STATE["last_valid_down"] = top_down
            STATE["last_update"] = time.time()

    except Exception:
        # fallback: non azzeriamo MAI
        for side in ["last_valid_up", "last_valid_down"]:
            for e in STATE[side]:
                e["data_quality"] = "degraded"
                e["explanation_simple"] = "Relative short-term momentum (backup)"
                e["explanation_technical"] = (
                    "Momentum estimated using limited but available market data"
                )

        STATE["market_state"] = "active" if STATE["last_valid_up"] else "neutral"


# ---------- API ----------

@app.get("/ranking/state")
def market_state():
    compute_rankings()
    return STATE


@app.get("/ranking/up")
def ranking_up(mode: str = "balanced"):
    compute_rankings()
    return STATE["last_valid_up"]


@app.get("/ranking/down")
def ranking_down(mode: str = "balanced"):
    compute_rankings()
    return STATE["last_valid_down"]
