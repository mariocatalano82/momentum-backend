import math
import random
from app.config import MAX_CONFIDENCE, MIN_CONFIDENCE

def compute_confidence(change_1h, change_24h, profile):
    # Calcolo basato su allineamento dei trend
    alignment = abs(change_1h) / max(abs(change_24h), 0.1)
    stability = 1 - min(abs(change_1h) / 10, 0.6)
    
    base = 55 + alignment * 15 + stability * 10
    
    if profile == "aggressive":
        base += abs(change_1h) * 0.8
    else:
        base -= abs(change_1h) * 0.5
        
    noise = random.uniform(-3, 3)
    confidence = base + noise
    # Limita il risultato tra MIN e MAX definiti in config.py
    return round(max(MIN_CONFIDENCE, min(MAX_CONFIDENCE, confidence)), 1)

def build_chart(change_1h):
    step = change_1h / 12
    return [round(step * i + random.uniform(-0.05, 0.05), 2) for i in range(1, 13)]

def tech_context(change_1h, change_24h):
    # Fornisce il contesto tecnico richiesto da api.py
    bias = "bullish" if change_24h >= 0 else "bearish"
    strength = "strong" if abs(change_24h) > 10 else "moderate"
    return {
        "bias": bias,
        "trend_strength": strength,
        "momentum_state": "accelerating" if abs(change_1h) > abs(change_24h) * 0.3 else "stable",
    }