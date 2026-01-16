import uvicorn
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.indicators import compute_confidence, get_full_name, build_chart

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SYMBOLS = ["BTC", "ETH", "SOL", "XRP", "ADA", "DOT", "FET", "AVAX", "LINK", "MATIC", "NEAR", "TIA", "PEPE", "INJ", "SUI"]
last_valid_cache = None

def fetch_primary():
    try:
        r = requests.get("https://api.binance.com/api/3/ticker/24hr", timeout=4)
        if r.status_code == 200:
            target = [s + "USDT" for s in SYMBOLS]
            return [{"s": i['symbol'].replace("USDT", ""), "p": float(i['lastPrice']), "c": float(i['priceChangePercent'])} for i in r.json() if i['symbol'] in target], True
    except: return [], False

def fetch_fallback():
    try:
        pairs = ",".join([f"{s}USD" for s in SYMBOLS if s != "PEPE"])
        r = requests.get(f"https://api.kraken.com/0/public/Ticker?pair={pairs}", timeout=3)
        if r.status_code == 200:
            res = r.json()['result']
            return [{"s": k.replace("ZUSD","").replace("XBT","BTC").replace("USD",""), "p": float(v['c'][0]), "c": (float(v['p'][0])/float(v['o'])-1)*100 if float(v['o'])!=0 else 0} for k,v in res.items()], True
    except: return [], False

@app.get("/api/market-data")
async def get_market_data():
    global last_valid_cache
    raw, success = fetch_primary()
    if not success: raw, success = fetch_fallback()
    
    if not success and last_valid_cache: return last_valid_cache

    processed = []
    for i in raw:
        c1h = round((i['c'] / 12) + (i['p'] % 0.04), 2)
        prob, tech = compute_confidence(c1h, i['c'], i['s'])
        processed.append({
            "symbol": i['s'], "name": get_full_name(i['s']),
            "change_1h": c1h, "change_24h": round(i['c'], 2),
            "probability": prob, "tech": tech, "chart_data": build_chart(c1h)
        })

    response = {
        "is_live": success,
        "market_leaders": [x for x in processed if x['symbol'] in ["BTC", "ETH"]],
        "last_valid_up": sorted([x for x in processed if x['change_1h'] >= 0], key=lambda x: x['probability'], reverse=True)[:5],
        "last_valid_down": sorted([x for x in processed if x['change_1h'] < 0], key=lambda x: x['probability'], reverse=True)[:5]
    }
    if success:
        last_valid_cache = response.copy()
        last_valid_cache["is_live"] = False
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)