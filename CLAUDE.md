# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is molbubi.info, a bike tracking system that monitors shared bike movements and calculates travel distances using real-world GPS data from a public API. The system consists of three main services in a microservices architecture:

- **Collector**: Polls the NextBike API and stores data in Redis
- **Processor**: Consumes data from Redis and processes it into PostgreSQL/TimescaleDB
- **API**: FastAPI service providing REST endpoints for bike data

## Architecture

The system follows a distributed architecture with clear separation of concerns:

```
NextBike API → Collector → Redis → Processor → TimescaleDB
                                                    ↑
                                              API Service
```

### Key Components

1. **Data Collection Layer** (`collector/`):
   - Fetches live bike data from NextBike API
   - Stores raw data in Redis streams for processing
   - Runs continuously with configurable polling intervals

2. **Data Processing Layer** (`processor/`):
   - Consumes messages from Redis streams
   - Processes and transforms bike location data
   - Stores processed data in TimescaleDB (PostgreSQL extension for time-series)

3. **API Layer** (`api/`):
   - FastAPI application with automatic OpenAPI documentation
   - Provides REST endpoints for bike history and distance calculations
   - Uses SQLAlchemy ORM with async support

4. **Database**:
   - TimescaleDB (PostgreSQL) for time-series bike data storage
   - Redis for message queuing and temporary data storage

## Development Commands

### Environment Setup
```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with appropriate values

# Build and start all services
docker compose up -d --build

# Stop all services
docker compose down

# View logs for all services
docker compose logs -f

# View logs for specific service
docker compose logs -f api
docker compose logs -f collector
docker compose logs -f processor
```

### Service Management
```bash
# Check service status
./status.sh

# Restart specific service
docker compose restart api

# Rebuild specific service
docker compose up -d --build api
```

### API Development (api/)
```bash
# Install dependencies with Poetry
cd api/
poetry install

# Run API locally (development)
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Export dependencies
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### Collector Development (collector/)
```bash
# Install dependencies with Poetry
cd collector/
poetry install

# Run collector locally
poetry run python -m app.main
```

### Processor Development (processor/)
```bash
# Install dependencies with Poetry
cd processor/
poetry install

# Run processor locally
poetry run python -m app.main
```

### Migrations Development (migrations/)
```bash
# Install dependencies with Poetry
cd migrations/
poetry install

# Run migrations locally
poetry run python run_migrations.py

# Create new migration
poetry run alembic revision --autogenerate -m "description"

# Check migration status
poetry run alembic current
poetry run alembic history
```

## Key Configuration

### Environment Variables (.env)
- `POSTGRES_*`: Database connection settings
- `PGADMIN_*`: pgAdmin interface credentials
- `API_URL`: NextBike API endpoint (should not be changed)
- `REDIS_*`: Redis connection settings
- `API_DOCKER_PORT`: Port for API service (default: 80)
- `PGADMIN_DOCKER_PORT`: Port for pgAdmin (default: 5050)
- `REDIS_INSIGHT_DOCKER_PORT`: Port for Redis Insight (default: 8001)

### Service Access Points
- API: `http://localhost` (or configured port)
- API Documentation: `http://localhost/docs`
- pgAdmin: `http://localhost:5050`
- Redis Insight: `http://localhost:8001`

## Code Organization

### API Service Structure (`api/app/`)
- `main.py`: FastAPI application setup and middleware
- `api/v1/`: API routes and endpoints
- `core/`: Configuration and exceptions
- `db/`: Database models and repository pattern
- `schemas/`: Pydantic models for request/response validation
- `services/`: Business logic layer

### Database Models
- Uses SQLAlchemy with declarative base
- TimescaleDB hypertables for time-series data
- Repository pattern for data access abstraction

### Key Patterns
- Dependency injection through FastAPI's dependency system
- Pydantic for data validation and serialization
- Async/await throughout the API layer
- Repository pattern for database operations
- Configuration management through pydantic-settings

## Testing

No formal test suite is currently implemented. When adding tests:
- Use pytest for Python testing
- Consider testing each service independently
- Mock external API calls (NextBike API)
- Test database operations with test database

## Development Notes

- The system uses Poetry for dependency management in the API service
- Other services use pip with requirements.txt
- All services are containerized with Docker
- The database uses TimescaleDB for efficient time-series data storage
- Redis is used as a message queue between collector and processor
- Configuration is environment-based for different deployment contexts