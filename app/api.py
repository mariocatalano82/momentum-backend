from .datasources import fetch_binance_tickers
from .indicators import compute_probability, build_chart_data
from config import MAX_COINS

def build_state(profile: str = "balanced"):
    raw = fetch_binance_tickers()

    coins = []
    for c in raw:
        try:
            change_24h = float(c["priceChangePercent"])
            change_1h = change_24h / 24

            coins.append({
                "symbol": c["symbol"].replace("USDT", ""),
                "name": c["symbol"].replace("USDT", ""),
                "change_1h": round(change_1h, 1),
                "change_24h": round(change_24h, 1),
                "probability": compute_probability(change_24h),
                "explanation": "Relative momentum vs market average (Binance)",
                "score": change_24h,
                "chart_data": build_chart_data(change_1h),
            })
        except Exception:
            continue

    up = sorted(coins, key=lambda x: x["score"], reverse=True)[:MAX_COINS]
    down = sorted(coins, key=lambda x: x["score"])[:MAX_COINS]

    return {
        "profile": profile,
        "last_valid_up": up,
        "last_valid_down": down,
    }
