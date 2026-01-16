from fastapi import FastAPI, Query
from app.api import build_state

app = FastAPI(title="Momentum Backend", version="1.0.0")


@app.get("/ranking/state")
def ranking_state(profile: str = Query("balanced")):
    """
    Main public endpoint.
    Always returns a ranking, using fallback if needed.
    """
    return build_state(profile)
