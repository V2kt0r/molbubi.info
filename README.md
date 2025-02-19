# Bike Tracking System Deployment Guide

## Prerequisites
1. Docker installed ([Installation Guide](https://docs.docker.com/get-docker/))
2. Environment variables set in `.env` file

## Deployment Steps

### 1. Clone Repository
```
git clone https://github.com/V2kt0r/BubiData.git
cd BubiData
```

### 2. Create Environment File
Create a `.env` file in the project root with these variables:
```
POSTGRES_DB = "bubi-data"
POSTGRES_USER = "admin"
POSTGRES_PASSWORD = "strongpassword"

PGADMIN_EMAIL = "admin@example.com"
PGADMIN_PASSWORD = "pgadminpass"

API_URL = "https://maps.nextbike.net/maps/nextbike-live.json?city=699&domains=bh"  # Don't change this
```

### 3. Build and Start Services
`docker compose up -d --build`


## Maintenance Commands
### Stop Services
`docker compose down`

### View Logs
`docker compose logs -f`

## Service Access Points

After successful deployment, you can access the system components at the following locations:

### 1. API Endpoints
**Base URL**: `http://localhost`  
The REST API provides the following main endpoints:
- `GET /api/history/{bike_number}` - Get specific bike's station history
- `GET /api/distance` - List all bike distances
- `GET /api/distance/{bike_number}` - Get specific bike's distance
- `GET /docs` - Interactive API documentation

### 2. Interactive API Documentation
**Access URL**: `http://localhost/docs`  
This automatically generated OpenAPI documentation provides:
- Live API endpoint testing
- Request/response schema visualization
- Example values for all parameters
- Direct integration with Swagger UI

### 3. pgAdmin Database Management
**Access URL**: `http://localhost:5050`  
PostgreSQL administration interface with:
- Database connection management
- SQL query editor
- Table visualization
- User permissions control

**Login Credentials**:
```
Email: ${PGADMIN_EMAIL} from your .env file
Password: ${PGADMIN_PASSWORD} from your .env file
```

### 4. Alternative Documentation Format
**ReDoc Interface**: `http://localhost/redoc`  
Alternative API documentation presentation featuring:
- Clean, readable format
- Detailed schema descriptions
- Response type documentation

## Access Summary Table

| Service                | URL                                  | Authentication          |
|------------------------|--------------------------------------|-------------------------|
| API Endpoints          | `http://localhost`                   | None required           |
| OpenAPI Documentation  | `http://localhost/docs`              | None required           |
| pgAdmin Interface      | `http://localhost:5050`              | .env credentials        |
| ReDoc Documentation    | `http://localhost/redoc`             | None required           |
