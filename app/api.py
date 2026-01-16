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

    MAJORS_LIST = ["BTC", "ETH", "SOL", "BNB", "XRP"]
    enriched = []
    
    for a in all_assets:
        prob = compute_confidence(a["change_1h"], a["change_24h"], profile, a["symbol"])
        tech = tech_context(a["change_1h"], a["change_24h"])
        enriched.append({
            "symbol": a["symbol"], "name": a["symbol"],
            "change_1h": a["change_1h"], "change_24h": a["change_24h"],
            "probability": prob, "chart_data": build_chart(a["change_1h"]), "tech": tech
        })

    # Ranking per probabilità invece che per variazione lineare
    up = sorted([x for x in enriched if x["change_1h"] > 0 and x["symbol"] not in MAJORS_LIST], 
                key=lambda x: x["probability"], reverse=True)[:5]
    down = sorted([x for x in enriched if x["change_1h"] < 0 and x["symbol"] not in MAJORS_LIST], 
                  key=lambda x: x["probability"], reverse=True)[:5]

    state = {
        "is_live": True,
        "timestamp": datetime.now().isoformat(),
        "market_leaders": [x for x in enriched if x["symbol"] in MAJORS_LIST],
        "last_valid_up": up,
        "last_valid_down": down
    }
    
    with open(DB_FILE, "w") as f: json.dump(state, f)
    return state