from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

app = FastAPI()

# =========================
# MOCK DATA
# =========================

CRYPTO_MARKET = [
    {"symbol": "BTC", "price": 90431, "change_1h": 0.03},
    {"symbol": "ETH", "price": 3120, "change_1h": 0.85},
    {"symbol": "SOL", "price": 136.53, "change_1h": 1.05},
    {"symbol": "XRP", "price": 2.12, "change_1h": 0.66},
    {"symbol": "DOGE", "price": 0.141, "change_1h": 0.42},
    {"symbol": "ADA", "price": 0.52, "change_1h": -0.62},
    {"symbol": "AVAX", "price": 38.7, "change_1h": -0.91},
]

STABLECOINS = {"USDT", "USDC", "DAI"}
VOLATILITY_THRESHOLD = {"balanced": 0.3, "aggressive": 0.0}

# =========================
# DEVICE STORAGE (TEMP)
# =========================

REGISTERED_DEVICES: List[Dict] = []

# =========================
# MODELS
# =========================

class DeviceRegistration(BaseModel):
    device_token: str
    mode: str
    notifications_enabled: bool

# =========================
# HELPERS
# =========================

def compute_probability(change):
    return min(95, round(abs(change) * 40, 1))

def explanation_simple(change):
    return (
        "Momentum positivo sostenuto da pressione in acquisto"
        if change > 0
        else "Debolezza di breve periodo con pressione in vendita"
    )

def explanation_technical(change):
    return (
        "Aumento della variazione oraria con volumi coerenti"
        if change > 0
        else "Contrazione del prezzo con incremento della volatilità"
    )

def analyze_market(mode: str):
    results = []
    threshold = VOLATILITY_THRESHOLD.get(mode, 0.3)

    for asset in CRYPTO_MARKET:
        if asset["symbol"] in STABLECOINS:
            continue

        if mode == "balanced" and abs(asset["change_1h"]) < threshold:
            continue

        results.append({
            "symbol": asset["symbol"],
            "price": asset["price"],
            "change_1h": round(asset["change_1h"], 2),
            "probability": compute_probability(asset["change_1h"]),
            "explanation_simple": explanation_simple(asset["change_1h"]),
            "explanation_technical": explanation_technical(asset["change_1h"]),
        })

    return results

# =========================
# API ENDPOINTS
# =========================

@app.get("/ranking/up")
def ranking_up(mode: str = "balanced"):
    data = analyze_market(mode)
    return sorted(
        [x for x in data if x["change_1h"] > 0],
        key=lambda x: x["probability"],
        reverse=True,
    )[:5]

@app.get("/ranking/down")
def ranking_down(mode: str = "balanced"):
    data = analyze_market(mode)
    return sorted(
        [x for x in data if x["change_1h"] < 0],
        key=lambda x: x["probability"],
        reverse=True,
    )[:5]

@app.post("/register-device")
def register_device(device: DeviceRegistration):
    REGISTERED_DEVICES.append({
        "token": device.device_token,
        "mode": device.mode,
        "enabled": device.notifications_enabled,
        "registered_at": datetime.utcnow().isoformat()
    })
    return {"status": "registered"}

@app.get("/devices")
def list_devices():
    return REGISTERED_DEVICES
