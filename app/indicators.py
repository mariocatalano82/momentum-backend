import math
import hashlib

# --- DIZIONARIO DESCRIZIONI (Invariato) ---
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
    """
    Spiega in linguaggio semplice PERCHÉ la moneta è in classifica.
    """
    c1h = round(c1h, 2)
    c24 = round(c24, 2)
    
    if c1h > 0:
        # SCENARIO POSITIVO
        if c24 > 0:
            return f"{symbol} is in the Top Leaders because it shows 'Momentum Convergence'. It was already strong over 24h (+{c24}%) and has accelerated further in the last hour (+{c1h}%), triggering the algorithm's high-confidence filter."
        else:
            return f"{symbol} enters the ranking due to a 'Reversal Spike'. Despite being down over 24h (-{abs(c24)}%), a sudden wave of buy volume in the last hour (+{c1h}%) suggests a potential bottom or a short-term bounce."
    else:
        # SCENARIO NEGATIVO
        if c24 < 0:
            return f"{symbol} is flagged as a Top Loser because of 'Panic Continuity'. Sellers are dominating both the daily trend (-{abs(c24)}%) and the hourly session (-{abs(c1h)}%), indicating no immediate support."
        else:
            return f"{symbol} appears in the downtrend list due to 'Profit Taking'. While the long-term trend remains positive (+{c24}%), the current hour shows a sharp pullback (-{abs(c1h)}%) as traders lock in gains."

def tech_context(change_1h, change_24h, symbol, probability, profile):
    # Dati tecnici esistenti
    c1h = round(change_1h, 2)
    c24 = round(change_24h, 2)
    
    # --- LOGICA CONFIDENCE CARD (Invariata come piace a te) ---
    if probability > 88:
        meaning = f"A score of {probability}% represents a 'Statistical Anomaly'. Buy pressure is exceptional."
    elif probability > 75:
        meaning = f"A score of {probability}% indicates a 'Confirmed Trend'. Buyers are consistently in control."
    else:
        meaning = f"A score of {probability}% suggests 'Moderate Conviction'. The move is not yet fully confirmed."

    if c1h > 0 and c24 > 0:
        drivers = f"Driven by Convergence: {symbol} is bullish on both daily (+{c24}%) and hourly (+{c1h}%) timeframes."
    elif c1h < 0 and c24 > 0:
        drivers = f"Penalized by Divergence: Daily trend is up (+{c24}%), but hourly profit-taking (-{abs(c1h)}%) lowers the score."
    elif c1h > 0 and c24 < 0:
        drivers = f"Boosted by Reversal: Despite a red day (-{abs(c24)}%), hourly recovery (+{c1h}%) is active."
    else:
        drivers = f"Reflecting Double Weakness: Both hourly (-{abs(c1h)}%) and daily (-{abs(c24)}%) metrics are bearish."

    if change_1h > 0:
        action_badge = "CLIMAX RUN" if probability > 88 else ("TREND FOLLOWING" if probability > 70 else "TESTING RES.")
    else:
        action_badge = "PANIC FLUSH" if probability > 85 else "SOFT BLEED"

    if probability > 85:
        pred_scenario = "Expect extreme volatility and potential reversal within 2 hours."
        advice = "Strategy: Tighten stops immediately. Risk of 'blow-off top' is high." if profile == "aggressive" else "Strategy: High Risk. Wait for a pullback."
    elif probability > 70:
        pred_scenario = "Expect trend continuation."
        advice = "Strategy: Good zone for entry. Momentum is healthy." if profile == "aggressive" else "Strategy: Confirm volume on next candle before entering."
    else:
        pred_scenario = "Expect choppy sideways movement."
        advice = "Strategy: No clear edge. Wait for score > 75%."

    full_action_text = f"{pred_scenario}\n\n{advice}"
    
    # --- DATI PER TECH CARD (Integrati con Ranking Reason) ---
    rsi_proxy = int(probability) if change_1h > 0 else (100 - int(probability))
    rsi_proxy = max(15, min(95, rsi_proxy))
    vol_impact = "HIGH" if abs(change_1h) > abs(change_24h/20) else "NORM"
    
    description = get_coin_description(symbol)
    ranking_reason = generate_ranking_reason(c1h, c24, symbol, probability) # NUOVA FUNZIONE

    return {
        "action_logic": action_badge,
        "confidence_meaning": meaning,
        "score_drivers": drivers,
        "prediction_action": full_action_text,
        "rsi": rsi_proxy,
        "vol_increase": vol_impact,
        "description": description,       # Existing
        "ranking_reason": ranking_reason, # NEW: The "Why in Ranking" text
        "outlook": f"Analysis: {action_badge}"
    }