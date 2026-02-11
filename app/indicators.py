import math
import hashlib

# --- UTILITY ---
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

# --- FUNZIONE RIPRISTINATA (Richiesta da api.py) ---
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

# --- FUNZIONE CHART (Richiesta da api.py) ---
def build_chart(change_1h):
    return [round(change_1h * (1.1 * math.sin((i/11) * 1.6)), 3) for i in range(12)]

# --- FUNZIONE REASONING ---
def generate_ranking_reason(c1h, c24, symbol, prob):
    c1h_r, c24_r = round(c1h, 2), round(c24, 2)
    if c1h > 0:
        if c24 > 0: return f"{symbol} shows 'Momentum Convergence'. Strong daily trend (+{c24_r}%) accelerated by a sharp hourly move (+{c1h_r}%)."
        return f"{symbol} triggers a 'Reversal Spike'. Recovering from a red day with high hourly conviction (+{c1h_r}%)."
    else:
        if c24 < 0: return f"{symbol} exhibits 'Panic Continuity'. Bearish pressure on both 24h (-{abs(c24_r)}%) and 1h (-{abs(c1h_r)}%) scales."
        return f"{symbol} in 'Profit Taking' phase. Pulling back (-{abs(c1h_r)}%) despite a positive daily performance."

# --- LOGICA ULTRA-PRECISA (Richiesta da api.py) ---
def tech_context(change_1h, change_24h, symbol, probability, profile):
    c1h, c24 = round(change_1h, 2), round(change_24h, 2)
    is_bullish = c1h > 0
    vol_ratio = abs(c1h) / (abs(c24/24) + 0.01)
    
    if (c1h > 0) != (c24 > 0): phase = "REVERSAL"
    elif abs(c1h) > abs(c24 / 2): phase = "ACCELERATION"
    else: phase = "STABILITY"

    alert = ""
    if probability > 92 and abs(c1h) > 4:
        alert = "⚠️ MARKET CLIMAX: Extreme momentum. High risk of sharp mean reversion. "

    if probability > 90:
        scenario = f"CRITICAL {phase} EXTREME"
        advice = f"High-conviction upside. Momentum ratio at {round(vol_ratio, 1)}x. Target 2H expansion. {alert}" if is_bullish else f"Severe sell pressure. Expect 2H downside continuation. {alert}"
    elif probability > 75:
        scenario = f"STRUCTURAL {phase} CONFIRMED"
        advice = f"Solid bullish structure. Trend convergence supports 2H expansion." if is_bullish else f"Confirmed bearish drift. 2H outlook remains negative."
    else:
        scenario = f"MARGINAL {phase} NOISE"
        advice = "Edge is limited. Probability lacks institutional backing. Neutral 2H stance."

    if probability > 92: logic = "CLIMAX"
    elif vol_ratio > 3.5: logic = "VOL SPIKE"
    elif phase == "REVERSAL" and abs(c1h) > 1.5: logic = "REVERSAL"
    elif probability > 75: logic = "TREND"
    else: logic = "STABLE"

    if vol_ratio > 2.5: vol_impact = f"CRITICAL ({round(vol_ratio,1)}x vs 24H avg)"
    elif vol_ratio > 1.2: vol_impact = f"ACTIVE ({round(vol_ratio,1)}x avg)"
    else: vol_impact = "FLAT (Low participation)"

    if is_bullish and c24 < -4: outlook = "Aggressive bottom recovery. 2H target: Previous resistance retest."
    elif not is_bullish and c24 > 4: outlook = "Distribution at local top. 2H target: Support level consolidation."
    elif is_bullish: outlook = "Trend health: Positive. 2H target: New local high exploration."
    else: outlook = "Trend health: Negative. 2H target: Lower liquidity zone search."

    return {
        "action_logic": logic,
        "confidence_meaning": "STATISTICAL CLIMAX" if probability > 90 else "TREND CONFIRMED",
        "score_drivers": f"V-Ratio: {round(vol_ratio,1)} | 1H: {c1h}% vs 24H: {c24}%",
        "prediction_action": f"{scenario}\n\n{advice}",
        "rsi": max(15, min(95, int(probability) if is_bullish else (100 - int(probability)))),
        "vol_increase": vol_impact,
        "description": get_coin_description(symbol),
        "ranking_reason": generate_ranking_reason(change_1h, change_24h, symbol, probability),
        "outlook": outlook
    }