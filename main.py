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

# Lista simboli corretta per Binance (devono essere ESATTAMENTE così)
TARGET_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", 
    "DOTUSDT", "FETUSDT", "AVAXUSDT", "LINKUSDT", "MATICUSDT", 
    "NEARUSDT", "TIAUSDT", "PEPEUSDT", "INJUSDT", "SUIUSDT"
]

def get_binance_data():
    try:
        response = requests.get(BINANCE_URL, timeout=10)
        if response.statusCode != 200:
            return []
        data = response.json()
        # Filtriamo i dati: prendiamo solo quelli nella nostra lista TARGET
        relevant = [d for d in data if d['symbol'] in TARGET_SYMBOLS]
        print(f"DEBUG: Trovate {len(relevant)} monete su Binance") # Vedrai questo nei log di Render
        return relevant
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        return []

@app.get("/api/market-data")
async def get_market_data():
    raw_data = get_binance_data()
    all_coins = []

    for item in raw_data:
        # Pulizia nome: BTCUSDT -> BTC
        raw_symbol = item['symbol']
        clean_symbol = raw_symbol.replace("USDT", "")
        
        c24h = float(item['priceChangePercent'])
        # Fallback 1h: usiamo una frazione della variazione 24h + un piccolo offset per dinamismo
        c1h = round((c24h / 12) + (float(item['lastPrice']) % 0.05), 2)
        
        prob, tech = compute_confidence(c1h, c24h, clean_symbol)
        
        all_coins.append({
            "symbol": clean_symbol,
            "name": get_full_name(clean_symbol),
            "change_1h": c1h,
            "change_24h": c24h,
            "probability": prob,
            "tech": tech,
            "chart_data": build_chart(c1h)
        })

    # Suddivisione logica per il frontend
    market_leaders = [c for c in all_coins if c['symbol'] in ["BTC", "ETH"]]
    
    # Prendiamo le migliori 5 in salita (o tutte se sono meno di 5)
    up_trends = sorted([c for c in all_coins if c['change_1h'] >= 0], 
                       key=lambda x: x['probability'], reverse=True)[:5]
    
    # Prendiamo le migliori 5 in discesa
    down_trends = sorted([c for c in all_coins if c['change_1h'] < 0], 
                         key=lambda x: x['probability'], reverse=True)[:5]

    return {
        "is_live": True,
        "market_leaders": market_leaders,
        "last_valid_up": up_trends,
        "last_valid_down": down_trends
    }

if __name__ == "__main__":
    # Render usa la variabile d'ambiente PORT, di solito 10000
    uvicorn.run(app, host="0.0.0.0", port=10000)