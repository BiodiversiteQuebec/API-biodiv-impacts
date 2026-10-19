import datetime
import time
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException
import geojson

from app.types.types import DataFormSubmission

from bq_impact_indicators import (
    compute_carbon_stocks,
    compute_connectivity,
    compute_conservation,
    compute_ecosystem_services,
    compute_habitat_destruction,
    compute_invasive_exotics,
    compute_pollution,
    compute_species_at_risk,
    compute_human_footprint,
)

from app.utils import (
    convert_to_geojson_polygon,
    extract_eee_survey,
    parse_influence_distance,
    save_request_log,
    NaNJSONResponse,
)

app = FastAPI(default_response_class=NaNJSONResponse)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/indicateurs")
async def indicateurs(submission: DataFormSubmission):
    start_time = time.time()
    form = submission.form

    if not form.empriseGeospatiale:
        raise HTTPException(
            status_code=400,
            detail="Une emprise géospatiale (polygone) est requise pour calculer les indicateurs."
        )

    try:
        poly = convert_to_geojson_polygon(form.empriseGeospatiale)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erreur de format pour l'emprise géospatiale : {str(e)}"
        )

    project_name = form.nomProjet.strip() if form.nomProjet else "Projet Démo"
    creator = form.nomPromoteur.strip() if form.nomPromoteur else "Biodiversité Québec"
    influence_distance = parse_influence_distance(form.aireInfluenceValeur)
    eee_survey, eee_weights = extract_eee_survey(form)

    functions = [
        (compute_connectivity, (poly,)),
        (compute_conservation, (poly, influence_distance)),
        (compute_species_at_risk, (poly, influence_distance)),
        (compute_ecosystem_services, (poly, 1000)),
        (compute_habitat_destruction, (poly,)),
        (compute_invasive_exotics, (poly, eee_survey, eee_weights)),
        (compute_pollution, ({},)),
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
            func_name = getattr(func, "__name__", str(func))
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

    response = {
        "projectId": submission.projectId,
        "project_name": project_name,
        "creator": creator,
        "total_computational_time": total_computational_time,
        "polygon": poly,
        "area_of_interest": buffered_polygon,
        "computed_date": computed_date,
        "created_date": computed_date,
        "indicators": indicators_list,
    }

    save_request_log(submission.model_dump())
    return response


# Individual indicator endpoints (for standalone calls / debugging)
@app.post("/compute_connectivity")
def connectivity_indicator(geojson: dict):
    poly = convert_to_geojson_polygon(geojson.get("geojson", geojson))
    return {"Connectivité": compute_connectivity(poly)}


@app.post("/carbon_stocks")
def carbon_stocks_indicator(geojson: dict):
    poly = convert_to_geojson_polygon(geojson.get("geojson", geojson))
    return {"Stocks de carbone": compute_carbon_stocks(poly)}


@app.post("/pollution")
def pollution_indicator(survey: dict):
    data = survey.get("survey", survey)
    return {"Pollution": compute_pollution(data)}


@app.post("/conservation")
def conservation_indicator(geojson: dict, influence_distance: float = 0):
    if "influence_area" in geojson:
        influence_distance = parse_influence_distance(geojson["influence_area"], 0.0)
    elif "influence_distance" in geojson:
        influence_distance = parse_influence_distance(geojson["influence_distance"], 0.0)
    poly = convert_to_geojson_polygon(geojson.get("geojson", geojson))
    return {"Conservation": compute_conservation(poly, influence_distance)}


@app.post("/ecosystem_services")
def ecosystem_services_indicator(geojson: dict, distance_max: float = 1000, milieu: str = "urbain"):
    if "distance_max" in geojson:
        distance_max = geojson["distance_max"]
    if "milieu" in geojson:
        milieu = geojson["milieu"]
    poly = convert_to_geojson_polygon(geojson.get("geojson", geojson))
    return {"Services écosystémiques": compute_ecosystem_services(poly, distance_max, milieu)}


@app.post("/habitat_destruction")
def habitat_destruction_indicator(geojson: dict):
    poly = convert_to_geojson_polygon(geojson.get("geojson", geojson))
    return {"Destruction de l'habitat": compute_habitat_destruction(poly)}


@app.post("/human_footprint")
def human_footprint_indicator(geojson: dict):
    poly = convert_to_geojson_polygon(geojson.get("geojson", geojson))
    return {"Empreinte humaine": compute_human_footprint(poly)}


@app.post("/invasive_exotics")
def invasive_exotics_indicator(geojson: dict, survey: dict, weights: dict = None):
    poly = convert_to_geojson_polygon(geojson.get("geojson", geojson))
    if weights is None:
        weights = {k: 0.0 for k in survey.keys()}
    return {"Espèces exotiques envahissantes": compute_invasive_exotics(poly, survey, weights)}


@app.post("/species_at_risk")
def species_at_risk_indicator(geojson: dict, influence_area: float = 0):
    if "influence_area" in geojson:
        influence_area = parse_influence_distance(geojson["influence_area"], 0.0)
    elif "influence_distance" in geojson:
        influence_area = parse_influence_distance(geojson["influence_distance"], 0.0)
    poly = convert_to_geojson_polygon(geojson.get("geojson", geojson))
    return {"Espèces en péril": compute_species_at_risk(poly, influence_area)}