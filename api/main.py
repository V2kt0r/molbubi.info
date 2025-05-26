import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from shared.database import engine, wait_for_db

from .endpoints import router
from .middleware.process_time import add_process_time_header


@asynccontextmanager
async def lifespan(app: FastAPI):
    await wait_for_db()
    yield
    await engine.dispose()


version = os.getenv("VERSION", "v0.1.0")

app = FastAPI(title="BubiData", version=version, lifespan=lifespan)

app.middleware("http")(add_process_time_header)

app.include_router(router)
