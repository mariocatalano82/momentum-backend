from fastapi import FastAPI
from app.api import build_state

app = FastAPI()

@app.get("/ranking/state")
def ranking_state(profile: str = "balanced"):
    try:
        return build_state(profile)
    except Exception as e:
        print("STATE ERROR:", e)
        return {
            "last_valid_up": [],
            "last_valid_down": []
        }
