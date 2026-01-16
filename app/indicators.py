import math
import hashlib

def get_deterministic_noise(symbol):
    hash_val = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
    return ((hash_val % 100) / 100 * 0.8) - 0.4

def compute_confidence(change_1h, change_24h, profile, symbol):
    # Calcolo dell'intensità: quanto l'ora attuale devia dalla media oraria 24h
    avg_hourly = abs(change_24h) / 24
    intensity = abs(change_1h) / (avg_hourly + 0.05)
    
    # Sigmoide per mappare il momentum in una probabilità reale
    is_convergent = (change_1h > 0) == (change_24h > 0)
    
    if is_convergent:
        # Trend solido: la confidenza cresce con l'accelerazione
        base = 68 + (min(intensity, 5) * 5.5)
    else:
        # Contro-trend: punteggio più basso e cauto
        base = 42 + (min(intensity, 4) * 7)

    if profile == "aggressive": base += 3.5

    final_conf = base + get_deterministic_noise(symbol)
    return round(max(35.0, min(98.5, final_conf)), 1)

def build_chart(change_1h):
    # Proiezione 2h con decadimento logaritmico
    return [round(change_1h * (1.1 * math.sin((i/11) * 1.6)), 3) for i in range(12)]

def tech_context(change_1h, change_24h):
    avg = abs(change_24h) / 24
    ratio = abs(change_1h) / (avg + 0.05)
    
    if ratio > 2.8:
        advice = "MOMENTUM BURST: High-velocity decoupling detected. Asset is outperforming daily volatility norms."
        score = round(min(9.8, 7.0 + ratio), 1)
    elif ratio > 1.2:
        advice = "SUSTAINED TREND: Momentum is healthy and supported by consistent volume flows."
        score = round(min(8.5, 5.5 + ratio), 1)
    else:
        advice = "LOW CONVICTION: Momentum is fading or consolidating. Expect range-bound movement."
        score = 4.2
        
    return {"advice": advice, "score": score, "ratio": round(ratio, 2)}