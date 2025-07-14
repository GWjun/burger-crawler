import os
from pydantic_settings import BaseSettings
from typing import Optional


def get_env_file():
    """환경에 따른 .env 파일 경로 반환"""
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        if os.path.exists(".env.production"):
            return ".env.production"
    else:
        if os.path.exists(".env.development"):
            return ".env.development"

    # 기본 .env 파일 사용
    if os.path.exists(".env"):
        return ".env"

    return None


class Settings(BaseSettings):
    # Environment
    environment: str = "development"

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
        case_sensitive = False
        env_file = get_env_file()


def get_settings() -> Settings:
    """설정 인스턴스를 반환하는 팩토리 함수"""
    return Settings()


# 전역 설정 인스턴스
settings = get_settings()
