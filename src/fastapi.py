from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json

app = FastAPI()

@app.get("/results")
def get_results():
    with open("output/results.json", "r") as f:
        data = json.load(f)
    return JSONResponse(content=data)

@app.get("/parking")
def parking_state():
    with open("parking_slots.json", "r") as f:
        slots = json.load(f)
    return JSONResponse(content=slots)
