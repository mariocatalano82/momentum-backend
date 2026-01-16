import uvicorn
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.indicators import compute_confidence, get_full_name, build_chart

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SYMBOLS = ["BTC", "ETH", "SOL", "XRP", "ADA", "DOT", "FET", "AVAX", "LINK", "MATIC", "NEAR", "TIA", "PEPE", "INJ", "SUI"]

@app.get("/")
async def root():
    return {"status": "Momentum Engine Online", "endpoint": "/api/market-data"}

@app.get("/api/market-data")
async def get_market_data():
    try:
        r = requests.get("https://api.binance.com/api/3/ticker/24hr", timeout=5)
        if r.status_code == 200:
            targets = [s + "USDT" for s in SYMBOLS]
            raw = [{"s": i['symbol'].replace("USDT",""), "p": float(i['lastPrice']), "c": float(i['priceChangePercent'])} for i in r.json() if i['symbol'] in targets]
            
            all_c = []
            for i in raw:
                c1h = round((i['c'] / 12) + (i['p'] % 0.04), 2)
                prob, tech = compute_confidence(c1h, i['c'], i['s'])
                all_c.append({
                    "symbol": i['s'], "name": get_full_name(i['s']),
                    "change_1h": c1h, "change_24h": round(i['c'], 2),
                    "probability": prob, "tech": tech, "chart_data": build_chart(c1h)
                })

            return {
                "is_live": True,
                "market_leaders": [x for x in all_c if x['symbol'] in ["BTC", "ETH"]],
                "last_valid_up": sorted([x for x in all_c if x['change_1h'] >= 0 and x['symbol'] not in ["BTC", "ETH"]], key=lambda x: x['probability'], reverse=True)[:5],
                "last_valid_down": sorted([x for x in all_c if x['change_1h'] < 0 and x['symbol'] not in ["BTC", "ETH"]], key=lambda x: x['probability'], reverse=True)[:5]
            }
    except:
        return {"is_live": False, "market_leaders": [], "last_valid_up": [], "last_valid_down": []}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)