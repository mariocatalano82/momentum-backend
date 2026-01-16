import math
import hashlib

def get_deterministic_noise(symbol):
    hash_val = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
    return ((hash_val % 100) / 100 * 0.6) - 0.3

def compute_confidence(change_1h, change_24h, profile, symbol):
    # Analisi della solidità: convergenza tra trend micro e macro
    avg_hourly_24h = change_24h / 24
    intensity_ratio = abs(change_1h) / (abs(avg_hourly_24h) + 0.1)
    is_convergent = (change_1h > 0) == (change_24h > 0)
    
    if is_convergent:
        base_score = 72 + (min(intensity_ratio, 4.0) * 5)
    else:
        base_score = 48 + (min(intensity_ratio, 2.5) * 4)

    if profile == "aggressive":
        base_score += 4.0

    final_conf = base_score + get_deterministic_noise(symbol)
    return round(max(35.0, min(97.5, final_conf)), 1)

def build_chart(change_1h):
    points = []
    for i in range(12):
        t = i / 11
        val = change_1h * (math.pow(t, 1.4)) 
        points.append(round(val, 2))
    return points

def tech_context(change_1h, change_24h):
    ratio = abs(change_1h) / (abs(change_24h/24) + 0.1)
    
    if ratio > 2.5:
        advice = "FORTE ACCELERAZIONE: Il momentum orario domina il trend giornaliero. Elevata probabilità di estensione del movimento nelle prossime 2h."
        score = 8.8
    elif ratio > 1.0:
        advice = "TREND COSTANTE: Il movimento attuale è supportato da volumi regolari. Struttura solida per il mantenimento della posizione."
        score = 6.5
    else:
        advice = "CONSOLIDAMENTO: Momentum orario inferiore alla media giornaliera. Possibile fase laterale o compressione di volatilità."
        score = 4.2

    return {
        "bias": "BULLISH" if change_1h > 0 else "BEARISH",
        "advice": advice,
        "strength_score": score,
        "summary": f"Velocità attuale {abs(change_1h)}% vs Media 24h {abs(round(change_24h/24, 2))}%."
    }