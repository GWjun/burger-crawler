from typing import List, Dict, Any
from loguru import logger

from .base import BaseCrawler
from src.__mock__.dummy_data import get_brand_dummy_data


class BurgerKingCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.burgerking.co.kr"
        self.brand_name = "버거킹"
        self.brand_name_eng = "burger_king"

    def crawl(self) -> List[Dict[str, Any]]:
        """버거킹 신제품 크롤링"""
        logger.info(f"Starting {self.brand_name} crawling...")

        # TODO: 실제 크롤링 로직 구현
        # 임시로 더미 데이터 반환
        logger.warning("Using dummy data - Replace with actual crawling logic")
        dummy_burgers = get_brand_dummy_data("burger_king", 3)

        logger.info(
            f"Finished {self.brand_name} crawling. Found {len(dummy_burgers)} items"
        )
        return dummy_burgers
