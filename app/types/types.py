import json
from typing import Any, List, Tuple, Union, Dict, Optional
from pydantic import BaseModel
from shapely import Polygon

############################################
################ENTITIES#####################
############################################

#Potentially change that for a stand lib for polygones Geopandas?
class Polygone(BaseModel):
    name: Optional[str] = "Zone d'intérêt"
    points: List[Tuple[float, float]]


    def model_dump_json(self):
        return {
            "name": self.name,
            "points": self.points
        }
    def to_geojson(self):
        polygon = Polygon(self.points)
        return polygon.__geo_interface__




############################################
################REQUESTS#####################
############################################

class IndicateursRequest(BaseModel):
    # Define the fields for your request body here
    poly: Union[Polygone, Dict[str, Any]]
    eee_qstr: Dict[str, Any] = {}
    pollution_qstr: Dict[str, Any] = {}
    project_name: Optional[str] = "Projet Démo"
    creator: Optional[str] = "Biodiversité Québec"
    created_date: Optional[str] = "2025-01-01T00:00:00Z"

