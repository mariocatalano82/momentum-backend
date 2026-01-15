import math
import random
from app.config import MAX_CONFIDENCE, MIN_CONFIDENCE

def compute_confidence(change_1h, change_24h, profile):
    # 1. Calcolo Allineamento (il trend breve conferma il lungo?)
    same_direction = (change_1h > 0) == (change_24h > 0)
    
    # 2. Forza Relativa (quanto spinge l'ultima ora rispetto alla media giornaliera)
    # Un valore ideale di spinta è circa il 15-20% del movimento giornaliero in un'ora
    hourly_intensity = abs(change_1h) / (abs(change_24h) * 0.2 + 0.1)
    
    if same_direction:
        # Se confermato, base alta che cresce con l'intensità
        base = 65 + (min(hourly_intensity, 1.0) * 15)
    else:
        # Se divergente, la confidenza crolla
        base = 45 - (min(hourly_intensity, 1.0) * 10)

    # 3. Profilo Trader
    if profile == "aggressive":
        base += 4 
    
    # Noise ridotto al minimo per stabilità (solo estetica)
    noise = random.uniform(-0.5, 0.5)
    confidence = base + noise
    
    return round(max(MIN_CONFIDENCE, min(MAX_CONFIDENCE, confidence)), 1)

def build_chart(change_1h):
    # Genera 12 punti che simulano l'andamento dell'ultima ora
    points = []
    current = 0.0
    step = change_1h / 12
    for i in range(12):
        current += step + random.uniform(-0.1, 0.1)
        points.append(round(current, 2))
    return points

def tech_context(change_1h, change_24h):
    # Genera consigli specifici basati sui dati
    intensity = abs(change_1h)
    is_bullish = change_1h > 0
    
    if intensity > 2.5:
        advice = "BREAKOUT: Volatilità estrema. Possibile estensione del trend."
    elif intensity > 1.0:
        advice = "MOMENTUM: Trend confermato. Buona pressione dei volumi."
    else:
        advice = "SIDEWAYS: Bassa volatilità. Attendere segnali di forza."

    return {
        "bias": "BULLISH" if is_bullish else "BEARISH",
        "advice": advice,
        "strength_idx": round(min(intensity * 2, 10), 1),
        "context_summary": f"Il prezzo sta {'salendo' if is_bullish else 'scendendo'} con una variazione dell'1h che rappresenta il {round(abs(change_1h/change_24h)*100 if change_24h !=0 else 0)}% del movimento giornaliero."
    }