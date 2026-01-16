import json
import os
from datetime import datetime
from app.indicators import compute_confidence, build_chart, tech_context
from app.datasources import fetch_assets_snapshot

DB_FILE = "last_valid_state.json"

def build_state(profile: str):
    all_assets = fetch_assets_snapshot()
    
    if not all_assets:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                state = json.load(f)
                state["is_live"] = False
                return state
        return {"error": "No data", "is_live": False}

    MAJORS = ["BTC", "ETH", "SOL", "BNB", "XRP"]
    enriched = []
    
    for a in all_assets:
        conf = compute_confidence(a["change_1h"], a["change_24h"], profile, a["symbol"])
        chart = build_chart(a["change_1h"])
        # Passiamo anche il symbol per personalizzare il testo friendly
        tech = tech_context(a["change_1h"], a["change_24h"], a["symbol"])
        
        enriched.append({
            "symbol": a["symbol"],
            "change_1h": a["change_1h"],
            "change_24h": a["change_24h"],
            "probability": conf,
            "chart_data": chart,
            "tech": tech
        })

    up = sorted([x for x in enriched if x["change_1h"] > 0 and x["symbol"] not in MAJORS], 
                key=lambda x: x["probability"], reverse=True)[:5]
    down = sorted([x for x in enriched if x["change_1h"] < 0 and x["symbol"] not in MAJORS], 
                  key=lambda x: x["probability"], reverse=True)[:5]
    leaders = [x for x in enriched if x["symbol"] in MAJORS]

    state = {
        "is_live": True,
        "timestamp": datetime.now().isoformat(),
        "market_leaders": leaders,
        "last_valid_up": up,
        "last_valid_down": down
    }
    
    with open(DB_FILE, "w") as f:
        json.dump(state, f)
        
    return state