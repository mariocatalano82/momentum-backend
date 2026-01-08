from fastapi import APIRouter
from app.datasources import get_top_50
from app.ranking import score_asset

router = APIRouter()

@router.get("/ranking/up")
def ranking_up():
    assets = get_top_50()
    ranked = []

    for asset in assets:
        growth, _ = score_asset(asset)
        ranked.append({
            "symbol": asset["symbol"].upper(),
            "price": asset["current_price"],
            "probability": growth,
            "change_1h": asset["price_change_percentage_1h_in_currency"],
            "explanation": "Positive momentum supported by volume"
        })

    ranked.sort(key=lambda x: x["probability"], reverse=True)
    return ranked[:5]

@router.get("/ranking/down")
def ranking_down():
    assets = get_top_50()
    ranked = []

    for asset in assets:
        _, drop = score_asset(asset)
        ranked.append({
            "symbol": asset["symbol"].upper(),
            "price": asset["current_price"],
            "probability": drop,
            "change_1h": asset["price_change_percentage_1h_in_currency"],
            "explanation": "Weak momentum and declining volume"
        })

    ranked.sort(key=lambda x: x["probability"], reverse=True)
    return ranked[:5]
