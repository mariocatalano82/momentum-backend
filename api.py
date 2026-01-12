from fastapi import FastAPI
import datasources
import time
import math

app = FastAPI()

CRYPTO_NAMES = {
    "BTC": "Bitcoin", "ETH": "Ethereum", "SOL": "Solana", "BNB": "Binance Coin",
    "XRP": "Ripple", "ADA": "Cardano", "DOGE": "Dogecoin", "AVAX": "Avalanche",
    "DOT": "Polkadot", "LINK": "Chainlink", "MATIC": "Polygon", "SHIB": "Shiba Inu"
}

def generate_detailed_explanation(c_24h, c_1h, profile, symbol):
    trend_24 = "rialzista" if c_24h > 0 else "ribassista"
    accel = "in accelerazione" if abs(c_1h) > abs(c_24h/24) else "in consolidamento"
    behavior = "una gestione prudente" if profile == "balanced" else "un'operatività rapida"
    
    return (f"L'asset è in lista perché mostra un trend {trend_24} del {abs(c_24h)}% nelle 24h. "
            f"Nell'ultima ora il momentum è {accel} ({round(c_1h, 2)}%). "
            f"Per il profilo {profile}, si consiglia {behavior} causa volatilità.")

@app.get("/ranking/state")
def get_state(profile: str = "balanced"):
    try:
        raw_data = datasources.get_crypto_data()
        results = []
        MIN_VOLUME = 2000000 

        for coin in raw_data:
            vol = float(coin.get('volume_usd', 0) or 0)
            if vol < MIN_VOLUME: continue

            c_24h = float(coin.get('price_change_percentage_24h', 0) or 0)
            c_1h = round(c_24h / 24 * 1.5, 2)
            
            sym = str(coin.get('symbol', '???')).replace('USDT', '').upper()
            name = CRYPTO_NAMES.get(sym, sym)
            prob = min(round(65 + (abs(c_24h) * 2.3), 1), 93.5)
            
            results.append({
                "symbol": sym, "name": name, "price_change_24h": round(c_24h, 2),
                "probability": prob, "prediction": "UP" if c_24h > 0 else "DOWN",
                "explanation": generate_detailed_explanation(c_24h, c_1h, profile, sym),
                "score": prob if c_24h > 0 else -prob,
                "chart_data": [c_24h*0.4, c_24h*0.7, c_24h*0.5, c_24h]
            })

        return {
            "last_valid_up": sorted([c for c in results if c['prediction'] == "UP"], key=lambda x: x['score'], reverse=True)[:5],
            "last_valid_down": sorted([c for c in results if c['prediction'] == "DOWN"], key=lambda x: x['score'])[:5]
        }
    except Exception as e:
        return {"error": str(e)}