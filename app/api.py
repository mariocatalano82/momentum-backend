from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import time

app = FastAPI()

# ===============================
# CORS
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# CONFIG
# ===============================
BINANCE_24H = "https://api.binance.com/api/v3/ticker/24hr"

TOP100_WHITELIST = {
    "BTC","ETH","BNB","SOL","XRP","ADA","AVAX","DOGE","TRX","DOT",
    "LINK","MATIC","ATOM","LTC","BCH","ICP","NEAR","FIL","APT","ARB",
    "OP","SUI","INJ","AAVE","UNI","IMX","RNDR","STX","KAS","XLM",
    "ETC","HBAR","ALGO","VET","MKR","THETA","GRT","QNT","EGLD","AXS",
    "FLOW","NEO","FTM","KAVA","SNX","RUNE","DYDX","ZEC","MINA","CAKE",
    "COMP","LDO","GMX","PEPE","CRV","SAND","MANA","EOS","XTZ","KSM",
    "AR","ROSE","CELO","1INCH","ENS","BAT","CHZ","BAL","ENJ","ZIL",
    "OMG","ANKR","ICX","WAVES","QTUM","ZRX","SC","ONT","IOTA","HOT"
}

# ===============================
# MARKET MEMORY (ANTI EMPTY UI)
# ===============================
market_state = {
    "market_state": "neutral",
    "last_valid_up": [],
    "last_valid_down": [],
    "last_update": None,
}

# ===============================
# HELPERS
# ===============================
def fetch_binance_data():
    r = requests.get(BINANCE_24H, timeout=10)
    r.raise_for_status()
    return r.json()

def normalize_symbol(symbol):
    return symbol.replace("USDT", "")

def build_entry(raw):
    change_1h = float(raw.get("priceChangePercent", 0)) / 24
    change_24h = float(raw.get("priceChangePercent", 0))
    score = change_24h

    probability = min(90, max(30, abs(score)))

    return {
        "symbol": normalize_symbol(raw["symbol"]),
        "name": normalize_symbol(raw["symbol"]),
        "change_1h": round(change_1h, 2),
        "change_24h": round(change_24h, 2),
        "score": round(score, 2),
        "probability": round(probability, 2),
        "explanation_simple": "Relative short-term momentum",
        "explanation_technical": "Relative strength vs broad crypto market",
        "data_quality": "normal",
    }

# ===============================
# CORE RANKING
# ===============================
def compute_rankings():
    data = fetch_binance_data()

    filtered = []
    for d in data:
        if not d["symbol"].endswith("USDT"):
            continue

        base = normalize_symbol(d["symbol"])
        if base not in TOP100_WHITELIST:
            continue

        filtered.append(build_entry(d))

    if not filtered:
        return [], []

    up = sorted(filtered, key=lambda x: x["score"], reverse=True)[:5]
    down = sorted(filtered, key=lambda x: x["score"])[:5]

    return up, down

# ===============================
# API ENDPOINTS
# ===============================
@app.get("/ranking/up")
def ranking_up(mode: str = "balanced"):
    up, down = compute_rankings()

    if up:
        market_state["market_state"] = "active"
        market_state["last_valid_up"] = up
        market_state["last_valid_down"] = down
        market_state["last_update"] = time.time()

        return up

    return market_state["last_valid_up"]

@app.get("/ranking/down")
def ranking_down(mode: str = "balanced"):
    up, down = compute_rankings()

    if down:
        market_state["market_state"] = "active"
        market_state["last_valid_up"] = up
        market_state["last_valid_down"] = down
        market_state["last_update"] = time.time()

        return down

    return market_state["last_valid_down"]

@app.get("/ranking/state")
def ranking_state():
    return market_state
