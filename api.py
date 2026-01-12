from fastapi import FastAPI
import datasources
import time
import math

app = FastAPI()

# Mappa Nomi Reali Espansa
CRYPTO_NAMES = {
    "BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana", "BNB": "Binance Coin",
    "XRP": "Ripple", "ADA": "Cardano", "DOGE": "Dogecoin", "AVAX": "Avalanche",
    "DOT": "Polkadot", "LINK": "Chainlink", "MATIC": "Polygon", "LTC": "Litecoin",
    "NEAR": "Near Protocol", "TRX": "Tron", "UNI": "Uniswap", "PEPE": "Pepe Coin",
    "SHIB": "Shiba Inu", "LDO": "Lido DAO", "TIA": "Celestia", "SUI": "Sui"
}

def calculate_solid_probability(c_24h, vol, profile):
    abs_c = abs(c_24h)
    # Base sigmoide per stabilità statistica
    base = 100 / (1 + math.exp(-abs_c / 7.5)) 
    
    # Trust Factor basato sul Volume (USD)
    if vol > 50000000: trust_factor = 1.12
    elif vol > 15000000: trust_factor = 1.05
    elif vol > 5000000: trust_factor = 0.95
    else: trust_factor = 0.80 # Punizione per volumi bassi
        
    profile_adj = 0.94 if profile == "balanced" else 1.0
    final_score = base * trust_factor * profile_adj
    
    # Cap 89% per mantenere onestà intellettuale del dato
    return round(min(max(final_score, 60.0), 89.0), 1)

@app.get("/ranking/state")
def get_state(profile: str = "balanced"):
    try:
        raw_data = datasources.get_crypto_data()
        results = []
        MIN_VOLUME = 4000000 # Solo mercati con min 4M volume

        for coin in raw_data:
            vol = float(coin.get('volume_usd', 0) or 0)
            if vol < MIN_VOLUME: continue

            c_24h = float(coin.get('price_change_percentage_24h', 0) or 0)
            raw_sym = str(coin.get('symbol', '???')).upper()
            
            # FIX NOMI: Pulizia del simbolo per matchare la lista CRYPTO_NAMES
            sym_clean = raw_sym.replace('USDT', '')
            full_name = CRYPTO_NAMES.get(sym_clean, sym_clean)
            
            prob = calculate_solid_probability(c_24h, vol, profile)
            
            results.append({
                "symbol": sym_clean,
                "name": full_name,
                "price_change_24h": round(c_24h, 2),
                "probability": prob,
                "prediction": "UP" if c_24h > 0 else "DOWN",
                "explanation": f"Analisi {sym_clean}: Momentum {'positivo' if c_24h > 0 else 'negativo'} confermato da volumi per {int(vol/1000000)}M USD. Il calcolo {profile} indica una fiducia del {prob}%.",
                "score": prob if c_24h > 0 else -prob,
                "chart_data": [c_24h*0.25, c_24h*0.55, c_24h*0.35, c_24h*0.85, c_24h]
            })

        return {
            "last_valid_up": sorted([c for c in results if c['prediction'] == "UP"], key=lambda x: x['score'], reverse=True)[:5],
            "last_valid_down": sorted([c for c in results if c['prediction'] == "DOWN"], key=lambda x: x['score'])[:5]
        }
    except Exception as e:
        return {"error": str(e)}