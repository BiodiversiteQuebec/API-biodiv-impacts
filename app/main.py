from typing import List, Tuple
from fastapi import FastAPI
from pydantic import BaseModel

from app.indicators.indicateur1 import compute_indicateur1
from app.types.types import IndicateursRequest


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


# This is where you could put your code for Indicateur 1
@app.post("/indicateurs")
async def indicateurs(request: IndicateursRequest):
    poly, eee_qstr, pollution_qstr = request.poly, request.eee_qstr, request.pollution_qstr

    ind1 = compute_indicateur1(poly, eee_qstr, pollution_qstr)
    return {"message": "Hello World"}
