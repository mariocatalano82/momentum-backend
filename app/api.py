import os
import json
import time
import random
import requests
from typing import List
from fastapi import FastAPI, Body, Query
from fastapi.middleware.cors import CORSMiddleware

from google.oauth2 import service_account
from google.auth.transport.requests import Request

# =========================================================
# APP
# =========================================================
app = FastAPI(
    title="Momentum Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# FCM CONFIG (HTTP v1)
# =========================================================
SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT")
if not SERVICE_ACCOUNT_JSON:
    raise RuntimeError("FIREBASE_SERVICE_ACCOUNT not configured")

SERVICE_ACCOUNT_INFO = json.loads(SERVICE_ACCOUNT_JSON)
PROJECT_ID = SERVICE_ACCOUNT_INFO["project_id"]

SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]
FCM_ENDPOINT = (
    f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"
)

# =========================================================
# STATE (volatile – ok per ora)
# =========================================================
REGISTERED_DEVICES: List[str] = []

CRYPTO_LIST = [
    "BTC", "ETH", "SOL", "XRP", "ADA",
    "DOGE", "AVAX", "LINK", "DOT", "MATIC"
]

# =========================================================
# HELPERS
# =========================================================
def get_access_token() -> str:
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO, scopes=SCOPES
    )
    credentials.refresh(Request())
    return credentials.token


def generate_ranking(direction: str, mode: str):
    """
    direction: 'up' | 'down'
    mode: 'balanced' | 'aggressive'
    """

    count = 5 if mode == "balanced" else random.randint(2, 4)

    selected = random.sample(CRYPTO_LIST, count)
    data = []

    for symbol in selected:
        prob = random.uniform(55, 75) if direction == "up" else random.uniform(55, 75)
        change = random.uniform(0.5, 3.5)
        if direction == "down":
            change *= -1

        data.append({
            "symbol": symbol,
            "probability": round(prob, 1),
            "change_1h": round(change, 2),
            "explanation_simple": (
                "Strong buying pressure detected"
                if direction == "up"
                else "Selling pressure increasing"
            ),
            "explanation_technical": (
                "RSI trend + volume confirmation"
                if direction == "up"
                else "Bearish divergence on momentum indicators"
            )
        })

    return data


# =========================================================
# HEALTH
# =========================================================
@app.get("/")
def root():
    return {"status": "Momentum backend running"}

# =========================================================
# RANKING
# =========================================================
@app.get("/ranking/up")
def ranking_up(mode: str = Query("balanced")):
    return generate_ranking("up", mode)


@app.get("/ranking/down")
def ranking_down(mode: str = Query("balanced")):
    return generate_ranking("down", mode)

# =========================================================
# DEVICES
# =========================================================
@app.post("/register-device")
def register_device(payload: dict = Body(...)):
    token = payload.get("device_token")
    if not token:
        return {"error": "Missing device_token"}

    if token not in REGISTERED_DEVICES:
        REGISTERED_DEVICES.append(token)

    return {"registered_devices": len(REGISTERED_DEVICES)}


@app.get("/devices")
def list_devices():
    return REGISTERED_DEVICES

# =========================================================
# NOTIFY (TEST)
# =========================================================
@app.post("/notify-test")
def notify_test():
    if not REGISTERED_DEVICES:
        return {"error": "No registered devices"}

    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; UTF-8",
    }

    results = []

    for token in REGISTERED_DEVICES:
        message = {
            "message": {
                "token": token,
                "notification": {
                    "title": "Momentum 🔔",
                    "body": "Nuove opportunità di mercato disponibili",
                },
                "data": {
                    "type": "ranking_update",
                    "ts": str(int(time.time()))
                },
                "android": {
                    "priority": "HIGH"
                }
            }
        }

        r = requests.post(
            FCM_ENDPOINT,
            headers=headers,
            json=message,
            timeout=10
        )

        try:
            body = r.json()
        except Exception:
            body = r.text

        results.append({
            "status": r.status_code,
            "response": body
        })

    return {"results": results}
