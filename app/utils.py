import datetime
import json
import math
import os
import time
from functools import wraps
from typing import Any, Dict, List, Tuple
import geojson
import numpy as np
from starlette.responses import JSONResponse


def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively sanitize objects for RFC 8259 compliant JSON serialization:
    - Replaces NaN and Infinity with None (which dumps as null)
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
    Custom JSONResponse that sanitizes NaN and Infinity into null (None),
    preventing 500 ValueError during serialization.
    """
    def render(self, content: Any) -> bytes:
        return json.dumps(
            sanitize_for_json(content),
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")



def timing_decorator(func):
    """
    Measures the execution time of a function.

    Args:
        func (function): Function to be timed.

    Returns:
        tuple: Function result and elapsed time.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        return result, elapsed_time
    return wrapper

@timing_decorator
def compute_indicateur1():
    return 42

def generate_response(indicators: List[Tuple[str, float]]) -> dict:
    return {f"indicator_{i+1}": {"value": value, "elapsed_time": elapsed_time} for i, (value, elapsed_time) in enumerate(indicators)}

def save_request_data_as_json(poly, eee_qstr, pollution_qstr):
    # Get current date and time
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Create a directory to save the files if it doesn't exist
    if not os.path.exists('request_logs'):
        os.makedirs('request_logs')

    # Define the file name
    file_name = f'request_logs/request_{timestamp}.json'

    def serialize_qstr(data):
        if isinstance(data, dict):
            return data
        if isinstance(data, list):
            return [item.to_dict() if hasattr(item, 'to_dict') else item for item in data]
        return str(data)

    poly_geom = poly.__geo_interface__ if hasattr(poly, '__geo_interface__') else poly

    # Create a dictionary with the data
    data = {
        "date_time": now.isoformat(),
        "poly": poly_geom,
        "eee_qstr": serialize_qstr(eee_qstr),
        "pollution_qstr": serialize_qstr(pollution_qstr)
    }

    # Write data to the file as JSON
    with open(file_name, 'w') as file:
        json.dump(sanitize_for_json(data), file, indent=4)

def convert_to_geojson_polygon(poly_data):
    if isinstance(poly_data, dict):
        if "coordinates" in poly_data:
            return geojson.Polygon(poly_data["coordinates"])
        if "points" in poly_data:
            points = list(poly_data["points"])
        else:
            raise ValueError("Polygon dict must contain 'coordinates' or 'points'")
    else:
        points = list(poly_data.points)
    
    # Ensure the polygon is closed (first and last points are the same)
    if points and points[0] != points[-1]:
        points.append(points[0])
    
    # Create the GeoJSON Polygon
    polygon = geojson.Polygon([points])
    
    return polygon

def to_flat_dict(raw_qstr):
    if isinstance(raw_qstr, dict):
        return raw_qstr
    polutions_qstrs = []
    for poluant in raw_qstr:
        if hasattr(poluant, 'name'):
            polutions_qstrs.append({poluant.name: getattr(poluant, 'answer', None)})
        elif isinstance(poluant, dict):
            name = poluant.get("name", poluant.get("id", ""))
            polutions_qstrs.append({name: poluant.get("answer")})
    result = {list(d.keys())[0]: list(d.values())[0] for d in polutions_qstrs if d} 
    return result

def to_eee_survey(raw_eee) -> tuple:
    survey = {}
    if isinstance(raw_eee, dict):
        for k, v in raw_eee.items():
            if isinstance(v, dict):
                ans = v.get("answer", False)
            else:
                ans = v
            if isinstance(ans, str):
                ans = ans.lower() in ("true", "1", "yes", "oui")
            survey[str(k)] = bool(ans)
        weights = {k: 0.0 for k in survey.keys()}
        return survey, weights
    survey = {}
    if isinstance(raw_eee, list):
        for item in raw_eee:
            if isinstance(item, dict):
                key = str(item.get("no_qstr", item.get("name", "")))
                ans = item.get("answer", False)
            else:
                key = str(getattr(item, "no_qstr", getattr(item, "name", "")))
                ans = getattr(item, "answer", False)
            if isinstance(ans, str):
                ans = ans.lower() in ("true", "1", "yes", "oui")
            key_name = f"Q{key}" if key.isdigit() else key
            if key_name:
                survey[key_name] = bool(ans)
    weights = {k: 0.0 for k in survey.keys()}
    return survey, weights