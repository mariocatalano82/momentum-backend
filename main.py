from fastapi import FastAPI
from app.api import router

app = FastAPI(title="Momentum Backend")

app.include_router(router)

@app.get("/")
def root():
    return {"status": "ok"}
