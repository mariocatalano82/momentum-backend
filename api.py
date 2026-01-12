from fastapi import FastAPI
import datasources
import time
import math

app = FastAPI()

# Mappa espansa per i nomi reali (Se non presente, il codice proverà a pulire il simbolo)
CRYPTO_NAMES = {
    "BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana", "BNB": "Binance Coin",
    "XRP": "Ripple", "ADA": "Cardano", "DOGE": "Dogecoin", "AVAX": "Avalanche",
    "DOT": "Polkadot", "LINK": "Chainlink", "MATIC": "Polygon", "SHIB": "Shiba Inu",
    "LTC": "Litecoin", "NEAR": "Near Protocol", "TRX": "Tron", "UNI": "Uniswap"
}

def calculate_realistic_probability(c_24h, vol, profile):
    # Logica di "smorzamento": più la percentuale è alta, più è difficile salire
    # Una variazione del 10% non darà più il 90%, ma circa il 78-82%
    abs_c = abs(c_24h)
    
    # Base di calcolo logaritmica
    base_prob = 50 + (15 * math.log1p(abs_c)) 
    
    # Bonus Volume: solo se supera i 10M USD dà un contributo reale
    vol_bonus = min(math.log10(vol / 1000000) * 2, 5) if vol > 1000000 else -5
    
    final_prob = base_prob + vol_bonus
    
    # Offset profilo
    if profile == "balanced":
        final_prob *= 0.92 # Più conservativo
    
    # Cap massimo realistico: è quasi impossibile essere sicuri al 100%
    return round(min(final_prob, 89.5), 1)

def generate_detailed_explanation(c_24h, c_1h, profile, symbol):
    trend_type = "rialzista" if c_24h > 0 else "ribassista"
    accel = "stabile" if abs(c_1h) < abs(c_24h/24) else "in forte spinta"
    
    return (f"Analisi {symbol}: Il momentum {trend_type} di 24h è attualmente {accel}. "
            f"Il calcolo ponderato per il profilo {profile} indica una pressione "
            f"{'dominante' if abs(c_24h) > 5 else 'moderata'}. Si raccomanda prudenza.")

@app.get("/ranking/state")
def get_state(profile: str = "balanced"):
    try:
        raw_data = datasources.get_crypto_data()
        results = []
        MIN_VOLUME = 3000000 # Alzato a 3M per escludere "rumore"

        for coin in raw_data:
            vol = float(coin.get('volume_usd', 0) or 0)
            if vol < MIN_VOLUME: continue

            c_24h = float(coin.get('price_change_percentage_24h', 0) or 0)
            c_1h = round(c_24h / 24 * 1.2, 2)
            
            # Pulizia Simbolo e Nome
            sym = str(coin.get('symbol', '???')).replace('USDT', '').upper()
            full_name = CRYPTO_NAMES.get(sym, sym.capitalize()) # Se non c'è, Capitalizza (es. Peper)
            
            prob = calculate_realistic_probability(c_24h, vol, profile)
            
            results.append({
                "symbol": sym,
                "name": full_name,
                "price_change_24h": round(c_24h, 2),
                "probability": prob,
                "prediction": "UP" if c_24h > 0 else "DOWN",
                "explanation": generate_detailed_explanation(c_24h, c_1h, profile, sym),
                "score": prob if c_24h > 0 else -prob,
                "chart_data": [c_24h*0.3, c_24h*0.6, c_24h*0.4, c_24h*0.9, c_24h]
            })

        return {
            "last_valid_up": sorted([c for c in results if c['prediction'] == "UP"], key=lambda x: x['score'], reverse=True)[:5],
            "last_valid_down": sorted([c for c in results if c['prediction'] == "DOWN"], key=lambda x: x['score'])[:5],
            "last_update": time.time()
        }
    except Exception as e:
        return {"error": str(e)}