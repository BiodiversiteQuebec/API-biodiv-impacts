import datetime
import json
import math
import os
import re
from typing import Any, Dict, Tuple, Optional
import geojson
import numpy as np
from starlette.responses import JSONResponse


def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively sanitize objects for RFC 8259 compliant JSON serialization:
    - Replaces NaN and Infinity with None (dumps as null)
    - Converts numpy types to native Python types
    """
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    if isinstance(obj, (float, np.floating)):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return float(obj)
    if isinstance(obj, (int, np.integer)):
        return int(obj)
    if isinstance(obj, np.ndarray):
        return [sanitize_for_json(x) for x in obj.tolist()]
    if isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [sanitize_for_json(v) for v in obj]
    return obj


class NaNJSONResponse(JSONResponse):
    """
    Custom JSONResponse that sanitizes NaN and Infinity into null (None).
    """
    def render(self, content: Any) -> bytes:
        return json.dumps(
            sanitize_for_json(content),
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


def normalize_lng(lng: float) -> float:
    """
    Normalizes longitude into [-180, 180] to handle map wrap from MapLibre scrolling.
    """
    lng_f = float(lng)
    norm = ((lng_f + 180.0) % 360.0) - 180.0
    return 180.0 if (norm == -180.0 and lng_f == 180.0) else norm


def convert_to_geojson_polygon(poly_data: Any) -> geojson.Polygon:
    """
    Extracts and normalizes a GeoJSON Polygon from:
    - FeatureCollection (e.g. from empriseGeospatiale)
    - Feature
    - Polygon dictionary
    """
    if not poly_data:
        raise ValueError("Emprise géospatiale manquante ou vide.")

    if isinstance(poly_data, dict) and "geojson" in poly_data and len(poly_data) == 1:
        poly_data = poly_data["geojson"]

    if isinstance(poly_data, dict) and poly_data.get("type") == "FeatureCollection":
        features = poly_data.get("features", [])
        if not features:
            raise ValueError("FeatureCollection sans features.")
        poly_data = features[0].get("geometry", {})

    if isinstance(poly_data, dict) and poly_data.get("type") == "Feature":
        poly_data = poly_data.get("geometry", {})

    if isinstance(poly_data, dict) and "coordinates" in poly_data:
        coords = poly_data["coordinates"]
    elif isinstance(poly_data, dict) and "points" in poly_data:
        coords = [poly_data["points"]]
    else:
        raise ValueError("Coordonnées de géométrie introuvables.")

    if not coords:
        raise ValueError("Coordonnées vides.")

    # Wrap single ring if needed
    if isinstance(coords, (list, tuple)) and coords and isinstance(coords[0], (list, tuple)):
        if coords[0] and isinstance(coords[0][0], (int, float)):
            coords = [coords]

    norm_coords = []
    for ring in coords:
        norm_ring = [[normalize_lng(pt[0]), float(pt[1])] for pt in ring]
        if norm_ring and norm_ring[0] != norm_ring[-1]:
            norm_ring.append(norm_ring[0])
        if len(norm_ring) < 4:
            raise ValueError("Un anneau de polygone doit comporter au moins 4 points.")
        norm_coords.append(norm_ring)

    return geojson.Polygon(norm_coords)


def parse_influence_distance(val: Optional[str], default: float = 0.0) -> float:
    """
    Parses influence distance in meters from arbitrary text input (e.g. '250', '250 km', '').
    """
    if not val:
        return default
    match = re.search(r"[-+]?\d*\.?\d+", str(val))
    if match:
        try:
            num = float(match.group(0))
            if "km" in str(val).lower():
                num *= 1000.0
            return max(0.0, num)
        except ValueError:
            return default
    return default


def extract_eee_survey(form: Any) -> Tuple[Dict[str, bool], Dict[str, float]]:
    """
    Extracts the 9 industrial activity switches from the form as EEE risk activities.
    """
    survey = {
        "palettes": bool(getattr(form, "switch_palettes", False)),
        "sols_organiques": bool(getattr(form, "switch_sols_organiques", False)),
        "plans_eau": bool(getattr(form, "switch_plans_eau", False)),
        "canalisation": bool(getattr(form, "switch_canalisation", False)),
        "milieux_aquatiques": bool(getattr(form, "switch_milieux_aquatiques", False)),
        "sols_interregional": bool(getattr(form, "switch_sols_interregional", False)),
        "especes_non_indigenes": bool(getattr(form, "switch_especes_non_indigenes", False)),
        "produits_ligneux": bool(getattr(form, "switch_produits_ligneux", False)),
        "transport_maritime": bool(getattr(form, "switch_transport_maritime", False)),
    }
    weights = {k: 0.0 for k in survey}
    return survey, weights


def save_request_log(submission_data: dict):
    """
    Saves raw submission to request_logs/ for auditing.
    """
    try:
        os.makedirs("request_logs", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(f"request_logs/request_{timestamp}.json", "w") as f:
            json.dump(sanitize_for_json(submission_data), f, indent=4)
    except Exception as e:
        print(f"Warning: Failed to save request log: {e}")


def sanitize_indicator_result(ind_name: str, item: Any) -> Any:
    """
    Sanitize and slim down indicator output payloads:
    - carbon_stocks: Remove massive qc_pixel_distribution array.
    - species_at_risk: Limit species_nearest_outside to the 5 closest species.
    """
    if not isinstance(item, dict):
        return item

    inter = item.get("intermediate_values")
    if ind_name == "carbon_stocks":
        if isinstance(inter, dict):
            inter.pop("qc_pixel_distribution", None)
        item.pop("qc_pixel_distribution", None)
    elif ind_name == "species_at_risk":
        if isinstance(inter, dict):
            nearest = inter.get("species_nearest_outside")
            if isinstance(nearest, list):
                sorted_nearest = sorted(
                    nearest,
                    key=lambda x: x.get("distance_m", float("inf")) if isinstance(x, dict) else float("inf")
                )
                inter["species_nearest_outside"] = sorted_nearest[:5]

    return item