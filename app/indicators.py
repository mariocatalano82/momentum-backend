import math
import random
from app.config import MAX_CONFIDENCE, MIN_CONFIDENCE

def compute_confidence(change_1h, change_24h, profile):
    """
    Calculates a realistic confidence score based on trend alignment 
    and relative strength between 1h and 24h performance.
    """
    # 1. Trend Alignment Check
    # Does the short-term trend (1h) confirm the long-term trend (24h)?
    same_direction = (change_1h > 0) == (change_24h > 0)
    
    # 2. Relative Intensity
    # We calculate how much the 1h move represents compared to a 20% 
    # expected hourly portion of the 24h move.
    intensity = abs(change_1h) / (abs(change_24h) * 0.2 + 0.1)
    
    if same_direction:
        # High confidence if trends are aligned (68% to 92%)
        base = 68 + (min(intensity, 1.2) * 20)
    else:
        # Lower confidence if price is retracing (40% to 55%)
        base = 55 - (min(intensity, 1.0) * 15)

    # 3. Trader Profile Adjustment
    if profile == "aggressive":
        base += 3.5
    
    # Minimal fluctuation for UI "liveliness"
    noise = random.uniform(-0.5, 0.5)
    confidence = base + noise
    
    # Hard cap at 95% to keep it realistic
    return round(max(MIN_CONFIDENCE, min(95.0, confidence)), 1)

def build_chart(change_1h):
    """
    Generates 12 data points for the Sparkline visualization.
    Simulates the volatility of the last hour.
    """
    points = []
    current = 0.0
    # Create a realistic path based on the 1h change
    step = change_1h / 12
    for i in range(12):
        current += step + random.uniform(-0.12, 0.12)
        points.append(round(current, 2))
    return points

def tech_context(change_1h, change_24h):
    """
    Generates dynamic technical advice and scores based on real performance.
    """
    intensity = abs(change_1h)
    is_up = change_1h > 0
    
    # Dynamic Advice Logic
    if intensity > 2.0:
        advice = "VOLATILITY SPIKE: Strong impulsive move detected. High probability of trend extension."
    elif intensity > 0.8:
        advice = "STEADY TREND: Consistent momentum. Market is showing solid accumulation/distribution."
    else:
        advice = "CONSOLIDATION: Low momentum. Sideways action, wait for a volume breakout."

    # Strength Score (0 to 10)
    # Based on how aggressive the 1h move is
    strength_score = round(min(intensity * 2.8, 10), 1)
    
    summary = (
        f"1h analysis shows a {'positive' if is_up else 'negative'} momentum "
        f"with a relative strength of {round(intensity, 1)}."
    )

    return {
        "bias": "BULLISH" if is_up else "BEARISH",
        "advice": advice,
        "strength_score": strength_score,
        "summary": summary
    }