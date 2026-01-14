from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import build_state

app = FastAPI()

# Permette a Flutter di comunicare con il server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ranking/state")
def ranking_state(profile: str = "balanced"):
    try:
        # Chiama la funzione build_state definita in app/api.py
        return build_state(profile)
    except Exception as e:
        print(f"ERRORE SERVER: {e}")
        return {"last_valid_up": [], "last_valid_down": []}

@app.get("/")
def health():
    return {"status": "active", "message": "Momentum Backend is running"}