from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Payment settings
    PAYME_MERCHANT_ID: str = ""
    PAYME_SECRET_KEY: str = ""
    CLICK_MERCHANT_ID: str = ""
    CLICK_SERVICE_ID: str = ""
    CLICK_SECRET_KEY: str = ""

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
