def build_state(profile: str):
    now_ts = datetime.now().isoformat()
    all_assets = fetch_assets_snapshot()
    
    if not all_assets:
        return load_from_disk() or {"error": "No data"}

    # Definiamo i Majors che vogliamo sempre monitorare
    MAJORS_LIST = ["BTC", "ETH", "SOL", "BNB", "XRP"]
    
    enriched = []
    for a in all_assets:
        conf = compute_confidence(a["change_1h"], a["change_24h"], profile, a["symbol"])
        enriched.append({
            "symbol": a["symbol"],
            "name": a["symbol"], # Se vuoi i nomi lunghi, servirebbe una mappa
            "change_1h": round(a["change_1h"], 2),
            "change_24h": round(a["change_24h"], 2),
            "probability": conf,
            "chart_data": build_chart(a["change_1h"]),
            "tech": tech_context(a["change_1h"], a["change_24h"])
        })

    # 1. Top Up
    up = sorted([x for x in enriched if x["change_1h"] > 0], key=lambda x: x["probability"], reverse=True)[:5]
    
    # 2. Top Down
    down = sorted([x for x in enriched if x["change_1h"] < 0], key=lambda x: x["probability"], reverse=True)[:5]
    
    # 3. Market Leaders (Majors)
    leaders = [x for x in enriched if x["symbol"] in MAJORS_LIST]
    # Ordiniamo i majors per capitalizzazione (approssimata qui dalla lista fissa)
    leaders.sort(key=lambda x: MAJORS_LIST.index(x["symbol"]))

    new_state = {
        "profile": profile,
        "timestamp": now_ts,
        "is_live": True,
        "last_valid_up": up,
        "last_valid_down": down,
        "market_leaders": leaders # Nuova sezione!
    }
    save_to_disk(new_state)
    return new_state