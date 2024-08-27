from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str
    DATABASE_PASSWORD: str
    DATABASE_USERNAME: str
    DATABASE_NAME: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRES_MINUTES: int
    JWT_ALGORITHM: str

    API_KEY: str

    class Config:
        env_file = '../.env'


settings = Settings()
