from fastapi import FastAPI
import datasources
import time
import math

app = FastAPI()

def generate_tech_explanation(val_24h, profile, symbol):
    intensity = "elevata" if abs(val_24h) > 5 else "moderata"
    context_24h = "accumulo" if val_24h > 0 else "distribuzione"
    
    if profile == "aggressive":
        msg = f"STRATEGIA AGGRESSIVE: {symbol} mostra volatilità {intensity}. "
        msg += f"Il trend di {context_24h} nelle 24h suggerisce operazioni rapide."
    else:
        msg = f"ANALISI BALANCED: {symbol} in fase di {context_24h} {intensity}. "
        msg += "Il momentum attuale richiede una gestione prudente."
    return msg

def calculate_credible_probability(c_24h, vol, profile):
    # Logica non lineare per percentuali realistiche
    base = abs(c_24h) * 5 
    vol_factor = 1.2 if vol > 1000000 else 0.8
    prob = (base * vol_factor)
    prob = 100 / (1 + math.exp(-prob / 15))
    final_prob = 60 + (prob * 0.3)
    if profile == "balanced": final_prob -= 5
    return round(min(final_prob, 93.5), 1)

@app.get("/ranking/state")
def get_state(profile: str = "balanced"):
    try:
        raw_data = datasources.get_crypto_data()
        results = []
        
        if not raw_data:
            return {"market_state": "neutral", "last_valid_up": [], "last_valid_down": []}

        for coin in raw_data:
            # Recupero sicuro dei dati dal dizionario originale
            # Usiamo i nomi esatti che arrivano da datasources.py
            c_24h = float(coin.get('price_change_percentage_24h', 0) or 0)
            vol = float(coin.get('volume_usd', 0) or 0)
            sym = str(coin.get('symbol', '???')).upper()
            name = str(coin.get('name', sym)).upper()
            
            prob = calculate_credible_probability(c_24h, vol, profile)
            
            results.append({
                "symbol": sym,
                "name": name,
                "price_change_24h": round(c_24h, 2),
                "probability": prob,
                "prediction": "UP" if c_24h > 0 else "DOWN",
                "explanation": generate_tech_explanation(c_24h, profile, sym),
                "score": prob if c_24h > 0 else -prob
            })

        top_up = sorted([c for c in results if c['prediction'] == "UP"], key=lambda x: x['score'], reverse=True)[:5]
        top_down = sorted([c for c in results if c['prediction'] == "DOWN"], key=lambda x: x['score'])[:5]

        return {
            "market_state": "bullish" if len(top_up) >= 3 else "neutral",
            "last_valid_up": top_up,
            "last_valid_down": top_down,
            "profile_active": profile,
            "last_update": time.time()
        }
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return {"error": str(e), "last_valid_up": [], "last_valid_down": []}