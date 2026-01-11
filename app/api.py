from fastapi import FastAPI
import time

app = FastAPI()

STATE = {
    "market_state": "active",
    "last_valid_up": [
        {"symbol": "BTC", "name": "Bitcoin"}
    ],
    "last_valid_down": [
        {"symbol": "ETH", "name": "Ethereum"}
    ],
    "last_update": time.time()
}

@app.get("/ranking/state")
def get_state():
    return STATE

@app.get("/ranking/up")
def get_up():
    return STATE["last_valid_up"]

@app.get("/ranking/down")
def get_down():
    return STATE["last_valid_down"]
