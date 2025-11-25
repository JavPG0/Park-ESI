from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()

@app.get("/results")
def get_results():
    results_path = BASE_DIR / "output" / "results.json"
    if not results_path.exists():
        return {"error": "results.json no existe aún"}
    with open(results_path, "r") as f:
        data = json.load(f)
    return data

@app.get("/parking")
def get_parking_slots():
    slots_path = BASE_DIR / "parking_slots.json"
    with open(slots_path, "r") as f:
        slots = json.load(f)
    return slots
