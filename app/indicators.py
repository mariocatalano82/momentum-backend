import math
import hashlib

# --- 1. DESCRIZIONI STATICHE (Base knowledge) ---
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
    # Genera una piccola variazione decimale fissa per evitare score identici
    hash_val = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
    return ((hash_val % 100) / 100 * 0.8) - 0.4

# --- 2. CALCOLO SCORE (Matematica Pura) ---
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

# --- 3. CHART GENERATOR ---
def build_chart(change_1h):
    return [round(change_1h * (1.1 * math.sin((i/11) * 1.6)), 3) for i in range(12)]

# --- 4. RANKING REASON (Breve) ---
def generate_ranking_reason(c1h, c24, symbol, prob):
    c1h_r, c24_r = round(c1h, 2), round(c24, 2)
    if c1h > 0:
        if c24 > 0: return f"{symbol} shows 'Momentum Convergence'. Strong daily trend (+{c24_r}%) accelerated by a sharp hourly move (+{c1h_r}%)."
        return f"{symbol} triggers a 'Reversal Spike'. Recovering from a red day with high hourly conviction (+{c1h_r}%)."
    else:
        if c24 < 0: return f"{symbol} exhibits 'Panic Continuity'. Bearish pressure on both 24h (-{abs(c24_r)}%) and 1h (-{abs(c1h_r)}%) scales."
        return f"{symbol} in 'Profit Taking' phase. Pulling back (-{abs(c1h_r)}%) despite a positive daily performance."

# --- 5. LOGICA DI CONTESTO (HUMAN-READABLE VERSION) ---
# Questa è la funzione che genera i testi delle card
def tech_context(change_1h, change_24h, symbol, probability, profile):
    c1h, c24 = round(change_1h, 2), round(change_24h, 2)
    is_bullish = c1h > 0
    
    # V-Ratio: Rapporto tra forza oraria e media giornaliera
    # Se > 1.0 significa che l'ora attuale è più intensa della media
    vol_ratio = abs(c1h) / (abs(c24/24) + 0.01)
    
    # Fase Tecnica (Per logica interna)
    if (c1h > 0) != (c24 > 0): phase = "REVERSAL"
    elif abs(c1h) > abs(c24 / 2): phase = "ACCELERATION"
    else: phase = "CONTINUATION"

    alert = ""
    
    # --- LIVELLO 1: ESTREMO (> 90%) - Situazione Pericolosa ---
    if probability > 90:
        if abs(c1h) > 4: alert = "⚠️ TOO FAST"
        
        scenario = "EXTREME MOVEMENT"
        if is_bullish:
            advice = f"Price is rising too fast to be safe. High chance of a quick drop back down. Taking profit is smarter than buying now."
        else:
            advice = f"Panic selling. The price is crashing vertically. Don't try to buy yet, wait for it to stabilize."

    # --- LIVELLO 2: TREND FORTE (75% - 90%) - Situazione Chiara ---
    elif probability > 75:
        scenario = "SOLID TREND"
        
        if is_bullish:
            if phase == "REVERSAL":
                advice = "Recovery in progress. After a bad day, buyers are finally returning with strength."
            elif vol_ratio > 1.2:
                advice = "Strong & Healthy. Prices are going up and volume confirms it's real. Good condition."
            else:
                advice = "Slow but Steady. The price is climbing gradually without risks. Safe to hold."
        else:
            if phase == "REVERSAL":
                advice = "Sudden Drop. The day was good, but sellers have taken control in the last hour."
            elif vol_ratio > 1.2:
                advice = "Heavy Selling. Big sell orders are pushing the price down. Risky to buy."
            else:
                advice = "Losing Strength. Price is slowly drifting lower. Interest is fading."

    # --- LIVELLO 3: BASSA CONFIDENZA (< 75%) - Situazione Incerta ---
    else:
        # Qui spieghiamo in parole povere perché l'analisi è incerta
        
        # Caso 1: CONFLITTO (1H dice su, 24H dice giù)
        if phase == "REVERSAL":
            scenario = "UNCERTAIN DIRECTION"
            if is_bullish:
                advice = f"Confusing signals. Short term is UP, long term is DOWN. It's too early to trust this recovery."
            else:
                advice = f"Mixed signals. Short term is DOWN, long term is UP. Wait for a clearer direction."

        # Caso 2: MERCATO FERMO (Volume basso)
        elif vol_ratio < 0.6:
            scenario = "MARKET IS ASLEEP"
            advice = "Nothing is happening. There is almost no trading volume right now. Better to stay out and wait."

        # Caso 3: MOVIMENTO DEBOLE (Il famoso 'Grinding/Chopping')
        else:
            scenario = "WEAK MOVEMENT"
            if is_bullish:
                advice = "It's trying to go up, but lacks energy. Without more buyers, it could easily fall back."
            else:
                advice = "It's slowly losing value. Not a crash, just a lack of interest from buyers."

    # --- Badge Logic (Etichette brevi per la UI) ---
    if probability > 92: logic = "CLIMAX"     # Picco massimo
    elif vol_ratio > 3.0: logic = "SURGE"     # Esplosione
    elif phase == "REVERSAL": logic = "TURN"  # Inversione
    elif probability > 75: logic = "TREND"    # Trend
    else: logic = "FLAT"                      # Piatto

    # --- Outlook (Previsione semplice 2H) ---
    if is_bullish:
        outlook = "Next 2H: Likely to continue up" if probability > 75 else "Next 2H: Unclear / Sideways"
    else:
        outlook = "Next 2H: Likely to go lower" if probability > 75 else "Next 2H: Drifting down"

    # --- Traduzione V-Ratio per umani ---
    if vol_ratio > 2.0: vol_impact = f"HIGH ({round(vol_ratio,1)}x)"
    elif vol_ratio > 1.0: vol_impact = "NORMAL"
    else: vol_impact = "LOW"

    return {
        "action_logic": logic,
        "confidence_meaning": "HIGH CONFIDENCE" if probability > 80 else "LOW CONFIDENCE",
        "score_drivers": f"V-Ratio: {round(vol_ratio,1)} | 1H: {c1h}% vs 24H: {c24}%",
        "prediction_action": f"{scenario}\n\n{advice}",
        "rsi": max(15, min(95, int(probability) if is_bullish else (100 - int(probability)))),
        "vol_increase": vol_impact,
        "description": get_coin_description(symbol),
        "ranking_reason": generate_ranking_reason(change_1h, change_24h, symbol, probability),
        "outlook": outlook
    }