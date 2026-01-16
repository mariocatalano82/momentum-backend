from datetime import datetime
import json
import os
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
    # Usiamo datetime correttamente ora che è importato
    now_ts = datetime.now().isoformat()
    assets = fetch_assets_snapshot()
    
    if assets:
        enriched = []
        for a in assets:
            conf = compute_confidence(a["change_1h"], a["change_24h"], profile)
            enriched.append({
                "symbol": a["symbol"],
                "name": a["symbol"], # Binance non dà il nome lungo
                "change_1h": round(a["change_1h"], 2),
                "change_24h": round(a["change_24h"], 2),
                "probability": conf,
                "chart_data": build_chart(a["change_1h"]),
                "tech": tech_context(a["change_1h"], a["change_24h"])
            })

        # Ranking basato su confidenza e performance
        up = sorted([x for x in enriched if x["change_1h"] > 0], 
                    key=lambda x: (x["probability"], x["change_1h"]), reverse=True)[:5]
        down = sorted([x for x in enriched if x["change_1h"] < 0], 
                      key=lambda x: (x["probability"], abs(x["change_1h"])), reverse=True)[:5]

        new_state = {
            "profile": profile,
            "timestamp": now_ts,
            "is_live": True,
            "last_valid_up": up,
            "last_valid_down": down
        }
        save_to_disk(new_state)
        return new_state
    else:
        last_state = load_from_disk()
        if last_state:
            last_state["is_live"] = False
            return last_state
        return {"error": "No data available", "is_live": False}