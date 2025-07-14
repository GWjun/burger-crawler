"""
크롤러 팩토리 - 브랜드별 크롤러 인스턴스 생성
"""

from typing import Dict, Type

from .base import BaseCrawler
from .lotteria import LotteriaCrawler
from .burger_king import BurgerKingCrawler
from .nobrand_burger import NoBrandBurgerCrawler
from .kfc import KFCCrawler


# 크롤러 매핑
CRAWLERS: Dict[str, Type[BaseCrawler]] = {
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


def get_available_brands() -> list[str]:
    """사용 가능한 브랜드 목록 반환"""
    return list(CRAWLERS.keys())


def register_crawler(brand: str, crawler_class: Type[BaseCrawler]) -> None:
    """새로운 크롤러 등록"""
    CRAWLERS[brand] = crawler_class
