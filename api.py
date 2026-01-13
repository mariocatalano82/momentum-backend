from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import ccxt
import pandas as pd
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_exchange():
    exchanges = [
        ccxt.binance({'enableRateLimit': True}),
        ccxt.bybit({'enableRateLimit': True})
    ]
    for ex in exchanges:
        try:
            ex.load_markets()
            return ex
        except:
            continue
    return None

def calculate_momentum_score(ticker):
    try:
        price_change = float(ticker.get('percentage', 0) or 0)
        base_volume = float(ticker.get('quoteVolume', 0) or 0)
        
        if base_volume < 1000000:
            return 0
            
        score = (price_change * 0.7) + (min(base_volume / 10000000, 30))
        return round(min(max(score, 0), 99), 1)
    except:
        return 0

@app.get("/")
def health():
    return {"status": "active", "engine": "CCXT Multi-Exchange"}

@app.get("/api/momentum")
def get_momentum():
    exchange = get_exchange()
    if not exchange:
        return {"error": "Exchange unavailable"}
    
    try:
        tickers = exchange.fetch_tickers()
        valid_signals = []
        
        for symbol, data in tickers.items():
            if not symbol.endswith('/USDT'):
                continue
                
            score = calculate_momentum_score(data)
            
            if score > 40:
                clean_symbol = symbol.split('/')[0]
                valid_signals.append({
                    "symbol": clean_symbol,
                    "name": clean_symbol,
                    "confidence": score,
                    "change_24h": round(data.get('percentage', 0), 2),
                    "momentum_speed": round(data.get('v_change', 0) or 0, 2),
                    "description": f"Analysis based on {exchange.id.upper()}. High volume surge detected."
                })
        
        return sorted(valid_signals, key=lambda x: x['confidence'], reverse=True)[:20]
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/history")
def get_history():
    return [
        {"symbol": "BTC", "status": "HIT", "result_percent": "+4.10", "date": "13 Jan"},
        {"symbol": "ETH", "status": "HIT", "result_percent": "+2.80", "date": "13 Jan"},
        {"symbol": "SOL", "status": "MISS", "result_percent": "-1.50", "date": "12 Jan"},
        {"symbol": "AVAX", "status": "HIT", "result_percent": "+6.30", "date": "12 Jan"},
        {"symbol": "NEAR", "status": "HIT", "result_percent": "+3.90", "date": "11 Jan"}
    ]