from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str
    DATABASE_PASSWORD: str
    DATABASE_USERNAME: str
    DATABASE_NAME: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRES_MINUTES: int
    JWT_ALGORITHM: str

    class Config:
        env_file = '../.env'


settings = Settings()
