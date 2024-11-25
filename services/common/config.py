# noinspection PyProtectedMember
from pydantic import BaseSettings


class ServiceSettings(BaseSettings):
    service_name: str
    database_url: str
    redis_url: str
    log_level: str = "INFO"
    environment: str = "development"

    class Config:
        env_file = ".env"
