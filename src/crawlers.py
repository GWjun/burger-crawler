from abc import ABC, abstractmethod
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from loguru import logger
import time
from config import settings


class BaseCrawler(ABC):
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.user_agent
        })

    @abstractmethod
    def crawl(self) -> List[Dict[str, Any]]:
        """각 브랜드별 크롤링 구현"""
        pass

    def get_selenium_driver(self):
        """Selenium WebDriver 설정"""
        options = Options()
        if settings.headless_mode:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-agent={self.ua.random}')
        
        driver = webdriver.Chrome(options=options)
        return driver

    def clean_text(self, text: str) -> str:
        """텍스트 정리"""
        if not text:
            return ""
        return text.strip().replace('\n', ' ').replace('\t', ' ')


class McDonaldsCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.mcdonalds.co.kr"
        self.brand = "맥도날드"

    def crawl(self) -> List[Dict[str, Any]]:
        """맥도날드 신제품 크롤링"""
        logger.info(f"Starting {self.brand} crawling...")
        burgers = []
        
        try:
            # 맥도날드 메뉴 페이지 크롤링 로직 구현
            # 실제 구현시 해당 사이트 구조에 맞게 수정 필요
            url = f"{self.base_url}/kr/ko-kr/product/burgers.html"
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 예시 구조 - 실제 사이트에 맞게 수정 필요
            menu_items = soup.select('.menu-item')  # 실제 셀렉터로 변경
            
            for item in menu_items:
                try:
                    name = self.clean_text(item.select_one('.item-name').text)
                    price = self.clean_text(item.select_one('.item-price').text)
                    description = self.clean_text(item.select_one('.item-description').text)
                    image_url = item.select_one('img')['src'] if item.select_one('img') else None
                    
                    burger_data = {
                        'name': name,
                        'brand': self.brand,
                        'price': price,
                        'description': description,
                        'image_url': image_url,
                        'is_new': True,  # 신제품 여부 판단 로직 추가 필요
                        'source_url': url
                    }
                    burgers.append(burger_data)
                    
                except Exception as e:
                    logger.error(f"Error parsing item: {str(e)}")
                    continue
                    
            time.sleep(settings.request_delay)
            
        except Exception as e:
            logger.error(f"Error crawling {self.brand}: {str(e)}")
        
        logger.info(f"Finished {self.brand} crawling. Found {len(burgers)} items")
        return burgers


class BurgerKingCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.burgerking.co.kr"
        self.brand = "버거킹"

    def crawl(self) -> List[Dict[str, Any]]:
        """버거킹 신제품 크롤링"""
        logger.info(f"Starting {self.brand} crawling...")
        burgers = []
        
        try:
            # 버거킹 메뉴 페이지 크롤링 로직 구현
            # 실제 구현시 해당 사이트 구조에 맞게 수정 필요
            pass
            
        except Exception as e:
            logger.error(f"Error crawling {self.brand}: {str(e)}")
        
        logger.info(f"Finished {self.brand} crawling. Found {len(burgers)} items")
        return burgers


class LotteriaCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.lotteria.com"
        self.brand = "롯데리아"

    def crawl(self) -> List[Dict[str, Any]]:
        """롯데리아 신제품 크롤링"""
        logger.info(f"Starting {self.brand} crawling...")
        burgers = []
        
        try:
            # 롯데리아 메뉴 페이지 크롤링 로직 구현
            # 실제 구현시 해당 사이트 구조에 맞게 수정 필요
            pass
            
        except Exception as e:
            logger.error(f"Error crawling {self.brand}: {str(e)}")
        
        logger.info(f"Finished {self.brand} crawling. Found {len(burgers)} items")
        return burgers


# 크롤러 팩토리
CRAWLERS = {
    'mcdonalds': McDonaldsCrawler,
    'burgerking': BurgerKingCrawler,
    'lotteria': LotteriaCrawler,
}


def get_crawler(brand: str) -> BaseCrawler:
    """브랜드별 크롤러 반환"""
    if brand in CRAWLERS:
        return CRAWLERS[brand]()
    else:
        raise ValueError(f"Unsupported brand: {brand}")
