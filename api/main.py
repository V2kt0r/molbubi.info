import os

from fastapi import FastAPI

from .endpoints import router
from .middleware.process_time import add_process_time_header

version = os.getenv("VERSION", "v0.1.0")

app = FastAPI(title="BubiData", version=version)

app.middleware("http")(add_process_time_header)

app.include_router(router)
