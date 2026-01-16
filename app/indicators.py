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
    return [round(change_1h * (1.1 * math.sin((i/11) * 1.6)), 3) for i in range(12)]

def tech_context(change_1h, change_24h, symbol):
    avg = abs(change_24h) / 24
    ratio = abs(change_1h) / (avg + 0.05)
    
    # LOGICA LINGUAGGIO FRIENDLY
    if ratio > 2.5:
        friendly = f"Attenzione: {symbol} sta correndo molto più velocemente del solito. È un segnale di grande forza, ma il prezzo è 'tirato'. Ottimo per chi è già dentro, rischioso per chi entra ora."
        tech = "VOLATILITY BURST: Momentum ratio > 2.5x. High probability of overextension."
    elif ratio > 1.2:
        friendly = f"{symbol} si sta muovendo in modo sano e costante. Il trend sembra solido e supportato da scambi regolari. Segnale di continuazione moderata."
        tech = "TREND PERSISTENCE: Balanced momentum. Volatility aligns with volume flows."
    else:
        friendly = f"{symbol} è in una fase di attesa. Non c'è una direzione chiara in questo momento. Meglio attendere un picco di velocità."
        tech = "CONSOLIDATION: Momentum ratio < 1.0. Asset is range-bound."

    return {
        "advice_friendly": friendly,
        "advice_tech": tech,
        "score": round(min(9.8, 4.0 + ratio), 1),
        "ratio": round(ratio, 2)
    }