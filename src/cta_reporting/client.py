from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Iterable, List

import pandas as pd
import requests

BASE_URL = "http://lapi.transitchicago.com/api/1.0/ttpositions.aspx"


def read_api_key(key_path: str | Path | None = None) -> str:
    """Read CTA API key from disk."""
    key_file = Path(key_path) if key_path else Path(__file__).resolve().parents[2] / "cta_api_key.txt"
    if not key_file.exists():
        raise FileNotFoundError(f"Missing API key file: {key_file}. Put your CTA API key in it.")

    api_key = key_file.read_text().strip()
    if not api_key:
        raise ValueError(f"API key file is empty: {key_file}")
    return api_key


def ensure_list(value):
    """CTA API sometimes returns a dict instead of a list; normalize to list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def fetch_trains(routes: Iterable[str], api_key: str | None = None, key_path: str | Path | None = None) -> pd.DataFrame:
    """Fetch train positions and return a normalized DataFrame."""
    key_to_use = api_key or read_api_key(key_path)
    route_param = ",".join(routes)

    params = {"rt": route_param, "key": key_to_use, "outputType": "JSON"}
    response = requests.get(BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    payload = response.json()

    routes_payload = ensure_list(payload.get("ctatt", {}).get("route"))
    trains: List[dict] = []

    for route in routes_payload:
        route_name = route.get("@name")
        for train in ensure_list(route.get("train")):
            train_copy = train.copy()
            train_copy["line"] = route_name
            trains.append(train_copy)

    fmt = "%Y-%m-%dT%H:%M:%S"
    rows = []

    for item in trains:
        try:
            prediction_generation_time = dt.datetime.strptime(item["prdt"], fmt)
            expected_arrival_time = dt.datetime.strptime(item["arrT"], fmt)
        except (KeyError, ValueError):
            continue

        rows.append(
            {
                "route_number": str(item.get("rn", "")),
                "dest_st": str(item.get("destSt", "")),
                "dest_name": str(item.get("destNm", "")),
                "train_direction": str(item.get("trDr", "")),
                "next_station_id": str(item.get("nextStaId", "")),
                "next_station_name": str(item.get("nextStaNm", "")),
                "prediction_generation_time": prediction_generation_time,
                "expected_arrival_time": expected_arrival_time,
                "is_approaching": str(item.get("isApp", "")),
                "is_delayed": str(item.get("isDly", "")),
                "flags": str(item.get("flags", "")),
                "lat": float(item.get("lat", 0) or 0),
                "lon": float(item.get("lon", 0) or 0),
                "heading": int(item.get("heading", 0) or 0),
                "line": str(item.get("line", route_name or "")),
            }
        )

    return pd.DataFrame(rows)
