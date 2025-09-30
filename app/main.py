#!/usr/bin/env python3.13
from fastapi import FastAPI, Request, HTTPException, Query, Header, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from app.models import SensorValue, PumpEvent
from app.database import get_db, init_db
from datetime import datetime, timedelta
from typing import List
import os
import csv
import io

from sqlalchemy.orm import Session

api = FastAPI()
# Get API_KEY from environment variable or use default as fallback
API_KEY = os.environ.get("API_KEY")

# Create tables if they don't exist
init_db()
# Get database file path from environment variable or use default


async def not_implemented():
    return {"message": "This endpoint is not yet implemented or deprecated."}


@api.post("/plants/measurements")
async def receive_sensor_data(request: Request):
    if request.headers.get("x-api-key") != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = await request.json()
    name = data.get("name")
    device_uuid = data.get("device_uuid")
    sensors = data.get("sensors", {})
    timestamp = datetime.now()

    session = get_db()

    for sensor_type, entry in sensors.items():
        sensor = SensorValue(
            name=name,
            device_uuid=device_uuid,
            timestamp=timestamp,
            sensor_type=sensor_type,
            value=entry.get("value"),
            unit=entry.get("unit")
        )
        session.add(sensor)

    session.commit()
    session.close()

    print(f"[Stored] {name} at {timestamp} → {sensors}")
    return {"status": "ok"}


@api.post("/plants/pump")
async def receive_watering(request: Request):
    if request.headers.get("x-api-key") != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    data = await request.json()

    name = data.get("name")
    device_uuid = data.get("device_uuid")
    timestamp = datetime.now()

    session = get_db()
    event = PumpEvent(name=name, device_uuid=device_uuid, timestamp=timestamp)
    session.add(event)
    session.commit()
    session.close()

    print(f"[Watering] {name} was watered at {timestamp}")
    return {"status": "ok"}


@api.get("/plants/recent")
async def get_recent_data_csv(
    minutes: int = Query(5, ge=1, le=1440),
    api_key: str = Header(..., alias="x-api-key")
):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    cutoff = datetime.now() - timedelta(minutes=minutes)

    try:
        session = get_db()
        try:
            # Query sensor values using SQLAlchemy ORM
            sensor_values = session.query(SensorValue).filter(
                SensorValue.timestamp >= cutoff
            ).order_by(SensorValue.timestamp.desc()).all()

            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["id", "name", "device_uuid",
                             "sensor_type", "value", "unit", "timestamp"])

            for sensor in sensor_values:
                writer.writerow([
                    sensor.id, sensor.name, sensor.device_uuid,
                    sensor.sensor_type, sensor.value, sensor.unit, sensor.timestamp
                ])

            output.seek(0)
        finally:
            session.close()

        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=recent_data.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")


@api.get("/plants/test")
async def test_endpoint(request: Request):
    if request.headers.get("x-api-key") != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"message": "API is working!", "value": 42}


@api.get("/plants")
async def hello():
    return {"message": "Welcome to the Smart Plants API"}


@api.get("/dash")
async def dashboard():
    # return static html page from index.html
    with open("index.html") as f:
        html_content = f.read()
    if not html_content:
        return {"message": "Error loading dashboard"}
    return HTMLResponse(content=html_content)
