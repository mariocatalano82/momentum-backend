import math
import hashlib

def get_deterministic_noise(symbol):
    """Aggiunge micro-variazioni deterministiche per evitare grafici piatti"""
    hash_val = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
    return ((hash_val % 100) / 100 * 0.8) - 0.4

def compute_confidence(change_1h, change_24h, profile, symbol):
    """Calcola la % di Momentum"""
    avg_hourly = abs(change_24h) / 24
    intensity = abs(change_1h) / (avg_hourly + 0.05)
    is_convergent = (change_1h > 0) == (change_24h > 0)
    
    if is_convergent:
        base = 68 + (min(intensity, 5) * 5.5)
    else:
        base = 42 + (min(intensity, 4) * 7)

    if profile == "aggressive": base += 3.5
    final_conf = base + get_deterministic_noise(symbol)
    return round(max(35.0, min(98.5, final_conf)), 1)

def build_chart(change_1h):
    """Simula un grafico sparkline basato sul trend 1h"""
    return [round(change_1h * (1.1 * math.sin((i/11) * 1.6)), 3) for i in range(12)]

def tech_context(change_1h, change_24h, symbol, probability):
    """Genera Action Logic, spiegazioni e predizioni"""
    
    # --- ACTION LOGIC ---
    if change_1h > 0:
        if probability > 88:
            action = "Climax Run"
            expl = f"{symbol} is showing an overextended vertical move. Momentum is peak-level."
        elif probability > 70:
            action = "Trend Following"
            expl = f"Solid upward trajectory for {symbol}. Volume supports the trend."
        else:
            action = "Testing Resistance"
            expl = f"{symbol} is attempting to break higher with moderate conviction."
    else:
        if probability > 85:
            action = "Panic Flush"
            expl = f"Aggressive selling pressure on {symbol}. Watch for liquidations."
        else:
            action = "Soft Bleed"
            expl = f"{symbol} is slowly losing key support levels."

    # --- PREDICTION ---
    if probability > 80:
        pred = "Expect high volatility and testing of new local extremes within 2 hours."
    else:
        pred = "Likely consolidation or sideways choppy movement."

    return {
        "action_logic": action,           # PER IL FRONTEND
        "confidence_explanation": expl,   # PER IL FRONTEND
        "prediction": pred,               # PER IL FRONTEND
        "outlook": f"Market analysis: {action}" 
    }