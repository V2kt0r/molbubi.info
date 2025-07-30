from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    model_config = SettingsConfigDict(env_file='.env')

    API_URL: str
    POLLING_INTERVAL_SECONDS: int

    REDIS_HOST: str
    REDIS_DOCKER_PORT: int
    REDIS_STREAM_NAME: str


settings = Settings()
