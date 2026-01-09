from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .client import fetch_trains

app = FastAPI(title="CTA Live Map")

DEFAULT_ROUTES = ["red", "blue", "brn", "g", "org", "pink", "p", "y"]


@app.get("/api/trains")
def get_trains():
    try:
        df = fetch_trains(routes=DEFAULT_ROUTES)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    features = []
    for _, row in df.iterrows():
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "route_number": row["route_number"],
                    "line": row["line"],
                    "dest_name": row["dest_name"],
                    "is_delayed": row["is_delayed"],
                    "is_approaching": row["is_approaching"],
                    "heading": row["heading"],
                    "next_station_name": row["next_station_name"],
                    "expected_arrival_time": row["expected_arrival_time"].isoformat(),
                    "prediction_generation_time": row["prediction_generation_time"].isoformat(),
                },
                "geometry": {"type": "Point", "coordinates": [row["lon"], row["lat"]]},
            }
        )

    return JSONResponse({"type": "FeatureCollection", "features": features})


static_dir = Path(__file__).resolve().parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
