from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from loguru import logger
import time
import re
import json
from datetime import datetime
from config import settings
from src.__mock__.dummy_data import get_brand_dummy_data

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent


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
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from fake_useragent import UserAgent

        ua = UserAgent()
        options = Options()
        if settings.headless_mode:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--user-agent={ua.random}")

        service = Service(executable_path="edgedriver_win64/msedgedriver.exe")
        driver = webdriver.Edge(service=service, options=options)
        return driver

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
        self.base_url = "https://www.lotteeatz.com"
        self.brand_name = "롯데리아"
        self.brand_name_eng = "lotteria"

    def crawl(self) -> List[Dict[str, Any]]:
        """롯데리아 신제품 크롤링"""
        logger.info(f"Starting {self.brand_name} crawling...")
        burgers = []

        menu_url = f"{self.base_url}/brand/ria"

        try:
            response = self.session.get(menu_url)
            response.raise_for_status()
            html_content = response.text

            # pList 데이터를 정규식으로 추출
            match = re.search(r"var pList = (.*?);", html_content, re.DOTALL)
            if match:
                json_str = match.group(1)
                product_list = json.loads(json_str)

                for item in product_list:
                    if item.get("displayCategoryNm") == "버거":
                        burger_data = self.create_burger_data_template(
                            name=item.get("presPrdNm"),
                            brand_name=self.brand_name,
                            brand_name_eng=self.brand_name_eng,
                        )
                        burger_data["price"] = self.extract_price(
                            str(item.get("sellPrice"))
                        )
                        burger_data["image_url"] = (
                            f"https://img.lotteeatz.com{item.get('imgPath')}{item.get('imgSystemFileNm')}.{item.get('imgExtsn')}"
                        )
                        burger_data["description"] = item.get("dispNm")
                        burger_data["shop_url"] = (
                            f"{self.base_url}/products/introductions/{item.get('presPrdId')}"
                        )
                        # 영양 정보 크롤링
                        nutrition_info = self._get_nutrition_info(
                            burger_data["shop_url"]
                        )
                        if nutrition_info:
                            burger_data["nutrition"] = nutrition_info
                        burgers.append(burger_data)
            else:
                logger.warning("Could not find pList data in the HTML.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error during crawling {self.brand_name}: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from pList: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

        logger.info(f"Finished {self.brand_name} crawling. Found {len(burgers)} items")
        return burgers

    def _get_nutrition_info(self, product_url: str) -> Optional[Dict[str, Any]]:
        """개별 제품 상세 페이지에서 영양 정보 크롤링"""
        logger.info(f"Crawling nutrition info for: {product_url}")
        driver = None
        try:
            driver = self.get_selenium_driver()
            driver.get(product_url)

            # 영양 정보 테이블이 로드될 때까지 대기
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.tbl_ty01"))
            )

            soup = BeautifulSoup(driver.page_source, "html.parser")
            nutrition_table = soup.select_one("table.tbl_ty01")

            nutrition_data = {}
            if nutrition_table:
                rows = nutrition_table.find_all("tr")
                for row in rows:
                    th = row.find("th")
                    td = row.find("td")
                    if th and td:
                        key = th.get_text(strip=True)
                        value = td.get_text(strip=True)

                        if "열량" in key:
                            nutrition_data["calories"] = self._parse_nutrition_value(
                                value
                            )
                        elif "지방" in key:
                            nutrition_data["fat"] = self._parse_nutrition_value(value)
                        elif "단백질" in key:
                            nutrition_data["protein"] = self._parse_nutrition_value(
                                value
                            )
                        elif "당류" in key:
                            nutrition_data["sugar"] = self._parse_nutrition_value(value)
                        elif "나트륨" in key:
                            nutrition_data["sodium"] = self._parse_nutrition_value(
                                value
                            )
            return nutrition_data
        except Exception as e:
            logger.error(f"Error crawling nutrition info from {product_url}: {e}")
            return None
        finally:
            if driver:
                driver.quit()

    def _parse_nutrition_value(self, text: str) -> Optional[float]:
        """영양 정보 텍스트에서 숫자(float) 추출"""
        match = re.search(r"([\d.]+)", text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None


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
    # "burger_king": BurgerKingCrawler,
    # "nobrand_burger": NoBrandBurgerCrawler,
    # "kfc": KFCCrawler,
}


def get_crawler(brand: str) -> BaseCrawler:
    """브랜드별 크롤러 반환"""
    if brand in CRAWLERS:
        return CRAWLERS[brand]()
    else:
        raise ValueError(
            f"Unsupported brand: {brand}. Available brands: {list(CRAWLERS.keys())}"
        )
