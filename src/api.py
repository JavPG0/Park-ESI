from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()

def load_users():
    user_path = BASE_DIR / "users.json"
    if not user_path.exists():
        return []
    with open(user_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    user_path = BASE_DIR / "users.json"
    with open(user_path, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

@app.get("/parking")
def get_parking_slots():
    slots_path = BASE_DIR / "parking_slots.json"
    with open(slots_path, "r") as f:
        slots = json.load(f)
    return slots


@app.post("/register")
def register(user: dict):
    users = load_users()

    # Evitar duplicados
    for u in users:
        if u["email"] == user["email"]:
            raise HTTPException(status_code=400,
                                detail="Este correo ya ha sido registrado.")

    users.append(user)
    save_users(users)
    return {"message": "Usuario registrado correctamente."}

@app.post("/login")
def login(credentials: dict):
    users = load_users()

    for u in users:
        if u["email"] == credentials["email"] and u["password"] == credentials["password"]:
            return {"message": "Login correcto."}

    raise HTTPException(status_code=401,
                        detail="Email o Contraseña incorrectos. Por favor, intente de nuevo.")
