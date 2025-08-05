import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.shared.exceptions import ResourceNotFound

app = FastAPI(title="molbubi.info", openapi_url="/api/v1/openapi.json", version=settings.VERSION)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    This middleware calculates the total time taken to process a request
    and adds it to the response headers.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# --- Exception Handler ---
@app.exception_handler(ResourceNotFound)
async def resource_not_found_exception_handler(request: Request, exc: ResourceNotFound):
    return JSONResponse(
        status_code=404,
        content={"message": exc.detail},
    )


app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "molbubi.info API is running"}
