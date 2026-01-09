import os
import json
import time
import requests
from typing import List
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

from google.oauth2 import service_account
from google.auth.transport.requests import Request

# =========================================================
# APP
# =========================================================
app = FastAPI(title="Momentum Backend (FCM v1)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# CONFIG
# =========================================================
# Env var che contiene IL JSON COMPLETO del Service Account
SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT")

if not SERVICE_ACCOUNT_JSON:
    raise RuntimeError("FIREBASE_SERVICE_ACCOUNT not configured")

SERVICE_ACCOUNT_INFO = json.loads(SERVICE_ACCOUNT_JSON)

PROJECT_ID = SERVICE_ACCOUNT_INFO.get("project_id")
if not PROJECT_ID:
    raise RuntimeError("project_id missing in service account")

FCM_V1_ENDPOINT = (
    f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"
)

SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

# =========================================================
# STATE (VOLATILE – OK PER TEST)
# =========================================================
REGISTERED_DEVICES: List[str] = []

# =========================================================
# HELPERS
# =========================================================
def get_access_token() -> str:
    """Ottiene un OAuth2 access token per FCM v1."""
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO, scopes=SCOPES
    )
    credentials.refresh(Request())
    return credentials.token

# =========================================================
# HEALTH
# =========================================================
@app.get("/")
def root():
    return {"status": "ok"}

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

    try:
        access_token = get_access_token()
    except Exception as e:
        return {"error": "Failed to get access token", "detail": str(e)}

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
                    "body": "Test notifica push (FCM HTTP v1)",
                },
                "data": {
                    "type": "test",
                    "ts": str(int(time.time())),
                },
                "android": {
                    "priority": "HIGH"
                }
            }
        }

        try:
            r = requests.post(
                FCM_V1_ENDPOINT,
                headers=headers,
                json=message,
                timeout=10,
            )
            try:
                body = r.json()
            except Exception:
                body = r.text

            results.append({
                "token": token[:12] + "...",
                "status": r.status_code,
                "response": body,
            })
        except Exception as e:
            results.append({
                "token": token[:12] + "...",
                "status": "exception",
                "error": str(e),
            })

    return {"results": results}
