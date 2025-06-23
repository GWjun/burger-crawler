from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str

    # Selenium
    headless_mode: bool = True

    # Crawling
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    request_delay: int = 1

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/crawler.log"

    # Schedule
    crawl_interval_hours: int = 6

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
