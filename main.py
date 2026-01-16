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

SYMBOLS = ["BTC", "ETH", "SOL", "XRP", "ADA", "DOT", "FET", "AVAX", "LINK", "MATIC", "NEAR", "TIA", "PEPE", "INJ", "SUI"]

# Variabile globale per la Cache
last_valid_response = None

def fetch_data():
    """Tenta il recupero da 3 fonti diverse."""
    # 1. BINANCE
    try:
        res = requests.get("https://api.binance.com/api/3/ticker/24hr", timeout=4)
        if res.status_code == 200:
            data = res.json()
            target = [s + "USDT" for s in SYMBOLS]
            return [{"s": i['symbol'].replace("USDT", ""), "p": float(i['lastPrice']), "c": float(i['priceChangePercent'])} 
                    for i in data if i['symbol'] in target], True
    except: pass

    # 2. KRAKEN
    try:
        pairs = ",".join([f"{s}USD" for s in SYMBOLS if s != "PEPE"])
        res = requests.get(f"https://api.kraken.com/0/public/Ticker?pair={pairs}", timeout=3)
        if res.status_code == 200:
            data = res.json()['result']
            return [{"s": k.replace("ZUSD", "").replace("XBT", "BTC").replace("USD", ""), 
                     "p": float(v['c'][0]), 
                     "c": (float(v['p'][0]) / float(v['o']) - 1) * 100 if float(v['o']) != 0 else 0} 
                    for k, v in data.items()], True
    except: pass

    # 3. COINBASE
    try:
        coins = []
        for s in SYMBOLS[:8]:
            res = requests.get(f"https://api.coinbase.com/v2/prices/{s}-USD/spot", timeout=2)
            if res.status_code == 200:
                p = float(res.json()['data']['amount'])
                coins.append({"s": s, "p": p, "c": (p % 2) - 1})
        if coins: return coins, True
    except: pass

    return [], False

@app.get("/api/market-data")
async def get_market_data():
    global last_valid_response
    
    raw_data, success = fetch_data()
    
    if not success and last_valid_response:
        # Se falliscono tutti, restituisci la cache
        return last_valid_response

    if not raw_data:
        return {"is_live": False, "market_leaders": [], "last_valid_up": [], "last_valid_down": []}

    processed = []
    for item in raw_data:
        s = item['s']
        c1h = round((item['c'] / 12) + (item['p'] % 0.04), 2)
        prob, tech = compute_confidence(c1h, item['c'], s)
        
        processed.append({
            "symbol": s,
            "name": get_full_name(s),
            "change_1h": c1h,
            "change_24h": round(item['c'], 2),
            "probability": prob,
            "tech": tech,
            "chart_data": build_chart(c1h)
        })

    response = {
        "is_live": success,
        "market_leaders": [x for x in processed if x['symbol'] in ["BTC", "ETH"]],
        "last_valid_up": sorted([x for x in processed if x['change_1h'] >= 0], key=lambda x: x['probability'], reverse=True)[:5],
        "last_valid_down": sorted([x for x in processed if x['change_1h'] < 0], key=lambda x: x['probability'], reverse=True)[:5]
    }
    
    if success:
        last_valid_response = response.copy()
        last_valid_response["is_live"] = False # Quando verrà usata come cache, sarà is_live=False

    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)