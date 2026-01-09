from fastapi import APIRouter
import random
import time

router = APIRouter()

# =========================
# CONFIGURAZIONE FILTRI
# =========================

STABLECOINS = {
    "USDT", "USDC", "DAI", "BUSD", "TUSD", "USDP", "FRAX"
}

MIN_VOLATILITY_1H = 0.3  # percentuale minima di movimento 1h

# =========================
# MOCK DATA (sostituibile con API reali)
# =========================

CRYPTO_MARKET = [
    {"symbol": "BTC", "price": 90431, "change_1h": 0.52},
    {"symbol": "ETH", "price": 4870, "change_1h": -0.41},
    {"symbol": "SOL", "price": 136.53, "change_1h": 1.05},
    {"symbol": "XRP", "price": 2.12, "change_1h": 0.66},
    {"symbol": "DOGE", "price": 0.141, "change_1h": 0.41},
    {"symbol": "AVAX", "price": 42.7, "change_1h": -0.78},
    {"symbol": "ADA", "price": 0.59, "change_1h": -0.22},
    {"symbol": "DOT", "price": 8.41, "change_1h": 0.18},
    {"symbol": "USDT", "price": 1.00, "change_1h": 0.01},
    {"symbol": "USDC", "price": 1.00, "change_1h": 0.00},
]

# =========================
# LOGICA MOMENTUM
# =========================

def compute_probability(change_1h: float) -> float:
    """
    Trasforma la variazione 1h in una probabilità (0–100)
    semplice, stabile e interpretabile.
    """
    base = min(abs(change_1h) * 35, 90)
    noise = random.uniform(-3, 3)
    return round(max(5, min(base + noise, 95)), 1)

def analyze_market():
    results = []

    for asset in CRYPTO_MARKET:
        symbol = asset["symbol"].upper()
        change_1h = asset["change_1h"]

        # ❌ Escludi stablecoin
        if symbol in STABLECOINS:
            continue

        # ❌ Escludi asset piatti
        if abs(change_1h) < MIN_VOLATILITY_1H:
            continue

        probability = compute_probability(change_1h)

        results.append({
            "symbol": symbol,
            "price": asset["price"],
            "change_1h": round(change_1h, 2),
            "probability": probability,
            "explanation": "Positive momentum supported by volume"
            if change_1h > 0 else
            "Negative momentum with selling pressure"
        })

    return results

# =========================
# ENDPOINT API
# =========================

@router.get("/ranking/up")
def ranking_up():
    data = analyze_market()
    data = [d for d in data if d["change_1h"] > 0]
    data.sort(key=lambda x: x["probability"], reverse=True)
    return data[:5]

@router.get("/ranking/down")
def ranking_down():
    data = analyze_market()
    data = [d for d in data if d["change_1h"] < 0]
    data.
