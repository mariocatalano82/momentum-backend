import os
import requests
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Momentum Backend",
    description="Ranking, predictions and notifications",
    version="1.0.0"
)

# =========================
# CONFIG
# =========================
FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY")

REGISTERED_DEVICES: list[str] = []

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
# HEALTH CHECK
# =========================
@app.get("/")
def root():
    return {"status": "Momentum backend running"}

# =========================
# DEVICE REGISTRATION
# =========================
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

# =========================
# TEST NOTIFICATION
# =========================
@app.post("/notify-test")
def notify_test():
    if not FCM_SERVER_KEY:
        return {"error": "FCM_SERVER_KEY not configured"}

    if not REGISTERED_DEVICES:
        return {"error": "No registered devices"}

    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "registration_ids": REGISTERED_DEVICES,
        "notification": {
            "title": "Momentum 🔔",
            "body": "Test notifica push riuscito"
        },
        "data": {
            "type": "test"
        }
    }

    r = requests.post(
        "https://fcm.googleapis.com/fcm/send",
        headers=headers,
        json=payload,
        timeout=10
    )

    return {
        "fcm_status": r.status_code,
        "fcm_response": r.json()
    }

# =========================
# MOCK RANKING (ESEMPIO)
# =========================
@app.get("/ranking/up")
def ranking_up():
    return [
        {
            "symbol": "BTC",
            "probability": 72.4,
            "change_1h": 1.2,
            "explanation_simple": "Forte pressione in acquisto",
            "explanation_technical": "RSI crescente, volumi sopra media"
        }
    ]

@app.get("/ranking/down")
def ranking_down():
    return [
        {
            "symbol": "ETH",
            "probability": 68.1,
            "change_1h": -0.9,
            "explanation_simple": "Indebolimento del momentum",
            "explanation_technical": "Divergenza ribassista su MACD"
        }
    ]
