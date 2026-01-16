import uvicorn
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.indicators import compute_confidence, get_full_name, build_chart

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BINANCE_URL = "https://api.binance.com/api/3/ticker/24hr"
SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOTUSDT", "FETUSDT", "AVAXUSDT", "LINKUSDT", "MATICUSDT", "NEARUSDT", "TIAUSDT", "PEPEUSDT"]

def get_binance_data():
    try:
        response = requests.get(BINANCE_URL)
        data = response.json()
        relevant = [d for d in data if d['symbol'] in SYMBOLS]
        return relevant
    except Exception:
        return []

@app.get("/api/market-data")
async def get_market_data():
    raw_data = get_binance_data()
    all_coins = []

    for item in raw_data:
        symbol = item['symbol'].replace("USDT", "")
        # Simulazione variazione 1h basata sulla volatilità per il calcolo (Binance non dà 1h nativo su 24h ticker)
        c24h = float(item['priceChangePercent'])
        c1h = round(c24h / 12 + (float(item['lastPrice']) % 0.1), 2) # Algoritmo di fallback per simulare 1h
        
        prob, tech = compute_confidence(c1h, c24h, symbol)
        
        all_coins.append({
            "symbol": symbol,
            "name": get_full_name(symbol),
            "change_1h": c1h,
            "change_24h": c24h,
            "probability": prob,
            "tech": tech,
            "chart_data": build_chart(c1h)
        })

    # Ordinamento per sezioni
    market_leaders = [c for c in all_coins if c['symbol'] in ["BTC", "ETH"]]
    up_trends = sorted([c for c in all_coins if c['change_1h'] > 0], key=lambda x: x['probability'], reverse=True)[:5]
    down_trends = sorted([c for c in all_coins if c['change_1h'] < 0], key=lambda x: x['probability'], reverse=True)[:5]

    return {
        "is_live": True,
        "market_leaders": market_leaders,
        "last_valid_up": up_trends,
        "last_valid_down": down_trends
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)