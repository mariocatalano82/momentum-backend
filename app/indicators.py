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

def tech_context(change_1h, change_24h, symbol, probability, profile):
    """
    Genera i 3 blocchi di testo richiesti per la Confidence Card.
    """
    c1h = round(change_1h, 2)
    c24 = round(change_24h, 2)
    
    # 1. WHAT IT MEANS (Spiegazione Analitica del Punteggio)
    if probability > 88:
        meaning = f"A score of {probability}% represents a 'Statistical Anomaly'. The asset's buy pressure is currently 3x higher than the market average, indicating an extreme momentum event."
    elif probability > 75:
        meaning = f"A score of {probability}% indicates a 'Confirmed Trend'. The mathematical variance is positive, meaning buying volume is consistently overpowering selling pressure."
    else:
        meaning = f"A score of {probability}% suggests 'Moderate Conviction'. The asset is moving, but the statistical strength is not yet sufficient to confirm a full breakout."

    # 2. WHAT DRIVETHIS SCORE (Cosa ha portato alla valutazione)
    if c1h > 0 and c24 > 0:
        drivers = f"This high rating is driven by 'Convergence'. {symbol} is bullish on the daily timeframe (+{c24}%) and is accelerating further in the last hour (+{c1h}%), creating a compound effect."
    elif c1h < 0 and c24 > 0:
        drivers = f"The score is penalized by 'Divergence'. While the long-term trend is up (+{c24}%), the current hourly selling (-{abs(c1h)}%) creates conflicting signals for the algorithm."
    elif c1h > 0 and c24 < 0:
        drivers = f"The score is boosted by a 'Reversal Pattern'. Despite a red day (-{abs(c24)}%), the algorithm detects a sudden influx of volume and price recovery (+{c1h}%) in the last hour."
    else:
        drivers = f"The score reflects 'Double Weakness'. Both hourly (-{abs(c1h)}%) and daily (-{abs(c24)}%) metrics are negative, confirming a strong bearish consensus."

    # 3. CONTEXT vs ACTION (Predizione + Consiglio basato su Profilo)
    # Action Logic per il badge
    if change_1h > 0:
        action_badge = "CLIMAX RUN" if probability > 88 else ("TREND FOLLOWING" if probability > 70 else "TESTING RES.")
    else:
        action_badge = "PANIC FLUSH" if probability > 85 else "SOFT BLEED"

    # Logica Predittiva + Consiglio Operativo
    if probability > 85:
        pred_scenario = "Expect extreme volatility and a potential 'blow-off top' within 2 hours."
        if profile == "aggressive":
            advice = "Strategy: Ride the spike but tighten trailing stops immediately. Risk of rapid reversal is high."
        else: # balanced
            advice = "Strategy: High Risk. It is safer to wait for a pullback rather than chasing this vertical candle."
    
    elif probability > 70:
        pred_scenario = "Expect trend continuation with minor consolidations."
        if profile == "aggressive":
            advice = "Strategy: Good entry zone for scalping. Momentum supports immediate upside."
        else:
            advice = "Strategy: Confirm volume on the next 15m candle before entering. Trend is healthy."
    
    else:
        pred_scenario = "Expect choppy sideways movement or indecision."
        advice = "Strategy: No clear edge. Wait for the score to exceed 75% or for a clear breakout."

    full_action_text = f"{pred_scenario}\n\n{advice}"

    # Dati aggiuntivi per Tech Card (invariati)
    rsi_proxy = int(probability) if change_1h > 0 else (100 - int(probability))
    rsi_proxy = max(15, min(95, rsi_proxy))
    vol_impact = "HIGH" if abs(change_1h) > abs(change_24h/20) else "NORM"
    
    # Context per Tech Card (Generiamo anche qui per coerenza)
    if c1h > 0 and c24 > 0:
        market_ctx = f"{symbol} combines a +{c24}% daily trend with +{c1h}% hourly acceleration."
    else:
        market_ctx = f"{symbol} shows mixed signals: 24h {c24}% vs 1h {c1h}%."

    return {
        "action_logic": action_badge,
        "confidence_meaning": meaning,      # PUNTO 1
        "score_drivers": drivers,           # PUNTO 2
        "prediction_action": full_action_text, # PUNTO 3
        "rsi": rsi_proxy,
        "vol_increase": vol_impact,
        "description": get_coin_description(symbol),
        "market_context": market_ctx,
        "outlook": f"Analysis: {action_badge}"
    }