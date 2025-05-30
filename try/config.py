import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    POLYGON_API_KEY: str = "keDH5lgSUzRw2em9oTcRdD9CHiHKiTaB"
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
    FINNHUB_API_KEY: str = os.getenv("FINNHUB_API_KEY", "demo")
    
    # HTTP Settings
    DEFAULT_RETRY_DELAY: int = 1
    MAX_RETRIES: int = 3
    REQUEST_TIMEOUT: int = 10
    
    # SEC Settings
    SEC_USER_AGENT: str = "StockTerminal/1.0 (contact@example.com)"
    
    class Config:
        env_file = ".env"

settings = Settings()
