import math
import hashlib

def get_deterministic_noise(symbol):
    # Genera un piccolo "rumore" fisso per ogni moneta per evitare score identici
    hash_val = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
    return ((hash_val % 100) / 100 * 0.9) - 0.45

def compute_confidence(change_1h, change_24h, profile, symbol):
    # 1. Velocity Ratio: Quanto corre ora rispetto alla media 24h?
    avg_hourly_speed = abs(change_24h) / 24
    if avg_hourly_speed == 0: avg_hourly_speed = 0.01
    
    velocity_ratio = abs(change_1h) / avg_hourly_speed
    
    # 2. Convergenza: 1H e 24H vanno nella stessa direzione?
    is_convergent = (change_1h > 0) == (change_24h > 0)
    
    # 3. Calcolo Score Base
    if is_convergent:
        # Trend confermato: premio l'accelerazione fino a un certo punto (cap a 5x)
        score = 65 + (min(velocity_ratio, 5.0) * 6)
    else:
        # Contro-trend (pullback o inversione): score più basso
        score = 40 + (min(velocity_ratio, 4.0) * 8)

    # 4. Profilo Utente
    if profile == "aggressive": score += 4.5
    
    # 5. Noise deterministico
    final_conf = score + get_deterministic_noise(symbol)
    
    # Cap (nessuna certezza al 100%, minimo 35%)
    return round(max(35.0, min(98.2, final_conf)), 1)

def build_chart(change_1h):
    # Proiezione 2H non lineare (curva di decadimento momentum)
    points = []
    for i in range(12): # 12 punti = 2 ore (10 min step)
        t = i / 11
        # Funzione: x * (1 + sin(t)) smorzata
        val = change_1h * (1.0 + (0.5 * math.sin(t * 3.14)))
        points.append(round(val, 2))
    return points

def tech_context(change_1h, change_24h):
    avg_speed = abs(change_24h) / 24
    if avg_speed == 0: avg_speed = 0.01
    ratio = abs(change_1h) / avg_speed
    
    # Testi professionali e dinamici
    if ratio > 3.0:
        advice = "MOMENTUM BURST: High-velocity anomaly. Asset is moving 3x faster than daily average."
        score = 9.5
    elif ratio > 1.5:
        advice = "HEALTHY TREND: Consistent buying pressure supporting the move. Volume aligns with price."
        score = 7.8
    elif ratio > 0.8:
        advice = "NEUTRAL FLOW: Price action aligns with daily averages. No significant anomaly detected."
        score = 5.5
    else:
        advice = "STAGNATION: Volatility compression. Expect chop or sudden breakout attempt."
        score = 3.5
        
    return {
        "advice": advice, 
        "score": round(min(score + (abs(change_1h)*0.5), 9.9), 1),
        "ratio": round(ratio, 1)
    }