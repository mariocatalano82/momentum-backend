import math
import hashlib

def get_deterministic_noise(symbol):
    hash_val = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
    return ((hash_val % 100) / 100 * 0.8) - 0.4

def compute_confidence(change_1h, change_24h, profile, symbol):
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
    # Simula grafico sparkline 
    return [round(change_1h * (1.1 * math.sin((i/11) * 1.6)), 3) for i in range(12)]

def tech_context(change_1h, change_24h, symbol, probability):
    # --- CALCOLO METRICHE PER UI (RSI Proxy + Vol Impact) ---
    # Dato che usiamo snapshot, stimiamo RSI basandoci su probability e trend
    rsi_proxy = int(probability) if change_1h > 0 else (100 - int(probability))
    # Limiamo gli estremi per realismo
    rsi_proxy = max(15, min(95, rsi_proxy))
    
    # Vol Impact basato sull'accelerazione
    vol_impact = "HIGH" if abs(change_1h) > abs(change_24h/20) else "NORM"

    # --- ACTION LOGIC ---
    if change_1h > 0:
        if probability > 88:
            action = "Climax Run"
            expl = f"{symbol} vertical surge. Peak momentum, risk of pullback."
        elif probability > 70:
            action = "Trend Following"
            expl = f"Solid upward trajectory for {symbol} supported by volume."
        else:
            action = "Testing Res."
            expl = f"{symbol} attempts to break higher with moderate conviction."
    else:
        if probability > 85:
            action = "Panic Flush"
            expl = f"Aggressive selling on {symbol}. Watch for liquidations."
        else:
            action = "Soft Bleed"
            expl = f"{symbol} is slowly losing key support levels."

    if probability > 80:
        pred = "Expect high volatility and new extremes within 2 hours."
    else:
        pred = "Likely consolidation or sideways movement."

    return {
        "action_logic": action,
        "confidence_explanation": expl,
        "prediction": pred,
        "outlook": f"Market Analysis: {action}",
        "rsi": rsi_proxy,       # AGGIUNTO PER TECH CARD
        "vol_increase": vol_impact # AGGIUNTO PER TECH CARD
    }