# API Testing Guide

This document explains how to run the comprehensive test suite for the molbubi.info API service.

## Test Suite Overview

The API service includes a comprehensive test suite with:
- **210+ test cases** across 16 test files
- **Near 100% code coverage** (95% target)
- **Unit tests** for repositories, services, and core components
- **Integration tests** for API endpoints
- **Edge case testing** for error handling and validation
- **Mock-based testing** for external dependencies

## Test Structure

```
api/tests/
├── conftest.py                    # Test configuration and fixtures
├── test_shared_repository.py      # Base repository tests
├── test_*_repository.py          # Repository layer tests (bikes, stations, distribution)
├── test_*_service.py             # Service layer tests (business logic)
├── test_endpoints_*.py           # API endpoint integration tests
├── test_shared_*.py              # Shared components (exceptions, database, schemas)
├── test_core_config.py           # Configuration management tests
└── test_main.py                  # FastAPI application tests
```

## Running Tests

### Method 1: Using Poetry (Recommended for Development)

```bash
# Navigate to API directory
cd api/

# Install dependencies (if not already installed)
poetry install

# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=app --cov-report=html --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_bikes_service.py -v

# Run specific test method
poetry run pytest tests/test_bikes_service.py::TestBikeService::test_get_bike_history_empty -v
```

### Method 2: Using Docker (Production-like Environment)

```bash
# From project root directory
cd /path/to/molbubi.info

# Run all tests in Docker
docker compose run --rm \
  -v ./api/tests:/code/tests \
  api bash -c "pip install pytest pytest-asyncio pytest-cov httpx pytest-mock fakeredis && pytest tests/ -v"

# Run tests with coverage in Docker
docker compose run --rm \
  -v ./api/tests:/code/tests \
  api bash -c "pip install pytest pytest-asyncio pytest-cov httpx pytest-mock fakeredis && pytest tests/ --cov=app --cov-report=term-missing -v"

# Run specific test files in Docker
docker compose run --rm \
  -v ./api/tests:/code/tests \
  api bash -c "pip install pytest pytest-asyncio pytest-cov httpx pytest-mock fakeredis && pytest tests/test_shared_exceptions.py tests/test_main.py -v"
```

### Method 3: GitHub Actions Workflow

Use the manual test workflow for CI/CD testing:

1. Go to the repository's Actions tab
2. Select "Manual Tests" workflow  
3. Click "Run workflow"
4. Choose:
   - **Service**: `api` or `all`
   - **Coverage**: `true` for coverage reports
   - **Test method**: `poetry` or `docker`
   - **Upload artifacts**: `true` to save test results

## Test Configuration

### Environment Variables

Tests use these environment variables (automatically set in CI):

```bash
DATABASE_URL=sqlite:///test.db     # Test database (SQLite for speed)
REDIS_URL=redis://localhost:6379/0 # Redis connection for tests
VERSION=test                       # Application version
```

### Coverage Settings

Coverage is configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = ["-v", "--cov=app", "--cov-report=html", "--cov-report=term-missing", "--cov-fail-under=95"]

[tool.coverage.run]
source = ["app"]
omit = ["tests/*", "*/__init__.py"]
```

## Test Categories

### 1. Repository Tests
- **Files**: `test_*_repository.py`
- **Coverage**: Database queries, pagination, filtering
- **Mocking**: SQLAlchemy sessions and query objects
- **Focus**: Data access patterns, SQL query logic

### 2. Service Tests  
- **Files**: `test_*_service.py`
- **Coverage**: Business logic, data transformation, error handling
- **Mocking**: Repository dependencies
- **Focus**: Service layer functionality, exception handling

### 3. API Endpoint Tests
- **Files**: `test_endpoints_*.py`  
- **Coverage**: HTTP request/response, validation, routing
- **Mocking**: Service layer dependencies
- **Focus**: API contract, error responses, edge cases

### 4. Core Component Tests
- **Files**: `test_shared_*.py`, `test_core_*.py`, `test_main.py`
- **Coverage**: Configuration, database connections, custom exceptions
- **Focus**: Infrastructure components, FastAPI app setup

## Test Fixtures and Mocking

### Key Fixtures (conftest.py)
- `client`: FastAPI TestClient for endpoint testing
- `test_db`: In-memory SQLite database for tests
- `mock_*_service`: Mock service objects for isolation
- `mock_redis`: Fake Redis client for testing

### Mocking Strategy
- **Unit tests**: Mock external dependencies (database, Redis)
- **Integration tests**: Use real FastAPI TestClient with mocked services
- **Repository tests**: Mock SQLAlchemy session and query objects
- **Service tests**: Mock repository dependencies

## Edge Cases Covered

- ✅ Invalid input validation (malformed dates, negative IDs)
- ✅ Resource not found scenarios (bikes, stations)
- ✅ Pagination edge cases (zero limits, large offsets)
- ✅ Database connection failures
- ✅ Empty result sets and null values
- ✅ URL encoding and special characters
- ✅ HTTP method validation
- ✅ Content type validation
- ✅ Large request handling

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the `api/` directory
2. **Database Errors**: Tests use SQLite by default; check environment variables
3. **Mock Failures**: Repository tests may fail if SQLAlchemy mocking is incorrect
4. **Coverage Issues**: Some complex SQL operations may not be fully testable with mocks

### Known Limitations

- Complex repository methods with SQLAlchemy operations may have mock-related test failures
- Coverage may be slightly lower for SQL-heavy repository methods
- Docker tests require volume mounting for test files

### Debugging Tips

```bash
# Run tests with verbose output and stop on first failure
poetry run pytest -v -x

# Run tests with print statements visible
poetry run pytest -s

# Run specific failing test with full traceback
poetry run pytest tests/test_file.py::TestClass::test_method -vvv

# Generate and view HTML coverage report
poetry run pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## Continuous Integration

The test suite is integrated into GitHub Actions:

- **Automatic**: Tests run on every push/PR (if configured)
- **Manual**: Use "Manual Tests" workflow for on-demand testing  
- **Coverage**: Reports uploaded as artifacts
- **Multi-method**: Supports both Poetry and Docker testing
- **Service isolation**: Can test API independently or with all services

## Performance

- **Speed**: ~3-5 seconds for full test suite (210+ tests)
- **Parallelization**: Tests run sequentially but are optimized with mocks
- **Memory**: Uses in-memory SQLite database for speed
- **Caching**: GitHub Actions uses Poetry/dependency caching

## Contributing

When adding new features:

1. **Write tests first** (TDD approach recommended)
2. **Maintain coverage** above 95%
3. **Include edge cases** for error handling
4. **Update this documentation** if adding new test patterns
5. **Use existing fixtures** and mocking patterns for consistency

For questions or issues with the test suite, check the existing test files for patterns and examples.