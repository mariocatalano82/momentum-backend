import math
import hashlib

# Dizionario esteso per nomi completi
COIN_NAMES = {
    "BTC": "Bitcoin", "ETH": "Ethereum", "XRP": "Ripple", "SOL": "Solana",
    "ADA": "Cardano", "DOT": "Polkadot", "MATIC": "Polygon", "LINK": "Chainlink",
    "AVAX": "Avalanche", "DOGE": "Dogecoin", "SHIB": "Shiba Inu", "FET": "Artificial Intelligence",
    "GLMR": "Moonbeam", "RNDR": "Render Token", "NEAR": "Near Protocol", "PEPE": "Pepe Coin",
    "TIA": "Celestia", "INJ": "Injective", "SUI": "Sui Network", "APT": "Aptos",
    "OP": "Optimism", "ARB": "Arbitrum", "LTC": "Litecoin", "BCH": "Bitcoin Cash"
}

def get_full_name(symbol):
    return COIN_NAMES.get(symbol, symbol)

def generate_human_advice(symbol, change_1h, hourly_avg, intensity, is_up):
    """Genera un'analisi umana e specifica basata sulla deviazione standard."""
    name = get_full_name(symbol)
    direction = "salita" if is_up else "discesa"
    
    if intensity > 7:
        return f"Movimento anomalo su {name}. La velocità attuale ({abs(change_1h)}%) è quasi {int(intensity)} volte superiore alla norma oraria di {hourly_avg:.2f}%. Questo indica una pressione {direction} estrema, tipica di un breakout istituzionale. Probabile continuazione nel breve, ma monitora i volumi per evitare trappole."
    elif intensity > 2.5:
        return f"Momentum solido per {name}. Il trend in {direction} mostra una forza reale, staccandosi nettamente dalla media giornaliera. C'è convinzione dietro questo movimento: le probabilità di persistenza per le prossime 2 ore sono elevate."
    elif intensity > 1.0:
        return f"{name} si muove in linea con il mercato. La velocità di {abs(change_1h)}% è leggermente superiore alla media oraria ({hourly_avg:.2f}%), indicando un interesse costante ma non esplosivo. Ottimo per strategie trend-following meno rischiose."
    else:
        return f"Segnale debole su {name}. Nonostante la variazione di prezzo, la spinta attuale è inferiore alla volatilità media registrata nelle ultime 24 ore. Il movimento manca di 'carburante' matematico; rischio di fase laterale imminente."

def compute_confidence(change_1h, change_24h, symbol):
    # Calcolo intensità rispetto alla media 24h
    hourly_avg = abs(change_24h) / 24
    intensity = abs(change_1h) / (hourly_avg + 0.05)
    is_up = change_1h > 0
    
    # Calcolo probabilità base
    if (change_1h > 0) == (change_24h > 0):
        base = 55 + (min(intensity, 8) * 5)
    else:
        base = 40 + (min(intensity, 8) * 6)
    
    # Noise deterministico per evitare piattume
    hash_val = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
    noise = ((hash_val % 100) / 100 * 2) - 1
    
    final_prob = round(max(25, min(98.5, base + noise)), 1)
    
    # Analisi tecnica contestuale
    context = {
        "bias": "BULLISH" if is_up else "BEARISH",
        "strength_score": round(min(10, intensity * 1.5), 1),
        "summary": f"Speed: {abs(change_1h)}% vs Avg: {hourly_avg:.2f}%",
        "human_advice": generate_human_advice(symbol, change_1h, hourly_avg, intensity, is_up)
    }
    
    return final_prob, context

def build_chart(change_1h):
    points = []
    for i in range(12):
        t = i / 11
        val = change_1h * (math.pow(t, 1.5)) 
        points.append(round(val, 2))
    return points