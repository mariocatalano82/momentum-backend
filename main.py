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

# Endpoint Binance e Simboli
BINANCE_URL = "https://api.binance.com/api/3/ticker/24hr"
TARGET_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOTUSDT", "FETUSDT", "AVAXUSDT", "LINKUSDT", "MATICUSDT", "NEARUSDT", "TIAUSDT", "PEPEUSDT", "INJUSDT", "SUIUSDT"]

@app.get("/api/market-data")
async def get_market_data():
    try:
        response = requests.get(BINANCE_URL, timeout=10)
        if response.status_code != 200:
            return {"error": "Binance unreachable", "market_leaders": [], "last_valid_up": [], "last_valid_down": []}
        
        data = response.json()
        relevant = [d for d in data if d['symbol'] in TARGET_SYMBOLS]
        
        all_coins = []
        for item in relevant:
            raw_symbol = item['symbol']
            clean_symbol = raw_symbol.replace("USDT", "")
            
            # Estrazione dati numerici sicura
            try:
                c24h = float(item.get('priceChangePercent', 0))
                last_price = float(item.get('lastPrice', 0))
                # Simulazione variazione 1h coerente
                c1h = round((c24h / 12) + (last_price % 0.02), 2)
                
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
            except:
                continue

        # Divisione in liste
        market_leaders = [c for c in all_coins if c['symbol'] in ["BTC", "ETH"]]
        up_trends = sorted([c for c in all_coins if c['change_1h'] >= 0], key=lambda x: x['probability'], reverse=True)[:5]
        down_trends = sorted([c for c in all_coins if c['change_1h'] < 0], key=lambda x: x['probability'], reverse=True)[:5]

        return {
            "is_live": True,
            "market_leaders": market_leaders,
            "last_valid_up": up_trends,
            "last_valid_down": down_trends
        }
    except Exception as e:
        return {"error": str(e), "market_leaders": [], "last_valid_up": [], "last_valid_down": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)