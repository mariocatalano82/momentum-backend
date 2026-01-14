from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import time
from typing import List, Dict

from app.api import refresh_cache_safe, get_cached_up, get_cached_down

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- HEALTH ----------------
@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/healthz")
def healthz():
    return {"ok": True}

# ---------------- ENDPOINTS ----------------
@app.get("/ranking/up")
def ranking_up(mode: str = Query("balanced")):
    refresh_cache_safe()
    return get_cached_up()

@app.get("/ranking/down")
def ranking_down(mode: str = Query("balanced")):
    refresh_cache_safe()
    return get_cached_down()
