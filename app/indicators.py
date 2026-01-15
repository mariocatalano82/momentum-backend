import math
import random
from app.config import MAX_CONFIDENCE, MIN_CONFIDENCE

def compute_confidence(change_1h, change_24h, profile):
    # Calcolo dinamico basato sulla volatilità reale
    alignment = abs(change_1h) / max(abs(change_24h), 0.1)
    stability = 1 - min(abs(change_1h) / 10, 0.6)

    # Base più bassa per permettere variazioni visibili
    base = 50 + (alignment * 10) + (stability * 10)

    if profile == "aggressive":
        base += abs(change_1h) * 0.5
    else:
        base -= abs(change_1h) * 0.3

    # Aggiungiamo un pizzico di casualità per testare il refresh
    noise = random.uniform(-5, 5)
    confidence = base + noise

    return round(max(MIN_CONFIDENCE, min(MAX_CONFIDENCE, confidence)), 1)

def build_chart(change_1h):
    # Genera 12 punti per il grafico
    step = change_1h / 12
    return [round(step * i + random.uniform(-0.1, 0.1), 2) for i in range(1, 13)]