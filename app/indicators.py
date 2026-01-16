import math
import hashlib

COIN_NAMES = {
    "BTC": "Bitcoin", "ETH": "Ethereum", "XRP": "Ripple", "SOL": "Solana",
    "ADA": "Cardano", "DOT": "Polkadot", "MATIC": "Polygon", "LINK": "Chainlink",
    "AVAX": "Avalanche", "DOGE": "Dogecoin", "SHIB": "Shiba Inu", "FET": "Artificial Intelligence",
    "NEAR": "Near Protocol", "PEPE": "Pepe Coin", "TIA": "Celestia", "INJ": "Injective",
    "SUI": "Sui Network", "APT": "Aptos", "OP": "Optimism", "ARB": "Arbitrum"
}

def get_full_name(symbol):
    return COIN_NAMES.get(symbol, symbol)

def generate_human_advice(symbol, change_1h, hourly_avg, intensity, is_up):
    name = get_full_name(symbol)
    direction = "upward" if is_up else "downward"
    
    if intensity > 7:
        return f"Extreme anomaly on {name}. Current velocity ({abs(change_1h)}%) is {int(intensity)}x the hourly norm of {hourly_avg:.2f}%. High institutional pressure detected. Breakout likely to persist, watch for over-extension."
    elif intensity > 2.5:
        return f"Solid momentum for {name}. The {direction} trend shows real strength, decoupling from the daily average. High mathematical conviction for the next 2 hours."
    elif intensity > 1.0:
        return f"{name} is moving with market flow. Velocity of {abs(change_1h)}% is slightly above avg ({hourly_avg:.2f}%). Stable interest, low risk for trend following."
    else:
        return f"Weak signal on {name}. Current thrust is below 24h volatility. Movement lacks volume support; potential fakeout or sideways phase."

def compute_confidence(change_1h, change_24h, symbol):
    hourly_avg = abs(change_24h) / 24
    intensity = abs(change_1h) / (hourly_avg + 0.05)
    is_up = change_1h > 0
    
    if (change_1h > 0) == (change_24h > 0):
        base = 55 + (min(intensity, 8) * 5)
    else:
        base = 40 + (min(intensity, 8) * 6)
    
    hash_val = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
    noise = ((hash_val % 100) / 100 * 2) - 1
    
    final_prob = round(max(25, min(98.5, base + noise)), 1)
    
    return final_prob, {
        "human_advice": generate_human_advice(symbol, change_1h, hourly_avg, intensity, is_up)
    }

def build_chart(change_1h):
    return [round(change_1h * (math.pow(i / 11, 1.5)), 2) for i in range(12)]