import enum
from typing import List, Tuple
from fastapi import FastAPI
from pydantic import BaseModel

from app.indicators.indicateur1 import compute_indicateur1
from app.types.types import IndicateursRequest


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


def generate_response(indicators: List[Tuple[str, float]]) -> dict:
    return {f"indicator_{i+1}": {"value": value, "elapsed_time": elapsed_time} for i, (value, elapsed_time) in enumerate(indicators)}

# This is where you could put your code for Indicateur 1
@app.post("/indicateurs")
async def indicateurs(request: IndicateursRequest):
    poly, eee_qstr, pollution_qstr = request.poly, request.eee_qstr, request.pollution_qstr

    indicators = []
    indicators.append(compute_indicateur1())


    res = generate_response(indicators)
    return res
