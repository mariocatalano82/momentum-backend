from app.indicators import *
from app.config import WEIGHTS

def score_asset(asset):
    change = asset.get("price_change_percentage_1h_in_currency") or 0
    volume = asset.get("total_volume") or 0

    scores = {
        "momentum": momentum(change),
        "volume": volume_score(volume),
        "rsi": rsi_score(),
        "trend": trend_score(change),
        "volatility": volatility_score(change)
    }

    growth_score = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
    drop_score = -growth_score

    return round(growth_score * 100, 1), round(drop_score * 100, 1)
