import os
import requests
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Momentum Backend")

FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY")

REGISTERED_DEVICES: list[str] = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

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

@app.post("/notify-test")
def notify_test():
    if not REGISTERED_DEVICES:
        return {"error": "No registered devices"}

    if not FCM_SERVER_KEY:
        return {"error": "FCM_SERVER_KEY not configured"}

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
    }

    try:
        r = requests.post(
            "https://fcm.googleapis.com/fcm/send",
            headers=headers,
            json=payload,
            timeout=10
        )

        # ⚠️ NON assumiamo che sia JSON
        try:
            response_body = r.json()
        except Exception:
            response_body = r.text

        return {
            "fcm_status": r.status_code,
            "fcm_response": response_body
        }

    except Exception as e:
        return {
            "error": "FCM request failed",
            "detail": str(e)
        }
