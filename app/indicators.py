import math
import hashlib

# Mapping tickers to Full Names
COIN_NAMES = {
    "BTC": "Bitcoin", "ETH": "Ethereum", "XRP": "Ripple",
    "SOL": "Solana", "ADA": "Cardano", "DOT": "Polkadot",
    "MATIC": "Polygon", "LINK": "Chainlink", "AVAX": "Avalanche",
    "DOGE": "Dogecoin", "SHIB": "Shiba Inu", "FET": "Artificial Intelligence",
    "GLMR": "Moonbeam", "RNDR": "Render", "NEAR": "Near Protocol",
    "PEPE": "Pepe", "TIA": "Celestia", "INJ": "Injective",
    "SUI": "Sui", "APT": "Aptos", "OP": "Optimism", "ARB": "Arbitrum"
}

def get_deterministic_noise(symbol):
    hash_val = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
    return ((hash_val % 100) / 100 * 0.4) - 0.2

def compute_confidence(change_1h, change_24h, profile, symbol):
    hourly_avg_24h = abs(change_24h) / 24
    intensity = abs(change_1h) / (hourly_avg_24h + 0.05)
    
    is_trend_following = (change_1h > 0) == (change_24h > 0)
    
    if is_trend_following:
        base = 55.0 + (min(intensity, 8.0) * 5.0)
    else:
        base = 40.0 + (min(intensity, 8.0) * 6.5)

    if profile == "aggressive": base += 3.0
    if intensity > 10: base -= (intensity - 10) * 3 # Over-extension penalty

    final_conf = base + get_deterministic_noise(symbol)
    return round(max(25.0, min(98.5, final_conf)), 1)

def build_chart(change_1h):
    points = []
    for i in range(12):
        t = i / 11
        val = change_1h * (math.pow(t, 1.5)) 
        points.append(round(val, 2))
    return points

def tech_context(change_1h, change_24h):
    hourly_avg = abs(change_24h / 24)
    ratio = abs(change_1h) / (hourly_avg + 0.05)
    s_score = min(9.8, max(1.0, (ratio * 1.5) if ratio > 1 else (ratio * 4)))
    
    if ratio > 3.0:
        advice = "STRONG MOMENTUM: Velocity is significantly above average. High probability of extension."
    elif ratio > 1.2:
        advice = "STABLE GROWTH: Momentum is consistent. Reliable for short-term positions."
    elif ratio > 0.7:
        advice = "CONSOLIDATION: Price within normal range. Low immediate predictive power."
    else:
        advice = "WEAK ACTION: Speed is below average. Risk of sideways movement or fade."

    return {
        "bias": "BULLISH" if change_1h > 0 else "BEARISH",
        "advice": advice,
        "strength_score": round(s_score, 1),
        "summary": f"Speed: {abs(change_1h)}% vs 24h Avg: {round(hourly_avg, 2)}%"
    }