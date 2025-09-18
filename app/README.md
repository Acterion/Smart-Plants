# Smart Plants

A lightweight FastAPI application for managing plant measurements.

This application allows you to:
- Record sensor data from plant monitoring devices
- Track watering events
- Query recent measurements
- Download the database

## API Endpoints

- POST `/plants/measurements` - Record sensor readings
- POST `/plants/pump` - Record watering events
- GET `/plants/database` - Download the entire database
- GET `/plants/recent` - Get recent measurements in CSV format
- GET `/plants/test` - Test the API functionality

## Deployment

This application can be deployed using Docker and Docker Compose:

```bash
docker compose up -d
```

The API will be available at http://localhost:8000
