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
    """
    Return an instance of the crawler associated with the specified brand.
    
    Parameters:
        brand (str): The brand name for which to retrieve a crawler instance.
    
    Returns:
        BaseCrawler: An instance of the crawler class registered for the given brand.
    
    Raises:
        ValueError: If the specified brand is not supported.
    """
    if brand in CRAWLERS:
        return CRAWLERS[brand]()
    else:
        raise ValueError(
            f"Unsupported brand: {brand}. Available brands: {list(CRAWLERS.keys())}"
        )


def get_available_brands() -> list[str]:
    """
    Return a list of all brand names currently registered in the crawler factory.
    
    Returns:
        list[str]: List of available brand names.
    """
    return list(CRAWLERS.keys())


def register_crawler(brand: str, crawler_class: Type[BaseCrawler]) -> None:
    """
    Register or update a crawler class for a specific brand.
    
    Adds the given crawler class to the internal registry under the specified brand name, allowing it to be retrieved by brand in future operations.
    """
    CRAWLERS[brand] = crawler_class
