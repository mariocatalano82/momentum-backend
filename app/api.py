from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- CONFIG ----------
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"
VS = "usd"
TOP_N = 5
TIMEOUT = 8

# ---------- GLOBAL STATE ----------
last_valid_up = []
last_valid_down = []
last_update = None
market_state = "neutral"


# ---------- BINANCE BACKUP ----------
def fetch_binance_backup():
    r = requests.get(BINANCE_URL, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()

    ranked = []
    for item in data:
        if not item["symbol"].endswith("USDT"):
            continue

        try:
            change_24h = float(item["priceChangePercent"])
        except Exception:
            continue

        symbol = item["symbol"].replace("USDT", "")

        ranked.append({
            "symbol": symbol,
            "name": symbol,
            "change_1h": 0.0,
            "change_24h": round(change_24h, 2),
            "score": round(change_24h, 2),
            "probability": min(90, max(30, abs(round(change_24h, 2)))),
            "explanation_simple": "Relative short-term momentum (backup)",
            "explanation_technical": "Binance 24h ticker fallback",
            "data_quality": "degraded"
        })

    up = sorted(ranked, key=lambda x: x["score"], reverse=True)[:TOP_N]
    down = sorted(ranked, key=lambda x: x["score"])[:TOP_N]

    return up, down


# ---------- PRIMARY COMPUTATION ----------
def compute_market():
    global last_valid_up, last_valid_down, last_update, market_state

    try:
        r = requests.get(
            COINGECKO_URL,
            params={
                "vs_currency": VS,
                "order": "market_cap_desc",
                "per_page": 100,
                "page": 1,
                "price_change_percentage": "1h,24h",
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()

        ranked = []
        for c in data:
            ch1 = c.get("price_change_percentage_1h_in_currency") or 0
            ch24 = c.get("price_change_percentage_24h_in_currency") or 0
            score = ch24

            ranked.append({
                "symbol": c["symbol"].upper(),
                "name": c["name"],
                "change_1h": round(ch1, 2),
                "change_24h": round(ch24, 2),
                "score": round(score, 2),
                "probability": min(90, max(30, abs(round(score, 2)))),
                "explanation_simple": (
                    "Relative short-term strength" if score > 0
                    else "Relative short-term weakness"
                ),
                "explanation_technical": "Relative strength vs broad crypto market",
                "data_quality": "normal"
            })

        up = sorted(ranked, key=lambda x: x["score"], reverse=True)[:TOP_N]
        down = sorted(ranked, key=lambda x: x["score"])[:TOP_N]

    except Exception:
        # 🔁 BINANCE BACKUP
        up, down = fetch_binance_backup()

    # ---------- CACHE ALWAYS UPDATED ----------
    last_valid_up = up
    last_valid_down = down
    last_update = time.time()

    strongest = max([abs(x["score"]) for x in up + down], default=0)
    market_state = "active" if strongest >= 1 else "neutral"

    return up, down


# ---------- ENDPOINTS ----------
@app.get("/ranking/up")
def ranking_up():
    up, _ = compute_market()
    return up


@app.get("/ranking/down")
def ranking_down():
    _, down = compute_market()
    return down


@app.get("/ranking/state")
def ranking_state():
    compute_market()
    return {
        "market_state": market_state,
        "last_valid_up": last_valid_up,
        "last_valid_down": last_valid_down,
        "last_update": last_update
    }
