import enum
from typing import List, Tuple
from fastapi import FastAPI
from pydantic import BaseModel
import geojson
import json
from typing import List, Literal
from fastapi import Body
from fastapi.responses import StreamingResponse
import matplotlib.pyplot as plt
import io
import numpy as np

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


app = FastAPI()

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
    result = compute_connectivity(geojson)
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
    result = compute_carbon_stocks(geojson)
    return {"Stocks de carbone": result}

@app.post("/pollution")
def pollution_indicator(survey: dict):
    """
    Endpoint to calculate the pollution indicator based on the provided survey data.

    Args:

        survey (dict): A dictionary containing survey data used to compute the pollution indicator.

    Returns:

        dict: A dictionary with the computed pollution indicator.
    """
    result = compute_pollution(survey)
    return {"Pollution": result}

@app.post("/conservation")
def conservation_indicator(geojson: dict, influence_distance: float):
    """
    Endpoint to calculate the conservation indicator for a given geographical area.

    Args:
        
        geojson (dict): A GeoJSON object representing the geographical area.
        
        influence_distance (float): The distance of influence outside of the geojson in meters.

    Returns:

        dict: A dictionary containing the conservation indicator result.
    """
    result = compute_conservation(geojson, influence_distance)
    return {"Conservation": result}

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
    result = compute_habitat_destruction(geojson)
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
    result = compute_human_footprint(geojson)
    return {"Empreinte humaine": result}

@app.post("/invasive_exotics")
def invasive_exotics_indicator(
        geojson: dict = Body(...),
        survey: dict = Body(...)):
    """
    Endpoint to calculate the invasive exotics indicator.

    Args:

        geojson (dict): A GeoJSON object representing the geographical area.

        survey (dict): A dictionary containing survey data used to compute the invasive exotics indicator.

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
    ]
  },
  "survey": {"Q1": false, "Q2": false, "Q3": false, "Q4": false, "Q5": false, "Q6": false, "Q7": false, "Q8": false, "Q9": true, "Q10": true}
}
    """
    result = compute_invasive_exotics(geojson, survey)
    return {"Espèces exotiques envahissantes": result}

@app.post("/species_at_risk")
def species_at_risk_indicator(geojson: dict):
    """
    Endpoint to calculate the species at risk indicator.

    Args:

        geojson (dict): A GeoJSON object representing the geographical area.

    Returns:

        dict: A dictionary containing the calculated species at risk indicator.
    """
    result = compute_species_at_risk(geojson)
    return {"Espèces en péril": result}


plt.rcParams['font.family'] = 'sans-serif'

@app.get("/graph")
def generate_graph():
    # Données de l'exemple
    categories = ["Destruction d'habitat", "Espèces exotiques envahissantes", "Services rendus par la nature", 
                  "Espèces à statut", "Empreinte humaine", "Destruction de puits de carbone",
                  "Connectivité", "Pollution", "Conservation"]
    ## Add a few white spaces to the right of the categories
    categories = [cat + " " * 10 for cat in categories]
    values = [0.29, 1, 0.34, 1, 0.19, 0.03, 0.00, 0.00, 0.00]

    # Trier les catégories et les valeurs en fonction des valeurs
    sorted_pairs = sorted(zip(values, categories), reverse=False)
    sorted_values, sorted_categories = zip(*sorted_pairs)

    # Création du graphique avec Matplotlib
    plt.figure(figsize=(6, 2.5), facecolor='none')
    # plt.hlines(y=sorted_categories, xmin=0, xmax=1, color='gray', alpha=0.7)
    # plt.scatter(sorted_values, sorted_categories, color='black', zorder=8)

    # # Ajouter les valeurs à côté des catégories
    # for value, category in zip(sorted_values, sorted_categories):
    #     plt.text(-0.06, category, f'{value:.2f}', va='center', ha='left', color='black')

    # Utiliser un colormap pour le dégradé de couleur
    cmap = plt.get_cmap("YlOrBr")
    norm = plt.Normalize(0, 1)
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    # Fonction pour dessiner une ligne avec un dégradé
    def draw_gradient_line(y, xmin, xmax):
        for i in range(256):
            plt.plot([xmin + i * (xmax - xmin) / 256, xmin + (i + 1) * (xmax - xmin) / 256], [y, y], color=cmap(gradient[0, i]), alpha=0.7)

    # Dessiner les lignes horizontales avec un dégradé de couleur
    for value, category in zip(sorted_values, sorted_categories):
        draw_gradient_line(category, 0, 1)

    # Ajouter les valeurs à côté des catégories
    for value, category in zip(sorted_values, sorted_categories):
        plt.scatter(value, category, color='black', zorder=8, s=150)
        plt.text(-0.17, category, f'{value:.2f}', va='center', ha='left', color='black')


    # # Lignes de référence (facultatif)
    plt.axvline(0.25, color='grey', linewidth=1, alpha=0.2)
    plt.axvline(0.5, color='grey', linewidth=1, alpha=0.2)
    plt.axvline(0.75, color='grey', linewidth=1, alpha=0.2)
    # plt.axvline(0.5, color='red', linestyle='--', linewidth=1)

    # Retirer la boîte autour de la figure
    plt.box(False)
    plt.xticks([])
    plt.tick_params(left=False)
    plt.tight_layout()#plt.subplots_adjust(left=0.45)

    # Sauvegarde dans un buffer en mémoire
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True)
    buf.seek(0)
    plt.close()

    # Retourner le graphique comme réponse
    return StreamingResponse(buf, media_type="image/png")