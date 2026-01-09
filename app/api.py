from fastapi import APIRouter
import random

router = APIRouter()

# =========================
# CONFIG
# =========================

STABLECOINS = {
    "USDT", "USDC", "DAI", "BUSD", "TUSD", "USDP", "FRAX"
}

MIN_VOLATILITY_1H = 0.3  # %

# =========================
# MOCK MARKET DATA
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
]

# =========================
# MOMENTUM LOGIC
# =========================

def compute_probability(change_1h: float) -> float:
    base = min(abs(change_1h) * 35, 90)
    noise = random.uniform(-4, 4)
    return round(max(5, min(base + noise, 95)), 1)

def explanation_simple(change_1h: float) -> str:
    if change_1h > 0:
        return "Momentum positivo supportato da pressione in acquisto"
    else:
        return "Momentum negativo con prevalenza di vendite"

def explanation_technical(change_1h: float) -> str:
    intensity = abs(change_1h)

    if intensity > 1.0:
        strength = "movimento forte"
    elif intensity > 0.6:
        strength = "movimento moderato"
    else:
        strength = "movimento iniziale"

    direction = "rialzista" if change_1h > 0 else "ribassista"

    templates = [
        f"{direction.capitalize()} {strength} nell’ultima ora",
        f"Variazione {direction} ({change_1h:+.2f}%) su timeframe 1h",
        f"Accelerazione {direction} con volatilità superiore alla media",
    ]

    return random.choice(templates)

def analyze_market():
    results = []

    for asset in CRYPTO_MARKET:
        symbol = asset["symbol"].upper()
        change_1h = asset["change_1h"]

        if symbol in STABLECOINS:
            continue

        if abs(change_1h) < MIN_VOLATILITY_1H:
            continue

        probability = compute_probability(change_1h)

        results.append({
            "symbol": symbol,
            "price": asset["price"],
            "change_1h": round(change_1h, 2),
            "probability": probability,
            # 🔹 S
            "explanation_simple": explanation_simple(change_1h),
            # 🔹 T
            "explanation_technical": explanation_technical(change_1h),
        })

    return results

# =========================
# API ENDPOINTS
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
    data.sort(key=lambda x: x["probability"], reverse=True)
    return data[:5]
