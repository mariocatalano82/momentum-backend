import math
import hashlib

def get_deterministic_noise(symbol):
    """Small variation to avoid identical numbers, based on the asset name."""
    hash_val = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
    return ((hash_val % 100) / 100 * 0.4) - 0.2

def compute_confidence(change_1h, change_24h, profile, symbol):
    """
    Core Logic for 2h Prediction.
    Measures the 'Health' of the movement by comparing 1h speed vs 24h average speed.
    """
    # 1. Calculate the 'Normal' hourly speed of the last 24h
    hourly_avg_24h = abs(change_24h) / 24
    
    # 2. Calculate Intensity Ratio (The 'Engine' of the prediction)
    # How much faster is it moving NOW compared to its 24h average?
    # We add 0.05 to avoid division by zero.
    intensity = abs(change_1h) / (hourly_avg_24h + 0.05)
    
    # 3. Determine Base Score
    # Trend-following (1h and 24h same direction) is more reliable.
    is_trend_following = (change_1h > 0) == (change_24h > 0)
    
    if is_trend_following:
        # If following the main trend, we start from a 'Neutral' 55% 
        # and add weight based on current intensity.
        base = 55.0 + (min(intensity, 8.0) * 5.0)
    else:
        # If it's a reversal (1h against 24h), it's riskier.
        # We start lower (35%) and need more intensity to prove strength.
        base = 35.0 + (min(intensity, 8.0) * 6.5)

    # 4. Profile Adjustments
    if profile == "aggressive":
        base += 3.0
    elif profile == "conservative":
        base -= 5.0

    # 5. Volatility Penalty
    # If intensity is too extreme (e.g. > 10x the average), it's likely a 'pump/dump'
    # which usually retraces within 2h. We lower the confidence.
    if intensity > 10:
        base -= (intensity - 10) * 3

    final_conf = base + get_deterministic_noise(symbol)
    
    # Clamp between 25.0% (No confidence) and 98.5% (Max statistical reliability)
    return round(max(25.0, min(98.5, final_conf)), 1)

def build_chart(change_1h):
    """Generates the momentum curve for the UI Sparkline."""
    points = []
    for i in range(12):
        t = i / 11
        # Exponential curve to show the acceleration path
        val = change_1h * (math.pow(t, 1.5)) 
        points.append(round(val, 2))
    return points

def tech_context(change_1h, change_24h):
    """Generates professional English analysis for the trader."""
    hourly_avg = abs(change_24h / 24)
    ratio = abs(change_1h) / (hourly_avg + 0.05)
    
    # Determination of Strength Score (1-10)
    # Directly linked to our intensity ratio
    s_score = min(9.8, max(1.0, (ratio * 1.5) if ratio > 1 else (ratio * 4)))
    
    if ratio > 3.0:
        advice = "STRONG MOMENTUM: Current velocity is significantly above the daily average. High probability of trend extension."
    elif ratio > 1.2:
        advice = "STABLE GROWTH: Momentum is consistent and supported by recent price action. Reliable for short-term positions."
    elif ratio > 0.7:
        advice = "CONSOLIDATION: Price is moving within its normal range. Low immediate predictive power."
    else:
        advice = "WEAK ACTION: Current speed is below daily average. High risk of sideways movement or fade."

    return {
        "bias": "BULLISH" if change_1h > 0 else "BEARISH",
        "advice": advice,
        "strength_score": round(s_score, 1),
        "summary": f"Speed: {abs(change_1h)}% vs 24h Avg: {round(hourly_avg, 2)}%."
    }