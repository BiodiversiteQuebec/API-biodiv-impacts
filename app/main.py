
import datetime
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from pydantic import BaseModel
import geojson
from fastapi import Body

from app.types.types import IndicateursRequest

from bq_impact_indicators import compute_carbon_stocks, compute_connectivity, compute_conservation, compute_ecosystem_services, compute_habitat_destruction, compute_invasive_exotics, compute_pollution, compute_species_at_risk, compute_human_footprint


from app.utils import (
    convert_to_geojson_polygon,
    save_request_data_as_json,
    to_eee_survey,
    NaNJSONResponse,
)



app = FastAPI(default_response_class=NaNJSONResponse)

class InvasiveExoticsRequest(BaseModel):
    geojson: dict
    survey: dict
    weights: dict = None

@app.get("/")
async def root():
    return {"message": "Hello World"}


# This is where you could put your code for Indicateur 1
@app.post("/indicateurs")
async def indicateurs(request: IndicateursRequest):
    start_time = time.time()
    poly, eee_qstr, pollution_qstr = request.poly, request.eee_qstr, request.pollution_qstr
    poly = convert_to_geojson_polygon(poly)
    
    eee_survey, eee_weights = to_eee_survey(eee_qstr)
    poll_survey = pollution_qstr

    functions = [
        (compute_connectivity, (poly,)),
        (compute_conservation, (poly, 10)),
        (compute_species_at_risk, (poly,)),
        (compute_ecosystem_services, (poly, 1000)),
        (compute_habitat_destruction, (poly,)),
        (compute_invasive_exotics, (poly, eee_survey, eee_weights)),
        (compute_pollution, (poll_survey,)),
        (compute_carbon_stocks, (poly,)),
        (compute_human_footprint, (poly,)),
    ]

    indicator_ids = {
        "compute_connectivity": "connectivity",
        "compute_conservation": "conservation",
        "compute_species_at_risk": "species_at_risk",
        "compute_ecosystem_services": "ecosystem_services",
        "compute_habitat_destruction": "habitat_destruction",
        "compute_invasive_exotics": "invasive_exotics",
        "compute_pollution": "pollution",
        "compute_carbon_stocks": "carbon_stocks",
        "compute_human_footprint": "human_footprint",
    }

    with ThreadPoolExecutor() as executor:
        func_to_future = {
            func: executor.submit(func, *args)
            for func, args in functions
        }
        
        indicators_list = []
        for func, args in functions:
            func_name = getattr(func, "__name__", getattr(func, "_mock_name", str(func)))
            default_id = indicator_ids.get(func_name, func_name)
            future = func_to_future[func]
            try:
                res = future.result()
                if isinstance(res, dict):
                    item = dict(res)
                    ind_name = item.pop("indicator_id", item.pop("indicator", default_id))
                    item.pop("indicator", None)
                    item.pop("name", None)
                    item = {"indicator_name": ind_name, **item}
                else:
                    item = {
                        "indicator_name": default_id,
                        "indicator_value": res,
                    }
                indicators_list.append(item)
            except Exception as e:
                print(f"Error computing indicator {func_name}: {e}")
                indicators_list.append({
                    "indicator_name": default_id,
                    "indicator_value": None,
                    "error": str(e),
                })

    total_computational_time = round(time.time() - start_time, 2)
    computed_date = datetime.datetime.now().isoformat()

    buffered_polygon = None
    for item in indicators_list:
        if isinstance(item, dict) and item.get("buffered_polygon"):
            buffered_polygon = item["buffered_polygon"]
            break

    area_of_interest = buffered_polygon
    project_name = request.project_name or "Projet Démo"
    creator = request.creator or "Biodiversité Québec"
    created_date = request.created_date or "2025-01-01T00:00:00Z"

    response = {
        "total_computational_time": total_computational_time,
        "polygon": poly,
        "area_of_interest": area_of_interest,
        "project_name": project_name,
        "creator": creator,
        "computed_date": computed_date,
        "created_date": created_date,
        "indicators": indicators_list,
    }


    save_request_data_as_json(poly, eee_qstr, pollution_qstr)
    return response


@app.post("/compute_connectivity")
def connectivity_indicator(geojson: dict):
    """
    Endpoint to compute connectivity indicator.

    This endpoint receives a GeoJSON object and computes the connectivity indicator
    based on the provided geographical data.

    Args:

        geojson (dict): A dictionary representing the GeoJSON object containing
                        geographical features.

    Returns:

        dict: A dictionary containing the computed connectivity indicator with the key "Connectivité".
    """
    poly = geojson.get("geojson", geojson)
    result = compute_connectivity(poly)
    return {"Connectivité": result}

@app.post("/carbon_stocks")
def carbon_stocks_indicator(geojson: dict):
    """
    Endpoint to calculate carbon stocks indicator.

    This endpoint receives a GeoJSON object and computes the carbon stocks
    based on the provided geographical data.

    Args:

        geojson (dict): A dictionary representing the GeoJSON object containing
                        the geographical data.

    Returns:

        dict: A dictionary with the key "Stocks de carbone" and the computed
            carbon stocks as the value.
    """
    poly = geojson.get("geojson", geojson)
    result = compute_carbon_stocks(poly)
    return {"Stocks de carbone": result}

