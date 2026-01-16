from fastapi import FastAPI
from app.indicators import compute_confidence, get_full_name, build_chart

app = FastAPI()

@app.get("/api/market-data")
async def get_market_data():
    # ... qui avrai la tua logica che recupera i dati da Binance ...
    # Esempio di ciclo di formattazione:
    
    processed_list = []
    for raw_coin in binance_results:
        symbol = raw_coin['symbol'].replace("USDT", "")
        c1h = float(raw_coin['change_1h'])
        c24h = float(raw_coin['change_24h'])
        
        prob, tech_data = compute_confidence(c1h, c24h, symbol)
        
        processed_list.append({
            "symbol": symbol,
            "name": get_full_name(symbol), # Recupera il nome completo
            "change_1h": c1h,
            "change_24h": c24h,
            "probability": prob,
            "tech": tech_data, # Contiene human_advice
            "chart_data": build_chart(c1h)
        })
    
    return processed_list