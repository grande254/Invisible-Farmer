import os
from functools import lru_cache
from dotenv import load_dotenv


load_dotenv()


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


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

    MASUMI_MODE: str = os.getenv("MASUMI_MODE", "local")
    MASUMI_PAYMENT_TYPE: str = os.getenv("MASUMI_PAYMENT_TYPE", "cardano_tx_verified")

    MASUMI_REGISTRY_SERVICE_URL: str = os.getenv("MASUMI_REGISTRY_SERVICE_URL", "http://localhost:3000")
    MASUMI_PAYMENT_SERVICE_URL: str = os.getenv("MASUMI_PAYMENT_SERVICE_URL", "http://localhost:3001")

    MASUMI_AGENT_IDENTIFIER: str = os.getenv(
        "MASUMI_AGENT_IDENTIFIER",
        "local-invisible-farmer-credit-review-agent",
    )
    MASUMI_AGENT_NAME: str = os.getenv(
        "MASUMI_AGENT_NAME",
        "Invisible Farmer Credit Review Agent",
    )
    MASUMI_AGENT_VERSION: str = os.getenv("MASUMI_AGENT_VERSION", "v2")

    MASUMI_SERVICE_PRICE_AMOUNT: float = float(os.getenv("MASUMI_SERVICE_PRICE_AMOUNT", "50"))
    MASUMI_SERVICE_PRICE_CURRENCY: str = os.getenv("MASUMI_SERVICE_PRICE_CURRENCY", "ADA")
    MASUMI_ENFORCE_PAYMENT: bool = env_bool("MASUMI_ENFORCE_PAYMENT", True)

    MASUMI_SELLING_WALLET_ADDRESS: str | None = os.getenv("MASUMI_SELLING_WALLET_ADDRESS")
    MASUMI_PURCHASE_WALLET_ADDRESS: str | None = os.getenv("MASUMI_PURCHASE_WALLET_ADDRESS")

    CARDANO_NETWORK: str = os.getenv("CARDANO_NETWORK", "preprod")
    BLOCKFROST_PROJECT_ID: str | None = os.getenv("BLOCKFROST_PROJECT_ID")
    CARDANO_MIN_CONFIRMATIONS: int = int(os.getenv("CARDANO_MIN_CONFIRMATIONS", "1"))

    PAYMENT_SERVICE_URL: str | None = os.getenv("PAYMENT_SERVICE_URL", MASUMI_PAYMENT_SERVICE_URL)
    PAYMENT_API_KEY: str | None = os.getenv("PAYMENT_API_KEY")
    SELLER_VKEY: str | None = os.getenv("SELLER_VKEY")
    NETWORK: str = os.getenv("NETWORK", "Preprod")
    AGENT_IDENTIFIER: str | None = os.getenv("AGENT_IDENTIFIER", MASUMI_AGENT_IDENTIFIER)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()