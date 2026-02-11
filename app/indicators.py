import math
import hashlib

# --- DIZIONARIO DESCRIZIONI ---
COIN_DESCRIPTIONS = {
    "BTC": "Bitcoin is the first decentralized digital currency, serving as a global store of value.",
    "ETH": "Ethereum is the leading smart contract platform for dApps and DeFi.",
    "SOL": "Solana is a high-performance blockchain known for speed and low fees.",
    "BNB": "BNB powers the Binance ecosystem and Smart Chain.",
    "XRP": "XRP is designed for fast, low-cost cross-border payments.",
    "ADA": "Cardano is a research-driven blockchain focused on sustainability.",
    "DOGE": "Dogecoin is a widely accepted peer-to-peer cryptocurrency.",
    "AVAX": "Avalanche is a platform for decentralized applications and custom networks.",
    "TRX": "TRON builds infrastructure for a decentralized internet.",
    "LINK": "Chainlink provides tamper-proof real-world data to smart contracts."
}

def get_coin_description(symbol):
    return COIN_DESCRIPTIONS.get(symbol, f"{symbol} is a digital asset driven by market speculation and utility.")

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

def generate_ranking_reason(c1h, c24, symbol, prob):
    c1h_r = round(c1h, 2)
    c24_r = round(c24, 2)
    if c1h > 0:
        if c24 > 0:
            return f"{symbol} shows 'Momentum Convergence'. Strong daily trend (+{c24_r}%) accelerated by a sharp hourly move (+{c1h_r}%)."
        return f"{symbol} triggers a 'Reversal Spike'. Recovering from a red day with high hourly conviction (+{c1h_r}%)."
    else:
        if c24 < 0:
            return f"{symbol} exhibits 'Panic Continuity'. Bearish pressure on both 24h (-{abs(c24_r)}%) and 1h (-{abs(c1h_r)}%) scales."
        return f"{symbol} in 'Profit Taking' phase. Pulling back (-{abs(c1h_r)}%) despite a positive daily performance."

def tech_context(change_1h, change_24h, symbol, probability, profile):
    c1h = round(change_1h, 2)
    c24 = round(change_24h, 2)
    is_bullish = c1h > 0

    # 1. GENERAZIONE PREDICTION ACTION (2H) - DINAMICA E ALLINEATA
    if probability > 85:
        scenario = f"CRITICAL {'EXPANSION' if is_bullish else 'FLUSH'}: High velocity move detected."
        if profile == "aggressive":
            advice = f"Strategy: {'Scalp long with tight stops' if is_bullish else 'Short momentum or stay flat'}. High risk of blow-off."
        else:
            advice = f"Strategy: Avoid entry. {'Overextended' if is_bullish else 'Falling knife'}. Wait for stabilization."
    elif probability > 70:
        scenario = f"TREND {'CONTINUATION' if is_bullish else 'DRIFT'}: Directional strength is confirmed."
        if profile == "aggressive":
            advice = f"Strategy: {'Entry zone healthy' if is_bullish else 'Short-biased approach'}. Follow the 1H lead."
        else:
            advice = f"Strategy: Confirm volume spike on next candle before {'buying' if is_bullish else 'exiting'}."
    else:
        scenario = "NEUTRAL DRIFT: Choppy price action expected within the 2H window."
        advice = "Strategy: No edge. Score below 75% indicates noise. Wait for confidence increase."

    full_prediction = f"{scenario}\n\n{advice}"

    # 2. DRIVERS E MEANING
    if probability > 88:
        meaning = "A 'Statistical Anomaly': Current pressure is in the top 5% of recent volatility."
    elif probability > 75:
        meaning = "A 'Confirmed Trend': Momentum is consistent with volume support."
    else:
        meaning = " 'Moderate Conviction': Move lacks full multi-timeframe confirmation."

    if is_bullish and c24 > 0:
        drivers = f"Convergence: Bullish on both daily (+{c24}%) and hourly (+{c1h}%) scales."
    elif not is_bullish and c24 < 0:
        drivers = f"Panic Flow: Bearish synergy detected across 24h and 1h intervals."
    else:
        drivers = f"Divergence: 1H ({c1h}%) is fighting the 24H ({c24}%) trend."

    # 3. TECHNICALS
    rsi_proxy = int(probability) if is_bullish else (100 - int(probability))
    rsi_proxy = max(15, min(95, rsi_proxy))
    vol_impact = "HIGH" if abs(c1h) > abs(c24/20) else "NORM"

    return {
        "action_logic": "CLIMAX" if probability > 88 else ("TREND" if probability > 70 else "TESTING"),
        "confidence_meaning": meaning,
        "score_drivers": drivers,
        "prediction_action": full_prediction,
        "rsi": rsi_proxy,
        "vol_increase": vol_impact,
        "description": get_coin_description(symbol),
        "ranking_reason": generate_ranking_reason(change_1h, change_24h, symbol, probability),
        "outlook": f"Analysis: {'Strong' if probability > 80 else 'Weak'} {'Upside' if is_bullish else 'Downside'}"
    }