from typing import List, Tuple
from pydantic import BaseModel

############################################
################ENTITIES#####################
############################################
class Polluant(BaseModel):
    name: str
    quantity: float

class EEE_QSTR(BaseModel):
    no_qstr: int
    answer: str

#Potentially change that for a stand lib for polygones Geopandas?
class Polygone(BaseModel):
    name: str
    points: List[Tuple[float, float]]


############################################
################REQUESTS#####################
############################################

class IndicateursRequest(BaseModel):
    # Define the fields for your request body here
    poly: Polygone
    eee_qstr: List[EEE_QSTR]
    pollution_qstr: List[Polluant]
