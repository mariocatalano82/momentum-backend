from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "online", "service": "Momentum Pro API"}

@app.get("/api/momentum")
def get_momentum():
    return [
        {"symbol": "BTC", "name": "Bitcoin", "confidence": 88, "change_24h": 2.45, "momentum_speed": 1.1, "description": "Strong bullish momentum detected on 4h timeframe."},
        {"symbol": "ETH", "name": "Ethereum", "confidence": 75, "change_24h": 1.12, "momentum_speed": 0.8, "description": "Stable growth with increasing volume."}
    ]

@app.get("/api/history")
def get_history():
    return [
        {"symbol": "BTC", "status": "HIT", "result_percent": "+5.40", "date": "12 Jan"},
        {"symbol": "ETH", "status": "HIT", "result_percent": "+3.12", "date": "11 Jan"},
        {"symbol": "SOL", "status": "MISS", "result_percent": "-1.20", "date": "10 Jan"},
        {"symbol": "DOT", "status": "HIT", "result_percent": "+4.25", "date": "09 Jan"},
        {"symbol": "LINK", "status": "HIT", "result_percent": "+6.80", "date": "08 Jan"}
    ]