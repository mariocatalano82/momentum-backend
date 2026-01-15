import math
import random
from app.config import MAX_CONFIDENCE, MIN_CONFIDENCE

def compute_confidence(change_1h, change_24h, profile):
    # Calcolo allineamento dei trend
    same_direction = (change_1h > 0) == (change_24h > 0)
    
    # Rapporto di intensità: quanto l'ultima ora spinge rispetto al giorno
    # Se l'ora fa il 20% del movimento giornaliero, il momentum è fortissimo
    intensity = abs(change_1h) / (abs(change_24h) * 0.2 + 0.1)
    
    if same_direction:
        # Trend confermato: confidenza alta tra 68% e 88%
        base = 68 + (min(intensity, 1.0) * 20)
    else:
        # Divergenza: il prezzo sta ritracciando. Confidenza bassa tra 40% e 55%
        base = 55 - (min(intensity, 1.0) * 15)

    if profile == "aggressive":
        base += 3
    
    # Stabilità del valore (noise ridotto allo 0.5%)
    confidence = base + random.uniform(-0.5, 0.5)
    return round(max(MIN_CONFIDENCE, min(95.0, confidence)), 1)

def build_chart(change_1h):
    # Genera 12 punti per lo Sparkline
    points = []
    curr = 0.0
    step = change_1h / 12
    for i in range(12):
        curr += step + random.uniform(-0.1, 0.1)
        points.append(round(curr, 2))
    return points

def tech_context(change_1h, change_24h):
    intensity = abs(change_1h)
    is_up = change_1h > 0
    
    if intensity > 2.0:
        advice = "VOLATILITY SPIKE: Movimento impulsivo. Possibile continuazione rapida."
    elif intensity > 0.8:
        advice = "STEADY TREND: Momentum costante. Accumulazione in corso."
    else:
        advice = "LOW MOMENTUM: Fase laterale. Attendere aumento dei volumi."

    return {
        "bias": "BULLISH" if is_up else "BEARISH",
        "advice": advice,
        "strength_score": round(min(intensity * 2.5, 10), 1),
        "summary": f"Analisi 1h indica un momentum {'positivo' if is_up else 'negativo'} con forza {round(intensity, 1)}."
    }