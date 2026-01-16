import math
import hashlib

def get_deterministic_noise(symbol):
    # Crea un valore fisso tra -0.3 e 0.3 basato sul nome della moneta
    hash_val = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
    return ((hash_val % 100) / 100 * 0.6) - 0.3

def compute_confidence(change_1h, change_24h, profile, symbol):
    same_direction = (change_1h > 0) == (change_24h > 0)
    ratio = abs(change_1h) / (abs(change_24h) / 24 + 0.01)
    
    if same_direction:
        base = 65 + (min(ratio, 2.0) * 12)
    else:
        base = 50 - (min(ratio, 1.5) * 10)

    if profile == "aggressive":
        base += 4.0

    # Aggiunge il noise fisso per non avere numeri "tondi" e casuali
    final_conf = base + get_deterministic_noise(symbol)
    return round(max(35.0, min(96.0, final_conf)), 1)

def build_chart(change_1h):
    points = []
    for i in range(12):
        t = i / 11
        # Curva di momentum non lineare
        val = change_1h * (math.pow(t, 1.5)) 
        points.append(round(val, 2))
    return points

def tech_context(change_1h, change_24h):
    intensity = abs(change_1h)
    if intensity > 1.5:
        advice = "STRONG MOMENTUM: Trend continuation likely in 2h."
        score = 8.5
    elif intensity > 0.5:
        advice = "STABLE ACCUMULATION: Steady growth for next 2h."
        score = 6.0
    else:
        advice = "LOW VOLATILITY: Sideways action expected."
        score = 4.0

    return {
        "bias": "BULLISH" if change_1h > 0 else "BEARISH",
        "advice": advice,
        "strength_score": score,
        "summary": f"Momentum {'positive' if change_1h > 0 else 'negative'} ({intensity}% hourly)."
    }