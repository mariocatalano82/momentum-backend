from fastapi import FastAPI
from app.api import build_state

app = FastAPI(title="Momentum Backend", version="1.0")

@app.get("/ranking/state")
def ranking_state(profile: str = "balanced"):
    return build_state(profile)
