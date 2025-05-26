import enum
from typing import List, Tuple
from fastapi import FastAPI
from pydantic import BaseModel
import geojson
import json
from typing import List, Literal
from fastapi import Body

from app.indicators.indicateur1 import compute_indicateur1
from app.types.types import IndicateursRequest

from bq_impact_indicators.carbon_stocks import compute_carbon_stocks
from bq_impact_indicators.connectivity import compute_connectivity
from bq_impact_indicators.conservation import compute_conservation
from bq_impact_indicators.ecosystem_services import compute_ecosystem_services
from bq_impact_indicators.habitat_destruction import compute_habitat_destruction
from bq_impact_indicators.pollution import compute_pollution
from bq_impact_indicators.human_footprint import compute_human_footprint
from bq_impact_indicators.invasive_exotics import compute_invasive_exotics
from bq_impact_indicators.species_at_risk import compute_species_at_risk


app = FastAPI(  
    root_path="/api/impacts",  # Ensure this matches your Nginx path
    #openapi_url="/api/impacts/openapi.json",
    #docs_url="/api/impacts/docs",
    #redoc_url="/api/impacts/redoc"
    )

class InvasiveExoticsRequest(BaseModel):
    geojson: dict
    survey: dict

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


@app.post("/connectivity")
def connectivity_indicator(geojson: dict = Body(
        ...,
        description="Polygone GeoJSON décrivant la zone d'intérêt.",
        example={"type": "Polygon", "coordinates": [ [ [ -72.105757756705444, 45.373220204006415 ], [ -72.112517052360417, 45.370936688061363 ], [ -72.111975292909051, 45.387204727363311 ], [ -72.105372599595512, 45.387014484949106 ], [ -72.105757756705444, 45.373220204006415 ] ] ] },
    )
):
    """
    Endpoint to compute connectivity indicator.

    This endpoint receives a GeoJSON polygon and computes the connectivity indicator
    based on the provided geographical data.

    Args:

        geojson (dict): A dictionary representing the GeoJSON object containing geographical features.

    Returns:

        dict: A dictionary containing the computed connectivity indicator with intermediate results.
    """
    result = compute_connectivity(geojson)
    return result

@app.post("/carbon_stocks")
def carbon_stocks_indicator(geojson: dict = Body(
        ...,
        description="Polygone GeoJSON décrivant la zone d'intérêt.",
        example={"type": "Polygon", "coordinates": [ [ [ -72.105757756705444, 45.373220204006415 ], [ -72.112517052360417, 45.370936688061363 ], [ -72.111975292909051, 45.387204727363311 ], [ -72.105372599595512, 45.387014484949106 ], [ -72.105757756705444, 45.373220204006415 ] ] ] },
    )
):
    """
    Endpoint to calculate carbon stocks indicator.

    This endpoint receives a GeoJSON object and computes the carbon stocks
    based on the provided geographical data.

    Args:

        geojson (dict): A dictionary representing the GeoJSON object containing
                        the geographical data.

    Returns:

        dict: A dictionary with the carbons stock indicator and intermediate results.
    """
    result = compute_carbon_stocks(geojson)
    return result

@app.post("/pollution")
def pollution_indicator(survey: dict = Body(
        ...,
        description="Dictionnaire du format id:{'quantity': float, 'units': str (e.g., 'tonnes')}.",
        example={
            "1": {"quantity": 0.006856416, "units": "tonnes"},
            "4": {"quantity": 0.001469232, "units": "tonnes"},
            "254": {"quantity": 1.0651932, "units": "tonnes"},
            "255": {"quantity": 5.754492, "units": "tonnes"},
            "256": {"quantity": 0.13345524, "units": "tonnes"},
            "287": {"quantity": 0.04652568, "units": "tonnes"}
        }
    )
):
    """
    Endpoint to calculate the pollution indicator based on the provided survey data.

    Args:

        survey (dict): A dictionary containing survey data used to compute the pollution indicator.

    Returns:

        dict: A dictionary with the computed pollution indicator and intermediate results.
    """
    result = compute_pollution(survey)
    return result

@app.post("/conservation")
def conservation_indicator(geojson: dict = Body(
        ...,
        description="Polygone GeoJSON décrivant la zone d'intérêt.",
        examples=[{"type": "Polygon", "coordinates": [ [ [ -72.105757756705444, 45.373220204006415 ], [ -72.112517052360417, 45.370936688061363 ], [ -72.111975292909051, 45.387204727363311 ], [ -72.105372599595512, 45.387014484949106 ], [ -72.105757756705444, 45.373220204006415 ] ] ] }],
    ), 
    influence_distance: float = Body(
        ...,
        description="Distance d'influence en dehors du polygone en mètres.",
        examples=[500]
    )
):
    """
    Endpoint to calculate the conservation indicator for a given geographical area.

    Args:
        
        geojson (dict): A GeoJSON object representing the geographical area.
        
        influence_distance (float): The distance of influence outside of the geojson in meters.

    Returns:

        dict: A dictionary containing the conservation indicator result.
    """
    result = compute_conservation(geojson, influence_distance)
    return result

