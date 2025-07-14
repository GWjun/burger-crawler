from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
import re
import os
from datetime import datetime
from loguru import logger

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from fake_useragent import UserAgent

from config import settings


class BaseCrawler(ABC):
    def __init__(self):
        """
        Initialize a new crawler instance with a requests session using a configured user-agent header.
        """
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.user_agent})

    @abstractmethod
    def crawl(self) -> List[Dict[str, Any]]:
        """
        Abstract method to perform brand-specific web crawling.
        
        Returns:
            List of dictionaries containing crawled burger data for a specific brand.
        """
        pass

    def get_selenium_driver(self):
        """
        Configure and return a Selenium Edge WebDriver instance optimized for fast web crawling.
        
        The driver is set up with multiple performance-enhancing options, including disabling images, CSS, plugins, and extensions, and uses a randomized user-agent. The Edge driver executable path is resolved relative to the project directory. The driver is configured with a 10-second page load timeout and a 3-second implicit wait. Raises a FileNotFoundError if the Edge driver executable is missing, and propagates any other exceptions encountered during driver creation.
        
        Returns:
            Edge WebDriver: A configured Selenium Edge WebDriver instance ready for use.
        
        Raises:
            FileNotFoundError: If the Edge driver executable is not found.
            Exception: If driver creation fails for any other reason.
        """
        try:
            ua = UserAgent()
            options = Options()

            # 성능 최적화 옵션 설정
            if settings.headless_mode:
                options.add_argument("--headless")

            # 필수 옵션만 유지하고 성능 최적화
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-images")  # 이미지 로드 비활성화로 속도 향상
            options.add_argument("--disable-css")  # CSS 로드 비활성화
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-logging")
            options.add_argument("--silent")
            options.add_argument("--disable-background-networking")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-client-side-phishing-detection")
            options.add_argument("--disable-default-apps")
            options.add_argument("--disable-hang-monitor")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--disable-prompt-on-repost")
            options.add_argument("--disable-sync")
            options.add_argument("--disable-translate")
            options.add_argument("--disable-windows10-custom-titlebar")
            options.add_argument("--memory-pressure-off")
            options.add_argument("--max_old_space_size=4096")
            options.add_argument(f"--user-agent={ua.random}")

            # 페이지 로딩 전략 설정 (eager: DOM이 준비되면 바로 반환)
            options.page_load_strategy = "eager"

            # 절대 경로로 드라이버 경로 설정
            current_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            driver_path = os.path.join(
                current_dir, "edgedriver_win64", "msedgedriver.exe"
            )

            if not os.path.exists(driver_path):
                raise FileNotFoundError(f"Edge driver not found at: {driver_path}")

            service = Service(executable_path=driver_path)
            driver = webdriver.Edge(service=service, options=options)

            # 타임아웃 설정 최적화
            driver.set_page_load_timeout(10)  # 페이지 로드 타임아웃 10초
            driver.implicitly_wait(3)  # 암시적 대기 3초로 단축

            return driver

        except Exception as e:
            logger.error(f"Failed to create Edge driver: {e}")
            raise

    def clean_text(self, text: str) -> str:
        """
        Sanitize input text by trimming whitespace and replacing newlines and tabs with spaces.
        
        Returns an empty string if the input is falsy.
        """
        if not text:
            return ""
        return text.strip().replace("\n", " ").replace("\t", " ")

    def extract_price(self, price_text: str) -> Optional[int]:
        """
        Extracts an integer price value from a string containing numeric characters.
        
        Parameters:
            price_text (str): The text potentially containing a price.
        
        Returns:
            Optional[int]: The extracted price as an integer, or None if no valid price is found.
        """
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
        """
        Create a standardized dictionary template for burger data with default fields and initial values.
        
        Parameters:
            name (str): The name of the burger.
            brand_name (str): The brand name in the local language.
            brand_name_eng (str): The brand name in English.
        
        Returns:
            Dict[str, Any]: A dictionary containing default fields for burger information, including name, brand details, description placeholders, price, availability, category, URLs, release date, patty type, and nutrition info.
        """
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
