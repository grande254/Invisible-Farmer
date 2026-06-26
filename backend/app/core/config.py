import os
from functools import lru_cache
from dotenv import load_dotenv


load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Invisible Farmer Credit Review Agent")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    API_VERSION: str = os.getenv("API_VERSION", "1.0.0")

    NEO4J_URI: str | None = os.getenv("NEO4J_URI")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str | None = os.getenv("NEO4J_PASSWORD")

    FEATHERLESS_API_KEY: str | None = os.getenv("FEATHERLESS_API_KEY")
    FEATHERLESS_BASE_URL: str = os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1")
    FEATHERLESS_MODEL: str | None = os.getenv("FEATHERLESS_MODEL")

    PAYMENT_SERVICE_URL: str | None = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:3001")
    PAYMENT_API_KEY: str | None = os.getenv("PAYMENT_API_KEY")
    SELLER_VKEY: str | None = os.getenv("SELLER_VKEY")
    NETWORK: str = os.getenv("NETWORK", "Preprod")
    AGENT_IDENTIFIER: str | None = os.getenv("AGENT_IDENTIFIER")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