@app.post("/ecosystem_services")
def ecosystem_services_indicator(geojson: dict, distance_max: float, milieu: str = "urbain"):
    """
    Endpoint to calculate ecosystem services indicator.

    Args:

        geojson (dict): GeoJSON object representing the geographical area.
        
        distance_max (float): Maximum distance to consider for the calculation.
        
        milieu (str, optional): Type of environment, default is "urbain".

    Returns:

        dict: A dictionary containing the calculated ecosystem services.
    """
    result = compute_ecosystem_services(geojson, distance_max, milieu)
    return result

@app.post("/habitat_destruction")
def habitat_destruction_indicator(geojson: dict = Body(
        ...,
        description="Polygone GeoJSON décrivant la zone d'intérêt.",
        example={"type": "Polygon", "coordinates": [ [ [ -72.105757756705444, 45.373220204006415 ], [ -72.112517052360417, 45.370936688061363 ], [ -72.111975292909051, 45.387204727363311 ], [ -72.105372599595512, 45.387014484949106 ], [ -72.105757756705444, 45.373220204006415 ] ] ] },
    )
    ):
    """
    Endpoint to calculate the habitat destruction indicator.

    Args:

        geojson (dict): A GeoJSON object representing the geographical area.

    Returns:

        dict: A dictionary containing the calculated habitat destruction indicator.
    """
    result = compute_habitat_destruction(geojson)
    return result

@app.post("/human_footprint")
def human_footprint_indicator(geojson: dict = Body(
        ...,
        description="Polygone GeoJSON décrivant la zone d'intérêt.",
        example={"type": "Polygon", "coordinates": [ [ [ -72.105757756705444, 45.373220204006415 ], [ -72.112517052360417, 45.370936688061363 ], [ -72.111975292909051, 45.387204727363311 ], [ -72.105372599595512, 45.387014484949106 ], [ -72.105757756705444, 45.373220204006415 ] ] ] },
    )
):
    """
    Endpoint to calculate the human footprint indicator.

    Args:

        geojson (dict): A GeoJSON object representing the geographical area.

    Returns:

        dict: A dictionary containing the calculated human footprint indicator.
    """
    result = compute_human_footprint(geojson)
    return result

@app.post("/invasive_exotics")
def invasive_exotics_indicator(
        geojson: dict = Body(
            ...,
            description="Polygone GeoJSON décrivant la zone d'intérêt.",
            examples=[
                {"type": "Polygon", "coordinates": [ [ [ -72.105757756705444, 45.373220204006415 ], [ -72.112517052360417, 45.370936688061363 ], [ -72.111975292909051, 45.387204727363311 ], [ -72.105372599595512, 45.387014484949106 ], [ -72.105757756705444, 45.373220204006415 ] ] ] }
            ]
        ),
        survey: dict = Body(
            ...,
            description="Dictionnaire des réponses au sondage sur les exotiques envahissantes.",
            examples=[{"Q1": False, "Q2": False, "Q3": False, "Q4": False, "Q5": False, "Q6": False, "Q7": False, "Q8": False, "Q9": False}],
        )
    ):
    """
    Endpoint to calculate the invasive exotics indicator.

    Args:

        geojson (dict): A GeoJSON object representing the geographical area.

        survey (dict): A dictionary containing survey data used to compute the invasive exotics indicator.

    Returns:

        dict: A dictionary containing the calculated invasive exotics indicator.
    """
    result = compute_invasive_exotics(geojson, survey)
    return result

@app.post("/species_at_risk")
def species_at_risk_indicator(geojson: dict = Body(
        ...,
        description="Polygone GeoJSON décrivant la zone d'intérêt.",
        example={"type": "Polygon", "coordinates": [ [ [ -72.105757756705444, 45.373220204006415 ], [ -72.112517052360417, 45.370936688061363 ], [ -72.111975292909051, 45.387204727363311 ], [ -72.105372599595512, 45.387014484949106 ], [ -72.105757756705444, 45.373220204006415 ] ] ] },
    )
):
    """
    Endpoint to calculate the species at risk indicator.

    Args:

        geojson (dict): A GeoJSON object representing the geographical area.

    Returns:

        dict: A dictionary containing the calculated species at risk indicator.
    """
    result = compute_species_at_risk(geojson)
    return result