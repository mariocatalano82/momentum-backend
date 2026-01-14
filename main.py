from fastapi import FastAPI
from app.api import router as api_router

app = FastAPI(title="Momentum Backend")

app.include_router(api_router)

@app.get("/")
def root():
    return {"status": "ok"}
