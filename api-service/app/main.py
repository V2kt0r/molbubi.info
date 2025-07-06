from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.exceptions import ResourceNotFound

app = FastAPI(title="BikeShare Data API", openapi_url="/api/v1/openapi.json")


# --- Exception Handler ---
@app.exception_handler(ResourceNotFound)
async def resource_not_found_exception_handler(request: Request, exc: ResourceNotFound):
    return JSONResponse(
        status_code=404,
        content={"message": exc.detail},
    )


app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to the BikeShare Data API"}
