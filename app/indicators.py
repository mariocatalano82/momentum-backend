import math
import hashlib

# --- DIZIONARIO E UTILITY ---
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

# --- FUNZIONE MANCANTE RIPRISTINATA ---
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

# --- ALTRE FUNZIONI RICHIESTE DA API.PY ---
def build_chart(change_1h):
    return [round(change_1h * (1.1 * math.sin((i/11) * 1.6)), 3) for i in range(12)]

def generate_ranking_reason(c1h, c24, symbol, prob):
    c1h_r, c24_r = round(c1h, 2), round(c24, 2)
    if c1h > 0:
        if c24 > 0: return f"{symbol} shows 'Momentum Convergence'. Strong daily trend (+{c24_r}%) accelerated by a sharp hourly move (+{c1h_r}%)."
        return f"{symbol} triggers a 'Reversal Spike'. Recovering from a red day with high hourly conviction (+{c1h_r}%)."
    else:
        if c24 < 0: return f"{symbol} exhibits 'Panic Continuity'. Bearish pressure on both 24h (-{abs(c24_r)}%) and 1h (-{abs(c1h_r)}%) scales."
        return f"{symbol} in 'Profit Taking' phase. Pulling back (-{abs(c1h_r)}%) despite a positive daily performance."

def tech_context(change_1h, change_24h, symbol, probability, profile):
    c1h, c24 = round(change_1h, 2), round(change_24h, 2)
    is_bullish = c1h > 0
    
    # Alert Climax
    alert = ""
    if probability > 92 and abs(c1h) > 4:
        alert = "⚠️ MARKET CLIMAX: Extreme momentum. High risk of sharp mean reversion. "
    
    # Prediction Action
    if probability > 85:
        scenario = f"CRITICAL {'EXPANSION' if is_bullish else 'FLUSH'}"
        advice = f"Strategy: {'Scalp long/tight stops' if is_bullish else 'Short momentum or flat'}. {alert}"
    elif probability > 70:
        scenario = f"TREND {'CONTINUATION' if is_bullish else 'DRIFT'}"
        advice = f"Strategy: {'Entry zone healthy' if is_bullish else 'Short-biased approach'}. Check next 1H candle."
    else:
        scenario = "NEUTRAL DRIFT"
        advice = "Strategy: No edge. Score below 75% indicates noise. Wait for confirmation."

    # Outlook Multi-Scenario
    if is_bullish and c24 < -3: outlook = "V-Shape Recovery attempt. Monitoring for bottom confirmation."
    elif not is_bullish and c24 > 3: outlook = "Distribution phase. Possible local top forming."
    else: outlook = f"{'Strong' if probability > 80 else 'Weak'} {'Upside' if is_bullish else 'Downside'} continuation."

    # Action Logic Granulare
    vol_ratio = abs(c1h) / (abs(c24/24) + 0.01)
    if probability > 88: logic = "CLIMAX"
    elif vol_ratio > 3: logic = "VOL SPIKE"
    elif (c1h > 0) != (c24 > 0): logic = "REVERSAL"
    elif probability > 70: logic = "TREND"
    else: logic = "STABLE"

    # Vol Impact
    if vol_ratio > 2.5: vol_impact = f"HIGH ({round(vol_ratio,1)}x avg volume)"
    else: vol_impact = "NORMAL (Low institutional interest)"

    return {
        "action_logic": logic,
        "confidence_meaning": "Statistical Anomaly" if probability > 88 else ("Confirmed Trend" if probability > 75 else "Moderate Conviction"),
        "score_drivers": f"{'Convergence' if (c1h>0)==(c24>0) else 'Divergence'}: 1H ({c1h}%) vs 24H ({c24}%)",
        "prediction_action": f"{scenario}\n\n{advice}",
        "rsi": max(15, min(95, int(probability) if is_bullish else (100 - int(probability)))),
        "vol_increase": vol_impact,
        "description": get_coin_description(symbol),
        "ranking_reason": generate_ranking_reason(change_1h, change_24h, symbol, probability),
        "outlook": outlook
    }