import json
import os
from datetime import datetime
from app.indicators import compute_confidence, build_chart, tech_context
from app.datasources import fetch_assets_snapshot

DB_FILE = "last_valid_state.json"

def save_to_disk(state):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        print(f"Disk save error: {e}")

def load_from_disk():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return None
    return None

def build_state(profile: str):
    # Ora datetime è importato correttamente
    now_ts = datetime.now().isoformat()
    
    all_assets = fetch_assets_snapshot()
    
    if not all_assets:
        last_state = load_from_disk()
        if last_state:
            last_state["is_live"] = False
            return last_state
        return {"error": "No data available", "is_live": False}

    # Definiamo i Majors (Market Leaders)
    MAJORS_LIST = ["BTC", "ETH", "SOL", "BNB", "XRP"]
    
    enriched = []
    for a in all_assets:
        # Aggiunto 'symbol' per confidenza deterministica
        conf = compute_confidence(a["change_1h"], a["change_24h"], profile, a["symbol"])
        enriched.append({
            "symbol": a["symbol"],
            "name": a["symbol"],
            "change_1h": round(a["change_1h"], 2),
            "change_24h": round(a["change_24h"], 2),
            "probability": conf,
            "chart_data": build_chart(a["change_1h"]),
            "tech": tech_context(a["change_1h"], a["change_24h"])
        })

    # Ranking
    up = sorted([x for x in enriched if x["change_1h"] > 0], key=lambda x: x["probability"], reverse=True)[:5]
    down = sorted([x for x in enriched if x["change_1h"] < 0], key=lambda x: x["probability"], reverse=True)[:5]
    
    # Sezione Leaders
    leaders = [x for x in enriched if x["symbol"] in MAJORS_LIST]
    leaders.sort(key=lambda x: MAJORS_LIST.index(x["symbol"]))

    new_state = {
        "profile": profile,
        "timestamp": now_ts,
        "is_live": True,
        "market_leaders": leaders,
        "last_valid_up": up,
        "last_valid_down": down
    }
    
    save_to_disk(new_state)
    return new_state