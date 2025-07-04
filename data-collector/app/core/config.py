import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    NEXTBIKE_API_URL: str = (
        "https://maps.nextbike.net/maps/nextbike-live.json?city=699&domains=bh"
    )
    POLLING_INTERVAL_SECONDS: int = 10

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_STREAM_NAME: str = "bike_data_stream"

    # In a real-world scenario, you might use `os.getenv` or a .env file
    # For simplicity, we define them here. To use a .env file, add:
    # class Config:
    #     env_file = ".env"


settings = Settings()
