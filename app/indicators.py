import math
import hashlib

# ... (COIN_DESCRIPTIONS e utility invariate fino a tech_context) ...

def tech_context(change_1h, change_24h, symbol, probability, profile):
    c1h, c24 = round(change_1h, 2), round(change_24h, 2)
    is_bullish = c1h > 0
    vol_ratio = abs(c1h) / (abs(c24/24) + 0.01)
    
    # 1. DETERMINAZIONE FASE DINAMICA
    if (c1h > 0) != (c24 > 0):
        phase = "REVERSAL"
    elif abs(c1h) > abs(c24 / 2):
        phase = "ACCELERATION"
    else:
        phase = "STABILITY"

    # 2. COSTRUZIONE PREDICTION ACTION (SOLIDA E PRECISA)
    # Analizziamo la forza del segnale basandoci sulla probabilità calcolata
    if probability > 90:
        scenario = f"CRITICAL {phase} EXTREME"
        if is_bullish:
            advice = f"High-conviction upside. Momentum ratio at {round(vol_ratio, 1)}x. Target 2H expansion. Risk: Climax exhaustion."
        else:
            advice = f"Severe sell pressure. Volatility spike detected. Expect 2H downside continuation. Avoid catching the knife."
    
    elif probability > 75:
        scenario = f"STRUCTURAL {phase} CONFIRMED"
        if is_bullish:
            advice = f"Solid bullish structure. Trend convergence supports upside for the next 2H window. Maintain long bias."
        else:
            advice = f"Confirmed bearish drift. Resistance levels holding. 2H outlook remains negative under current volume."
            
    else:
        scenario = f"MARGINAL {phase} NOISE"
        advice = f"Edge is limited. Probability ({probability}%) lacks institutional backing. Neutral 2H stance recommended."

    # 3. ACTION LOGIC GRANULARE (MAPPA DIRETTAMENTE AI COLORI APP)
    if probability > 92: logic = "CLIMAX"
    elif vol_ratio > 3.5: logic = "VOL SPIKE"
    elif phase == "REVERSAL" and abs(c1h) > 1.5: logic = "REVERSAL"
    elif probability > 75: logic = "TREND"
    else: logic = "STABLE"

    # 4. VOL IMPACT DESCRITTIVO
    if vol_ratio > 2.5:
        vol_impact = f"CRITICAL ({round(vol_ratio,1)}x relative to 24H)"
    elif vol_ratio > 1.2:
        vol_impact = f"ACTIVE ({round(vol_ratio,1)}x average)"
    else:
        vol_impact = "FLAT (Low participation)"

    # 5. OUTLOOK MULTI-SCENARIO (LOGICA INCROCIATA 1H/24H)
    if is_bullish and c24 < -4:
        outlook = "Aggressive bottom recovery. 2H target: Previous resistance retest."
    elif not is_bullish and c24 > 4:
        outlook = "Distribution at local top. 2H target: Support level consolidation."
    elif is_bullish:
        outlook = "Trend health: Positive. 2H target: New local high exploration."
    else:
        outlook = "Trend health: Negative. 2H target: Lower liquidity zone search."

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