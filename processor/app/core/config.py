from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    # Redis for consuming data
    REDIS_HOST: str
    REDIS_DOCKER_PORT: int
    REDIS_STREAM_NAME: str
    REDIS_CONSUMER_GROUP: str
    REDIS_CONSUMER_NAME: str

    # Redis for storing bike state
    REDIS_BIKE_STATE_HASH: str
    REDIS_STATION_BIKES_SET_PREFIX: str

    # PostgreSQL Connection
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
