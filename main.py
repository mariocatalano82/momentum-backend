from fastapi import FastAPI, Query
from app.api import build_market_state

app = FastAPI(title="Momentum Backend")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/ranking/state")
def ranking_state(profile: str = Query("balanced", regex="^(balanced|aggressive)$")):
    return build_market_state(profile)
