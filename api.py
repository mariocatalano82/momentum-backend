from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import time
import datasources
import indicators
import config

app = FastAPI()

# Permette a Flutter di comunicare con il server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_prediction_data(profile="balanced"):
    try:
        raw_coins = datasources.get_top_50()
        results = []
        
        # Applichiamo i pesi dal file config.py
        w = config.WEIGHTS
        if profile == "aggressive":
            w = {"momentum": 0.5, "volume": 0.2, "rsi": 0.1, "trend": 0.1, "volatility": 0.1}

        for c in raw_coins:
            c_1h = c.get('price_change_percentage_1h_in_currency', 0) or 0
            c_24h = c.get('price_change_percentage_24h_in_currency', 0) or 0
            vol = c.get('total_volume', 0) or 0
            
            # Calcolo degli indicatori basato sui tuoi file .py
            m_score = indicators.momentum(c_1h)
            v_score = indicators.volume_score(vol)
            t_score = indicators.trend_score(c_1h)
            
            # Punteggio finale normalizzato
            score = (m_score * w['momentum']) + (v_score * w['volume']) + (t_score * w['trend'])
            confidence = min(abs(score) * 100, 98.5) # Limite massimo realistico

            results.append({
                "symbol": c['symbol'].upper(),
                "name": c['name'],
                "price": c['current_price'],
                "change_1h": round(c_1h, 2),
                "change_24h": round(c_24h, 2),
                "probability": round(confidence, 1),
                "explanation": f"Basato su momentum ({round(m_score,2)}) e volumi. Trend 1h vs 24h indica una potenziale accelerazione.",
                "score": score
            })
        
        # Ordiniamo per trovare le Top 5 Up e Down
        top_up = sorted(results, key=lambda x: x['score'], reverse=True)[:5]
        top_down = sorted(results, key=lambda x: x['score'])[:5]
        return top_up, top_down
    except Exception as e:
        print(f"Errore: {e}")
        return [], []

@app.get("/ranking/state")
def get_state(profile: str = "balanced"):
    up, down = get_prediction_data(profile)
    return {
        "market_state": "active" if len(up) > 0 else "neutral",
        "last_valid_up": up,
        "last_valid_down": down,
        "last_update": time.time()
    }