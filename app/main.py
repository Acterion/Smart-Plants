#!/usr/bin/env python3.13
from fastapi import FastAPI, Request, HTTPException, Query, Header, Depends
from fastapi.responses import FileResponse, StreamingResponse
from models import SensorValue, PumpEvent
from database import SessionLocal, init_db
from datetime import datetime, timedelta
from typing import List
import os
import csv
import io
import sqlite3

from sqlalchemy.orm import Session

api = FastAPI()
API_KEY = "vKpsikScqRUt2CdC"

# Create tables if they don't exist
init_db()
DATABASE_PATH = "plants.db"


@api.post("/plants/measurements")
async def receive_sensor_data(request: Request):
    if request.headers.get("x-api-key") != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = await request.json()
    name = data.get("name")
    device_uuid = data.get("device_uuid")
    sensors = data.get("sensors", {})
    timestamp = datetime.now()

    session = SessionLocal()

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

    session = SessionLocal()
    event = PumpEvent(name=name, device_uuid=device_uuid, timestamp=timestamp)
    session.add(event)
    session.commit()
    session.close()

    print(f"[Watering] {name} was watered at {timestamp}")
    return {"status": "ok"}


@api.get("/plants/database")
async def download_database(request: Request):
    if request.headers.get("x-api-key") != "vKpsikScqRUt2CdC":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if os.path.exists(DATABASE_PATH):
        return FileResponse(
            path=DATABASE_PATH,
            media_type="application/octet-stream",
            filename="plants.db"
        )

    raise HTTPException(status_code=404, detail="Database not found")


@api.get("/plants/recent")
async def get_recent_data_csv(
    minutes: int = Query(5, ge=1, le=1440),
    api_key: str = Header(..., alias="x-api-key")
):
    if api_key != "vKpsikScqRUt2CdC":
        raise HTTPException(status_code=401, detail="Unauthorized")

    cutoff = datetime.now() - timedelta(minutes=minutes)

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT id, name, device_uuid, sensor_type, value, unit, timestamp FROM sensor_values "
                  "WHERE timestamp >= ? ORDER BY timestamp DESC", (cutoff,))
        rows = c.fetchall()
        conn.close()

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "name", "device_uuid",
                        "sensor_type", "value", "unit", "timestamp"])
        writer.writerows(rows)
        output.seek(0)

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