@app.post("/pollution")
def pollution_indicator(survey: dict):
    """
    Endpoint to calculate the pollution indicator based on the provided survey data.

    Args:

        survey (dict): A dictionary containing survey data used to compute the pollution indicator.
                       Each key is a pollutant ID and value contains 'units' and 'quantity'.

    Returns:

        dict: A dictionary with the computed pollution indicator.
    """
    data = survey.get("survey", survey)
    result = compute_pollution(data)
    return {"Pollution": result}

@app.post("/conservation")
def conservation_indicator(geojson: dict, influence_distance: float = 0):
    """
    Endpoint to calculate the conservation indicator for a given geographical area.

    Args:
        
        geojson (dict): A GeoJSON object representing the geographical area.
        
        influence_distance (float): The distance of influence outside of the geojson in meters.

    Returns:

        dict: A dictionary containing the conservation indicator result.
    """
    if "influence_area" in geojson:
        influence_distance = geojson["influence_area"]
    elif "influence_distance" in geojson:
        influence_distance = geojson["influence_distance"]
    poly = geojson.get("geojson", geojson)
    result = compute_conservation(poly, influence_distance)
    return {"Conservation": result}

@app.post("/ecosystem_services")
def ecosystem_services_indicator(geojson: dict, distance_max: float = 1000, milieu: str = "urbain"):
    """
    Endpoint to calculate ecosystem services indicator.

    Args:

        geojson (dict): GeoJSON object representing the geographical area.
        
        distance_max (float): Maximum distance to consider for the calculation.
        
        milieu (str, optional): Type of environment, default is "urbain".

    Returns:

        dict: A dictionary containing the calculated ecosystem services.
    """
    if "distance_max" in geojson:
        distance_max = geojson["distance_max"]
    if "milieu" in geojson:
        milieu = geojson["milieu"]
    poly = geojson.get("geojson", geojson)
    result = compute_ecosystem_services(poly, distance_max, milieu)
    return {"Services écosystémiques": result}

@app.post("/habitat_destruction")
def habitat_destruction_indicator(geojson: dict):
    """
    Endpoint to calculate the habitat destruction indicator.

    Args:

        geojson (dict): A GeoJSON object representing the geographical area.

    Returns:

        dict: A dictionary containing the calculated habitat destruction indicator.
    """
    poly = geojson.get("geojson", geojson)
    result = compute_habitat_destruction(poly)
    return {"Destruction de l'habitat": result}

@app.post("/human_footprint")
def human_footprint_indicator(geojson: dict):
    """
    Endpoint to calculate the human footprint indicator.

    Args:

        geojson (dict): A GeoJSON object representing the geographical area.

    Returns:

        dict: A dictionary containing the calculated human footprint indicator.
    """
    poly = geojson.get("geojson", geojson)
    result = compute_human_footprint(poly)
    return {"Empreinte humaine": result}

@app.post("/invasive_exotics")
def invasive_exotics_indicator(
        geojson: dict = Body(...),
        survey: dict = Body(...),
        weights: dict = Body(None)):
    """
    Endpoint to calculate the invasive exotics indicator.

    Args:

        geojson (dict): A GeoJSON object representing the geographical area.

        survey (dict): A dictionary containing survey data used to compute the invasive exotics indicator.

        weights (dict, optional): A dictionary containing weights for each survey question.

    Returns:

        dict: A dictionary containing the calculated invasive exotics indicator.

    Usage:

    {
      "geojson": {
        "type": "Polygon",
        "coordinates": [
            [
                [-71.989021573308534, 45.404000415469056],
                [-71.987038174572334, 45.402959401362089],
                [-71.98540963380141, 45.404505556821491],
                [-71.987028443356962, 45.40533493226846],
                [-71.987140253500854, 45.405362234064313],
                [-71.987237484510757, 45.405372474057657],
                [-71.987315263440109, 45.405372473936815],
                [-71.987402772819166, 45.405369066780658],
                [-71.987480546508735, 45.405351995013334],
                [-71.987543748498041, 45.405324697182159],
                [-71.987621531580913, 45.405304216052308],
                [-71.987670135059872, 45.405266675018261],
                [-71.989021573308534, 45.404000415469056]
            ]
        eee_weights]
      },
      "survey": {"Q1": false, "Q2": false, "Q3": false, "Q4": false, "Q5": false, "Q6": false, "Q7": false, "Q8": false, "Q9": true, "Q10": true},
      "weights": {"Q1": 0.0, "Q2": 0.0, "Q3": 0.0, "Q4": 0.0, "Q5": 0.0, "Q6": 0.0, "Q7": 0.0, "Q8": 0.0, "Q9": 1.0, "Q10": 1.0}
    }
    """
    poly = geojson.get("geojson", geojson)
    if weights is None:
        weights = {k: 0.0 for k in survey.keys()}
    result = compute_invasive_exotics(poly, survey, weights)
    return {"Espèces exotiques envahissantes": result}

@app.post("/species_at_risk")
def species_at_risk_indicator(geojson: dict = Body(...), influence_area: float = 0):
    """
    Endpoint to calculate the species at risk indicator.

    Args:

        geojson (dict): A GeoJSON object representing the geographical area.

        influence_area (float, optional): The distance corresponding to the radius of the influence area in meters. Default is 0.

    Returns:

        dict: A dictionary containing the calculated species at risk indicator.
    """
    if "influence_area" in geojson:
        influence_area = geojson["influence_area"]
    elif "influence_distance" in geojson:
        influence_area = geojson["influence_distance"]
    poly = geojson.get("geojson", geojson)
    result = compute_species_at_risk(poly, influence_area)
    return {"Espèces en péril": result}