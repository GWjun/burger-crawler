from typing import List, Dict, Any
from loguru import logger

from .base import BaseCrawler
from src.__mock__.dummy_data import get_brand_dummy_data


class NoBrandBurgerCrawler(BaseCrawler):
    def __init__(self):
        """
        Initialize the NoBrandBurgerCrawler with brand-specific configuration.
        
        Sets the base URL, Korean brand name, and English brand identifier for the No Brand Burger crawler.
        """
        super().__init__()
        self.base_url = "https://www.nobrand.co.kr"
        self.brand_name = "노브랜드 버거"
        self.brand_name_eng = "nobrand_burger"

    def crawl(self) -> List[Dict[str, Any]]:
        """
        Retrieve new product data for No Brand Burger by returning placeholder dummy data.
        
        Returns:
            A list of dictionaries, each representing a dummy product entry for No Brand Burger.
        """
        logger.info(f"Starting {self.brand_name} crawling...")

        # TODO: 실제 크롤링 로직 구현
        # 임시로 더미 데이터 반환
        logger.warning("Using dummy data - Replace with actual crawling logic")
        dummy_burgers = get_brand_dummy_data("nobrand_burger", 3)

        logger.info(
            f"Finished {self.brand_name} crawling. Found {len(dummy_burgers)} items"
        )
        return dummy_burgers
