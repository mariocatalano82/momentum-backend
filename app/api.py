import json
import os
from app.indicators import compute_confidence, build_chart, tech_context
from app.datasources import fetch_assets_snapshot

def build_state(profile: str):
    # Scarica dati (Binance -> Kraken Fallback)
    all_assets = fetch_assets_snapshot()
    
    if not all_assets:
        return {"error": "No data available", "is_live": False}

    MAJORS = ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE"]
    enriched = []
    
    for a in all_assets:
        # Usa change_1h_est dai datasource
        c1h = a["change_1h_est"]
        c24 = a["change_24h"]
        
        prob = compute_confidence(c1h, c24, profile, a["symbol"])
        chart = build_chart(c1h)
        # Genera i testi parlanti
        tech = tech_context(c1h, c24, a["symbol"], prob)
        
        enriched.append({
            "symbol": a["symbol"],
            "change_1h": round(c1h, 2),
            "change_24h": round(c24, 2),
            "probability": prob,
            "chart_data": chart,
            "tech": tech
        })

    # Ordinamento e Filtri
    up = sorted([x for x in enriched if x["change_1h"] > 0 and x["symbol"] not in MAJORS], 
                key=lambda x: x["probability"], reverse=True)[:5]
    down = sorted([x for x in enriched if x["change_1h"] < 0 and x["symbol"] not in MAJORS], 
                  key=lambda x: x["probability"], reverse=True)[:5]
    leaders = [x for x in enriched if x["symbol"] in MAJORS]

    return {
        "is_live": True,
        "market_leaders": leaders,
        "last_valid_up": up,
        "last_valid_down": down
    }