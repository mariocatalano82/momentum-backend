from fastapi import FastAPI
import threading
import time
import requests

app = FastAPI()

# ====== GLOBAL STATE ======
STATE = {
    "market_state": "neutral",
    "last_valid_up": [],
    "last_valid_down": [],
    "last_update": None,
}

# ====== CONFIG ======
COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd&order=market_cap_desc&per_page=100&page=1"
    "&price_change_percentage=1h,24h"
)

REFRESH_SECONDS = 300  # 5 minuti

# ====== CORE LOGIC ======
def compute_rankings():
    try:
        r = requests.get(COINGECKO_URL, timeout=10)
        r.raise_for_status()
        data = r.json()

        scored = []
        for c in data:
            ch1 = c.get("price_change_percentage_1h_in_currency") or 0
            ch24 = c.get("price_change_percentage_24h_in_currency") or 0
            score = ch1 * 0.6 + ch24 * 0.4

            scored.append({
                "symbol": c["symbol"].upper(),
                "name": c["name"],
                "change_1h": round(ch1, 2),
                "change_24h": round(ch24, 2),
                "score": round(score, 2),
                "probability": min(90, max(30, abs(round(score * 2, 1)))),
                "explanation_simple": "Short-term momentum signal",
                "explanation_technical": (
                    "Ranking derived from 1h and 24h relative performance "
                    "within the broader crypto market"
                ),
                "data_quality": "normal",
            })

        up = sorted(scored, key=lambda x: x["score"], reverse=True)[:5]
        down = sorted(scored, key=lambda x: x["score"])[:5]

        if up or down:
            STATE["market_state"] = "active"
            STATE["last_valid_up"] = up
            STATE["last_valid_down"] = down
            STATE["last_update"] = time.time()
        else:
            STATE["market_state"] = "neutral"

        print("✔ Momentum recomputed")

    except Exception as e:
        print("❌ Compute error:", e)
        STATE["market_state"] = "neutral"


# ====== BACKGROUND LOOP ======
def background_loop():
    while True:
        compute_rankings()
        time.sleep(REFRESH_SECONDS)


# ====== STARTUP ======
@app.on_event("startup")
def startup():
    compute_rankings()  # calcolo immediato
    t = threading.Thread(target=background_loop, daemon=True)
    t.start()


# ====== API ======
@app.get("/ranking/state")
def ranking_state():
    return STATE


@app.get("/ranking/up")
def ranking_up():
    return STATE["last_valid_up"]


@app.get("/ranking/down")
def ranking_down():
    return STATE["last_valid_down"]
