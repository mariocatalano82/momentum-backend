import math
import hashlib

def get_deterministic_noise(symbol, intensity):
    """
    Genera un micro-aggiustamento basato sul nome della moneta.
    Identico per tutti gli utenti, evita salti casuali.
    """
    hash_val = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
    # Restituisce un valore tra -0.3 e 0.3 basato sul simbolo
    return ((hash_val % 100) / 100 * 0.6) - 0.3

def compute_confidence(change_1h, change_24h, profile, symbol):
    # 1. Calcolo Base (Allineamento Trend)
    same_direction = (change_1h > 0) == (change_24h > 0)
    
    # Rapporto di forza tra breve e medio termine
    ratio = abs(change_1h) / (abs(change_24h) / 24 + 0.01)
    
    if same_direction:
        # Se 1h conferma 24h, confidenza alta (65-92)
        base = 65 + (min(ratio, 2.0) * 12)
    else:
        # Se in contrasto (retracement), confidenza media (40-60)
        base = 50 - (min(ratio, 1.5) * 10)

    # 2. Correzione Profilo
    if profile == "aggressive":
        base += 4.0

    # 3. Noise Deterministico (Seed basato sul simbolo)
    # Serve a dare varietà decimale senza essere casuale
    final_conf = base + get_deterministic_noise(symbol, abs(change_1h))
    
    return round(max(35.0, min(96.0, final_conf)), 1)

def build_chart(change_1h):
    """
    Crea 12 punti che simulano la traiettoria dell'ultima ora.
    Usa una funzione logistica per simulare l'accelerazione del momentum.
    """
    points = []
    for i in range(12):
        # Progressone da 0 a 1
        t = i / 11
        # Simuliamo un movimento non lineare (più realistico)
        # La variazione totale deve corrispondere a change_1h
        val = change_1h * (math.pow(t, 1.5)) 
        points.append(round(val, 2))
    return points

def tech_context(change_1h, change_24h):
    intensity = abs(change_1h)
    
    # Logica predittiva per le 2 ore successive
    if intensity > 1.5:
        advice = "STRONG MOMENTUM: High probability of trend continuation in the 2h window."
        score = 8.5
    elif intensity > 0.5:
        advice = "STABLE ACCUMULATION: Steady growth expected for the next 2 hours."
        score = 6.0
    else:
        advice = "LOW VOLATILITY: Sideways movement likely. No clear 2h direction."
        score = 4.0

    return {
        "bias": "BULLISH" if change_1h > 0 else "BEARISH",
        "advice": advice,
        "strength_score": score,
        "summary": f"Momentum is {'positive' if change_1h > 0 else 'negative'} with {intensity}% hourly volatility."
    }