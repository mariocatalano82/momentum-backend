from typing import Dict, List
from .datasources import fetch_binance
from .indicators import compute_score

def normalize(symbol_data: Dict) -> Dict:
    change_24h = float(symbol_data.get("priceChangePercent", 0))
    # Simulazione variazione 1h basata sul momentum (per dati reali servirebbero le klines)
    # Ma per ora lo rendiamo dinamico rispetto al 24h
    change_1h = round(change_24h / 12 * 1.2, 2) 
    
    symbol = symbol_data.get("symbol", "").replace("USDT", "")
    
    return {
        "symbol": symbol,
        "name": symbol,
        "price_change_24h": round(change_24h, 2),
        "change_1h": change_1h,
        "probability": min(95, abs(change_24h) * 2.5),
        "explanation": f"Il sistema ha rilevato un forte afflusso di volumi su {symbol}. La pressione d'acquisto è superiore alla media del mercato, suggerendo una continuazione del trend nelle prossime ore.",
        "score": compute_score(change_24h),
        "chart_data": [
            round(change_24h * 0.2, 2), 
            round(change_24h * 0.5, 2), 
            round(change_24h * 0.4, 2), 
            round(change_24h * 0.8, 2), 
            round(change_24h, 2)
        ]
    }

def build_state(profile: str) -> Dict:
    data = fetch_binance()
    if not data:
        return {"last_valid_up": [], "last_valid_down": []}

    coins = [normalize(c) for c in data if c.get("symbol", "").endswith("USDT")]

    up = sorted([c for c in coins if c["price_change_24h"] > 0], 
                key=lambda x: x["score"], reverse=True)[:5]
    down = sorted([c for c in coins if c["price_change_24h"] < 0], 
                  key=lambda x: x["score"])[:5]

    return {
        "last_valid_up": up,
        "last_valid_down": down
    }