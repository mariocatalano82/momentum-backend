import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# =========================================================
# APP
# =========================================================
app = FastAPI(
    title="Momentum Backend",
    version="1.2.0",
    description="Short-term crypto momentum (1–2h probability)"
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

# =========================================================
# HELPERS
# =========================================================
def fetch_market_data():
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "price_change_percentage": "1h,24h",
    }
    r = requests.get(COINGECKO_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def compute_short_term_score(change_1h: float, change_24h: float) -> float:
    """
    Stima della probabilità di continuità del movimento
    nelle prossime 1–2 ore.

    - 1h = driver principale (80%)
    - 24h = contesto (20%), limitato per evitare distorsioni
    """

    # contesto limitato per non dominare
    context = max(min(change_24h, 5), -5)

    score = (change_1h * 0.8) + (context * 0.2)
    return score


def probability_from_score(score: float) -> float:
    """
    Converte lo score in probabilità realistica.
    Niente numeri estremi o fuorvianti.
    """
    base = min(abs(score) * 6, 20)  # scala prudente
    return round(55 + base, 1)


def format_coin(coin, score, change_1h, change_24h):
    direction = "up" if score >= 0 else "down"

    return {
        "symbol": coin["symbol"].upper(),
        "price": round(coin["current_price"], 4),
        "probability": probability_from_score(score),
        "change_1h": round(change_1h, 2),
        "change_24h": round(change_24h, 2),
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
        "focus": "Short-term probability (next 1–2h)"
    }

# =========================================================
# RANKING
# =========================================================
@app.get("/ranking/up")
def ranking_up(mode: str = Query("balanced")):
    data = fetch_market_data()
    results = []

    for coin in data:
        c1h = coin.get("price_change_percentage_1h_in_currency") or 0
        c24h = coin.get("price_change_percentage_24h_in_currency") or 0

        score = compute_short_term_score(c1h, c24h)

        if score > 0:
            results.append(format_coin(coin, score, c1h, c24h))

    results.sort(key=lambda x: x["probability"], reverse=True)

    limit = 5 if mode == "balanced" else 3
    return results[:limit]


@app.get("/ranking/down")
def ranking_down(mode: str = Query("balanced")):
    data = fetch_market_data()
    results = []

    for coin in data:
        c1h = coin.get("price_change_percentage_1h_in_currency") or 0
        c24h = coin.get("price_change_percentage_24h_in_currency") or 0

        score = compute_short_term_score(c1h, c24h)

        if score < 0:
            results.append(format_coin(coin, score, c1h, c24h))

    results.sort(key=lambda x: x["probability"], reverse=True)

    limit = 5 if mode == "balanced" else 3
    return results[:limit]
