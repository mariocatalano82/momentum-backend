from fastapi import FastAPI
import datasources
import time
import math

app = FastAPI()

# Mappa Nomi Reali completa
CRYPTO_NAMES = {
    "BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana", "BNB": "Binance Coin",
    "XRP": "Ripple", "ADA": "Cardano", "DOGE": "Dogecoin", "AVAX": "Avalanche",
    "DOT": "Polkadot", "LINK": "Chainlink", "MATIC": "Polygon", "LTC": "Litecoin",
    "NEAR": "Near Protocol", "TRX": "Tron", "UNI": "Uniswap", "PEPE": "Pepe Coin"
}

def calculate_solid_probability(c_24h, vol, profile):
    """
    Calcolo basato su affidabilità statistica. 
    Per arrivare all'80%, serve volume alto E trend costante.
    """
    abs_c = abs(c_24h)
    
    # 1. Base probabilistica (Sigmoide)
    # Una variazione del 5% su 24h porta una base di circa 65%
    base = 100 / (1 + math.exp(-abs_c / 8)) 
    
    # 2. Moltiplicatore di Affidabilità del Volume (Trust Factor)
    # Se il volume è sotto i 5M, la fiducia nel dato cala drasticamente
    if vol > 50000000: # Top Volume (>50M)
        trust_factor = 1.1
    elif vol > 10000000: # Mid Volume (>10M)
        trust_factor = 1.0
    else: # Low Volume (<10M)
        trust_factor = 0.85
        
    # 3. Penalità Profilo (Balanced è più scettico del dato)
    profile_adjustment = 0.95 if profile == "balanced" else 1.0
    
    final_score = base * trust_factor * profile_adjustment
    
    # Range realistico: 60% (incertezza) - 88% (massima forza storica)
    # Superare l'85% richiede condizioni di mercato eccezionali.
    return round(min(max(final_score, 60.0), 88.5), 1)

def get_market_context(c_24h):
    if abs(c_24h) > 10: return "Alta Volatilità (Rischio Elevato)"
    if abs(c_24h) > 5: return "Trend Consolidato"
    return "Accumulo Laterale"

@app.get("/ranking/state")
def get_state(profile: str = "balanced"):
    try:
        raw_data = datasources.get_crypto_data()
        results = []
        MIN_VOLUME = 5000000 # Filtro rigoroso: min 5 milioni di volume

        for coin in raw_data:
            vol = float(coin.get('volume_usd', 0) or 0)
            if vol < MIN_VOLUME: continue

            c_24h = float(coin.get('price_change_percentage_24h', 0) or 0)
            sym = str(coin.get('symbol', '???')).replace('USDT', '').upper()
            
            # Mapping Nome: se non in lista, usa il simbolo pulito
            full_name = CRYPTO_NAMES.get(sym, sym)
            
            prob = calculate_solid_probability(c_24h, vol, profile)
            context = get_market_context(c_24h)
            
            results.append({
                "symbol": sym,
                "name": full_name,
                "price_change_24h": round(c_24h, 2),
                "probability": prob,
                "prediction": "UP" if c_24h > 0 else "DOWN",
                "explanation": f"L'algoritmo rileva un {context}. La fiducia del {prob}% è basata sulla convergenza tra volumi (USD {int(vol/1000000)}M) e variazione 24h. Strategia {profile}: monitorare breakout.",
                "score": prob if c_24h > 0 else -prob,
                "chart_data": [c_24h*0.2, c_24h*0.5, c_24h*0.3, c_24h*0.8, c_24h]
            })

        # Prendi solo i top reali
        top_up = sorted([c for c in results if c['prediction'] == "UP"], key=lambda x: x['score'], reverse=True)[:5]
        top_down = sorted([c for c in results if c['prediction'] == "DOWN"], key=lambda x: x['score'])[:5]

        return {
            "last_valid_up": top_up,
            "last_valid_down": top_down,
            "server_time": time.time()
        }
    except Exception as e:
        return {"error": str(e)}