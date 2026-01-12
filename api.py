from fastapi import FastAPI
import datasources
import time

app = FastAPI()

def calculate_confidence(change_24h, change_1h, volume, profile):
    # Logica: Se la variazione 1h è nella stessa direzione della 24h ma più "ripida",
    # il momentum sta accelerando. 
    
    # Peso del volume (più è alto rispetto alla media, più è affidabile)
    vol_factor = 1.2 if volume > 1000000 else 0.8
    
    # Calcolo base della forza
    strength = (change_1h * 0.7) + (change_24h * 0.3)
    
    # Calcolo Confidence (0-100)
    conf = abs(strength) * 15 * vol_factor
    
    # Adattamento al profilo
    if profile == "aggressive":
        conf = conf * 1.2 # Più propenso a dare alte probabilità
    else:
        conf = conf * 0.8 # Più conservativo
        
    return min(round(conf, 1), 99.0)

@app.get("/ranking/state")
def get_state(profile: str = "balanced"):
    raw_data = datasources.get_crypto_data()
    results = []

    for coin in raw_data:
        # Recuperiamo i dati dallo scanner
        c_24h = coin.get('price_change_percentage_24h', 0)
        # Nota: Binance fornisce il 24h, stimiamo il trend 1h per la predizione
        # In una versione pro useremmo dati storici, qui usiamo il trend attuale
        c_1h = c_24h / 24 * 1.5 
        vol = coin.get('volume_usd', 0)

        confidence = calculate_confidence(c_24h, c_1h, vol, profile)
        
        results.append({
            "symbol": coin['symbol'].upper(),
            "name": coin['name'],
            "price_change_24h": round(c_24h, 2),
            "probability": confidence,
            "prediction": "UP" if c_24h > 0 else "DOWN",
            "score": confidence if c_24h > 0 else -confidence
        })

    # Top 5 Momentum Up e Down
    top_up = sorted([c for c in results if c['prediction'] == "UP"], key=lambda x: x['score'], reverse=True)[:5]
    top_down = sorted([c for c in results if c['prediction'] == "DOWN"], key=lambda x: x['score'])[:5]

    return {
        "market_state": "bullish" if len(top_up) > 3 else "neutral",
        "last_valid_up": top_up,
        "last_valid_down": top_down,
        "profile_active": profile,
        "last_update": time.time()
    }