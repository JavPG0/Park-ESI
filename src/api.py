from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from .email_sender import send_emails
import json

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()

def load_users():
    user_path = BASE_DIR / "data/users.json"
    if not user_path.exists():
        return []
    with open(user_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    user_path = BASE_DIR / "data/users.json"
    with open(user_path, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

def load_vehicles():
    vehicle_path = BASE_DIR / "data/vehicles.json"
    if not vehicle_path.exists():
        return []
    with open(vehicle_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_vehicles(vehicles):
    vehicle_path = BASE_DIR / "data/vehicles.json"
    with open(vehicle_path, "w", encoding="utf-8") as f:
        json.dump(vehicles, f, indent=4)

def load_following_status():
    path = BASE_DIR / "data/results.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def send_all_emails(emails):
    send_emails(emails)

@app.get("/parking")
def get_parking_slots():
    slots_path = BASE_DIR / "data/parking_slots.json"
    with open(slots_path, "r") as f:
        slots = json.load(f)
    return slots


@app.post("/register/user")
def registerUser(user: dict):
    users = load_users()

    for u in users:
        if u["email"] == user["email"]:
            raise HTTPException(status_code=400,
                                detail="Este correo ya ha sido registrado.")

    users.append(user)
    save_users(users)
    return {"message": "Usuario registrado correctamente."}

@app.post("/login")
def login(user: dict):
    users = load_users()

    for u in users:
        if u["email"] == user["email"] and u["password"] == user["password"]:
            return {"message": "Login correcto."}

    raise HTTPException(status_code=401,
                        detail="Email o Contraseña incorrectos. Por favor, intente de nuevo.")

@app.post("/delete/user")
def deleteUser(data: dict):
    email = data.get("email")

    users = load_users()
    updated_users = [u for u in users if u["email"] != email]

    vehicles = load_vehicles()
    updated_vehicles = [v for v in vehicles if v["email"] != email]

    if len(updated_users) == len(users):
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    save_users(updated_users)
    save_vehicles(updated_vehicles)
    return {"message": "Usuario eliminado correctamente."}

@app.post("/register/vehicle")
def registerVehicle(vehicle: dict):
    vehicles = load_vehicles()

    for v in vehicles:
        if v["plate"] == vehicle["plate"] and vehicle["shared"] is False:
            raise HTTPException(status_code=400,
                                detail="Este vehículo ya ha sido registrado.")

    vehicles.append(vehicle)
    save_vehicles(vehicles)
    return {"message": "Vehículo registrado correctamente."}

@app.post("/consult")
def consult_vehicles(data: dict):
    email = data.get("email")

    vehicles = load_vehicles()
    user_vehicles = [v for v in vehicles if v["email"] == email]

    return JSONResponse(content=user_vehicles)

@app.post("/delete/vehicle")
def deleteVehicle(data: dict):
    plate = data.get("plate")

    vehicles = load_vehicles()
    updated = [v for v in vehicles if v["plate"] != plate]

    if len(updated) == len(vehicles):
        raise HTTPException(status_code=404, detail="Vehículo no encontrado.")

    save_vehicles(updated)
    return {"message": "Vehículo eliminado correctamente."}

@app.post("/get/blocking-vehicles")
def get_related_vehicles(data: dict):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email requerido")

    vehicles = load_vehicles()
    following = load_following_status()  # dict: {matricula: plaza | None}

    # Matrículas del usuario
    user_plates = {
        v["plate"]
        for v in vehicles
        if v["email"] == email
    }

    if not user_plates:
        return {"emails": []}

    # Plazas donde están los coches del usuario
    user_slots = {
        following[plate]
        for plate in user_plates
        if plate in following and following[plate] is not None
    }

    if not user_slots:
        return {"emails": []}

    # Plazas objetivo (+25)
    target_slots = {slot + 25 for slot in user_slots}

    # Matrículas aparcadas en esas plazas
    plates_in_target_slots = {
        plate
        for plate, slot in following.items()
        if slot in target_slots
    }

    # Emails de esos vehículos
    result_emails = {
        v["email"]
        for v in vehicles
        if v["plate"] in plates_in_target_slots
    }

    return {"emails": list(result_emails)}

@app.post("/send/emails")
def get_related_vehicles(data: dict):
    emails = data.get("emails")
    send_all_emails(emails)
