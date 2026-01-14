from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import get_top_up, get_top_down

app = FastAPI(title="Momentum Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/ranking/up")
def ranking_up():
    return get_top_up()

@app.get("/ranking/down")
def ranking_down():
    return get_top_down()
