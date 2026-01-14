from fastapi import FastAPI
from app.api import build_state

app = FastAPI()

@app.get("/ranking/state")
def ranking_state(profile: str = "balanced"):
    return build_state(profile)
