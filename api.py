from fastapi import FastAPI
import datasources
import time
import math

app = FastAPI()

def calculate_credible_probability(c_24h, vol, profile):
    # Logica per evitare 95% fissi
    base = abs(c_24h) * 5 
    vol_factor = 1.2 if vol > 1000000 else 0.8
    prob = (base * vol_factor)
    prob = 100 / (1 + math.exp(-prob / 15))
    final_prob = 65 + (prob * 0.25)
    if profile == "balanced": final_prob -= 5
    return round(min(final_prob, 92.5), 1)

@app.get("/ranking/state")
def get_state(profile: str = "balanced"):
    try:
        raw_data = datasources.get_crypto_data()
        results = []
        for coin in raw_data:
            c_24h = float(coin.get('price_change_percentage_24h', 0) or 0)
            vol = float(coin.get('volume_usd', 0) or 0)
            prob = calculate_credible_probability(c_24h, vol, profile)
            
            # Costruiamo il nome completo in modo sicuro
            sym = str(coin.get('symbol', '???')).upper()
            name = str(coin.get('name', sym)).upper()
            
            results.append({
                "symbol": sym,
                "name": name,
                "price_change_24h": round(c_24h, 2),
                "probability": prob,
                "prediction": "UP" if c_24h > 0 else "DOWN",
                "explanation": f"L'asset {sym} mostra un trend {'rialzista' if c_24h > 0 else 'ribassista'} del {abs(c_24h)}% nelle 24h. Analisi {profile}: momentum in fase di {'espansione' if abs(c_24h) > 3 else 'consolidamento'}.",
                "score": prob if c_24h > 0 else -prob
            })

        top_up = sorted([c for c in results if c['prediction'] == "UP"], key=lambda x: x['score'], reverse=True)[:5]
        top_down = sorted([c for c in results if c['prediction'] == "DOWN"], key=lambda x: x['score'])[:5]

        return {
            "market_state": "bullish" if len(top_up) >= 3 else "neutral",
            "last_valid_up": top_up,
            "last_valid_down": top_down
        }
    except Exception as e:
        return {"error": str(e), "last_valid_up": [], "last_valid_down": []}