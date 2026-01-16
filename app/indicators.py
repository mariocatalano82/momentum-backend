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

def tech_context(change_1h, change_24h, symbol, probability):
    avg = abs(change_24h) / 24
    ratio = abs(change_1h) / (avg + 0.05)
    
    # 1. TECH CARD OUTLOOK (Market context)
    if change_1h > 0:
        if ratio > 2.5:
            outlook = f"{symbol} is experiencing a violent momentum breakout. It has entered the ranking because its current speed is {round(ratio,1)}x higher than its daily average, suggesting a major inflow of capital or news-driven volatility."
        else:
            outlook = f"{symbol} shows a steady upward trend. It secured a spot in the ranking due to its consistent price appreciation over the last hour, maintaining a healthy balance between volume and price growth."
    else:
        if ratio > 2.5:
            outlook = f"{symbol} is under heavy selling pressure. Its rapid decline relative to the 24h trend indicates a sharp momentum shift, likely triggering stop-losses and increasing liquidation risks."
        else:
            outlook = f"{symbol} is slowly losing ground. The downward momentum is controlled but persistent, placing it among the top losers as buyers fail to provide significant support at current levels."

    # 2. CONFIDENCE CARD (Calculation interpretation & Prediction)
    if probability > 90:
        conf_expl = f"The {probability}% score indicates an extreme statistical anomaly. The momentum is so vertical that it is deviating significantly from standard market behavior."
        pred = "Expect high volatility. In the next 2 hours, the asset will likely attempt a final 'blow-off' peak followed by a sharp technical correction (Mean Reversion)."
    elif probability > 75:
        conf_expl = f"A {probability}% score represents a confirmed and strong trend. The mathematical alignment between 1h and 24h movements is highly optimized."
        pred = "The momentum is expected to persist. In the next 2 hours, the asset has a high probability of maintaining its current direction with minor pullbacks."
    else:
        conf_expl = f"The {probability}% score shows moderate conviction. The signal is present but lacks the acceleration needed for a guaranteed breakout."
        pred = "Expect choppy movement. The asset might enter a brief consolidation phase before the next significant move."

    return {
        "outlook": outlook,
        "confidence_explanation": conf_expl,
        "prediction": pred
    }