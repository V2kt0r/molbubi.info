from fastapi import FastAPI

from .endpoints import router
from .middleware.process_time import add_process_time_header

app = FastAPI()

app.middleware("http")(add_process_time_header)

app.include_router(router)
