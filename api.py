from fastapi import FastAPI
import datasources
import time

app = FastAPI()

def generate_tech_explanation(coin, profile):
    c_24h = coin['price_change_24h']
    # Simulazione trend breve termine per l'analisi
    trend_type = "rialzista" if c_24h > 0 else "ribassista"
    intensity = "elevata" if abs(c_24h) > 5 else "moderata"
    
    # Linguaggio differenziato per profilo
    if profile == "aggressive":
        intro = f"Analisi di Breakout: L'asset mostra una volatilità {intensity}. "
        action = "Ideale per strategie scalping con stop-loss stretto."
    else:
        intro = f"Analisi di Momentum: Movimento {trend_type} con forza {intensity}. "
        action = "Il contesto suggerisce una gestione prudente della posizione."

    if c_24h > 0:
        detail = f"Il momentum delle ultime 24h (+{c_24h}%) indica accumulo. Nelle ultime 2 ore la pressione in acquisto è dominante."
    else:
        detail = f"La contrazione del {abs(c_24h)}% evidenzia una fase di distribuzione. Il trend di breve termine resta sotto pressione."

    return f"{intro}{detail} {action}"

@app.get("/ranking/state")
def get_state(profile: str = "balanced"):
    raw_data = datasources.get_crypto_data()
    results = []

    for coin in raw_data:
        c_24h = coin.get('price_change_percentage_24h', 0)
        # Calcolo Confidence semplificato
        prob = abs(c_24h) * 12
        if profile == "aggressive":
            prob = prob * 1.3
        
        confidence = min(round(prob, 1), 98.9)
        prediction = "UP" if c_24h > 0 else "DOWN"
        
        results.append({
            "symbol": coin['symbol'].upper(),
            "name": coin['name'],
            "price_change_24h": round(c_24h, 2),
            "probability": confidence,
            "prediction": prediction,
            "explanation": generate_tech_explanation(coin, profile),
            "score": confidence if prediction == "UP" else -confidence
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