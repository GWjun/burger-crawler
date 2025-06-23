from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from loguru import logger
import time
import re
from datetime import datetime
from config import settings
from src.dummy_data import get_brand_dummy_data

# Selenium imports (현재 더미 데이터 사용 중이므로 주석 처리)
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from fake_useragent import UserAgent


class BaseCrawler(ABC):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.user_agent})

    @abstractmethod
    def crawl(self) -> List[Dict[str, Any]]:
        """각 브랜드별 크롤링 구현"""
        pass

    def get_selenium_driver(self):
        """Selenium WebDriver 설정 (실제 크롤링 시 사용)"""
        # 현재는 더미 데이터를 사용하므로 주석 처리
        # from selenium import webdriver
        # from selenium.webdriver.chrome.options import Options
        # from fake_useragent import UserAgent
        #
        # ua = UserAgent()
        # options = Options()
        # if settings.headless_mode:
        #     options.add_argument('--headless')
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        # options.add_argument(f'--user-agent={ua.random}')
        #
        # driver = webdriver.Chrome(options=options)
        # return driver
        pass

    def clean_text(self, text: str) -> str:
        """텍스트 정리"""
        if not text:
            return ""
        return text.strip().replace("\n", " ").replace("\t", " ")

    def extract_price(self, price_text: str) -> Optional[int]:
        """가격 텍스트에서 숫자 추출"""
        if not price_text:
            return None

        # 숫자만 추출
        price_match = re.search(r"[\d,]+", price_text.replace(",", ""))
        if price_match:
            return int(price_match.group().replace(",", ""))
        return None

    def create_burger_data_template(
        self, name: str, brand_name: str, brand_name_eng: str
    ) -> Dict[str, Any]:
        """기본 버거 데이터 템플릿 생성"""
        return {
            "name": name,
            "brand_name": brand_name,
            "brand_name_eng": brand_name_eng,
            "description": None,
            "description_full": None,
            "image_url": None,
            "price": 0,
            "set_price": None,
            "available": True,
            "category": "버거",
            "shop_url": None,
            "released_at": datetime.now(),
            "patty": "undefined",
            "brand_description": None,
            "brand_logo_url": None,
            "brand_website_url": None,
            "nutrition": None,
        }


class LotteriaCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.lotteria.com"
        self.brand_name = "롯데리아"
        self.brand_name_eng = "lotteria"

    def crawl(self) -> List[Dict[str, Any]]:
        """롯데리아 신제품 크롤링"""
        logger.info(f"Starting {self.brand_name} crawling...")

        # 임시로 더미 데이터 반환 (실제 크롤링 로직 구현 전까지)
        logger.warning("Using dummy data - Replace with actual crawling logic")
        dummy_burgers = get_brand_dummy_data("lotteria", 3)

        logger.info(
            f"Finished {self.brand_name} crawling. Found {len(dummy_burgers)} items"
        )
        return dummy_burgers


class BurgerKingCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.burgerking.co.kr"
        self.brand_name = "버거킹"
        self.brand_name_eng = "burger_king"

    def crawl(self) -> List[Dict[str, Any]]:
        """버거킹 신제품 크롤링"""
        logger.info(f"Starting {self.brand_name} crawling...")

        # 임시로 더미 데이터 반환 (실제 크롤링 로직 구현 전까지)
        logger.warning("Using dummy data - Replace with actual crawling logic")
        dummy_burgers = get_brand_dummy_data("burger_king", 3)

        logger.info(
            f"Finished {self.brand_name} crawling. Found {len(dummy_burgers)} items"
        )
        return dummy_burgers


class NoBrandBurgerCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.nobrand.co.kr"
        self.brand_name = "노브랜드 버거"
        self.brand_name_eng = "nobrand_burger"

    def crawl(self) -> List[Dict[str, Any]]:
        """노브랜드 버거 신제품 크롤링"""
        logger.info(f"Starting {self.brand_name} crawling...")

        # 임시로 더미 데이터 반환 (실제 크롤링 로직 구현 전까지)
        logger.warning("Using dummy data - Replace with actual crawling logic")
        dummy_burgers = get_brand_dummy_data("nobrand_burger", 3)

        logger.info(
            f"Finished {self.brand_name} crawling. Found {len(dummy_burgers)} items"
        )
        return dummy_burgers


class KFCCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.kfc.co.kr"
        self.brand_name = "KFC"
        self.brand_name_eng = "kfc"

    def crawl(self) -> List[Dict[str, Any]]:
        """KFC 신제품 크롤링"""
        logger.info(f"Starting {self.brand_name} crawling...")

        # 임시로 더미 데이터 반환 (실제 크롤링 로직 구현 전까지)
        logger.warning("Using dummy data - Replace with actual crawling logic")
        dummy_burgers = get_brand_dummy_data("kfc", 3)

        logger.info(
            f"Finished {self.brand_name} crawling. Found {len(dummy_burgers)} items"
        )
        return dummy_burgers


# 크롤러 팩토리
CRAWLERS = {
    "lotteria": LotteriaCrawler,
    "burger_king": BurgerKingCrawler,
    "nobrand_burger": NoBrandBurgerCrawler,
    "kfc": KFCCrawler,
}


def get_crawler(brand: str) -> BaseCrawler:
    """브랜드별 크롤러 반환"""
    if brand in CRAWLERS:
        return CRAWLERS[brand]()
    else:
        raise ValueError(
            f"Unsupported brand: {brand}. Available brands: {list(CRAWLERS.keys())}"
        )
