from fastapi import FastAPI
import datasources
import time

app = FastAPI()

def generate_tech_explanation(coin, profile):
    c_24h = coin['price_change_percentage_24h']
    intensity = "elevata" if abs(c_24h) > 5 else "moderata"
    
    if profile == "aggressive":
        intro = f"Analisi Breakout: Volatilità {intensity}. "
        action = "Ideale per strategie scalping ad alto rischio."
    else:
        intro = f"Analisi Momentum: Forza {intensity}. "
        action = "Suggerita gestione prudente della posizione."

    detail = f"Il movimento di {round(c_24h, 2)}% nelle 24h indica una fase di {'accumulo' if c_24h > 0 else 'distribuzione'}."
    return f"{intro} {detail} {action}"

@app.get("/ranking/state")
def get_state(profile: str = "balanced"):
    raw_data = datasources.get_crypto_data()
    results = []

    for coin in raw_data:
        c_24h = coin.get('price_change_percentage_24h', 0)
        # Calcolo Confidence coerente
        prob = min(round(abs(c_24h) * 12 * (1.3 if profile == "aggressive" else 0.8), 1), 98.9)
        pred = "UP" if c_24h > 0 else "DOWN"
        
        results.append({
            "symbol": coin['symbol'].upper(),
            "name": coin['name'],
            "price_change_24h": round(c_24h, 2),
            "probability": prob,
            "prediction": pred,
            "explanation": generate_tech_explanation(coin, profile),
            "score": prob if pred == "UP" else -prob
        })

    top_up = sorted([c for c in results if c['prediction'] == "UP"], key=lambda x: x['score'], reverse=True)[:5]
    top_down = sorted([c for c in results if c['prediction'] == "DOWN"], key=lambda x: x['score'])[:5]

    return {
        "market_state": "bullish" if len(top_up) > 3 else "neutral",
        "last_valid_up": top_up,
        "last_valid_down": top_down,
        "profile_active": profile,
        "last_update": time.time()
    }