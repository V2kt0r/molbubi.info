from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Redis for consuming data
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_STREAM_NAME: str = "bike_data_stream"
    REDIS_CONSUMER_GROUP: str = "processing_group"
    REDIS_CONSUMER_NAME: str = "processor_1"  # In real scaling, this would be dynamic

    # Redis for storing bike state
    REDIS_BIKE_STATE_HASH: str = "bike_states"
    REDIS_STATION_BIKES_SET_PREFIX: str = "station_bikes:"

    # PostgreSQL Connection
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "bikedata"

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
