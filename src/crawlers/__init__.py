"""
Burger Crawler - 브랜드별 크롤러 패키지
"""

from .base import BaseCrawler
from .lotteria import LotteriaCrawler
from .burger_king import BurgerKingCrawler
from .nobrand_burger import NoBrandBurgerCrawler
from .kfc import KFCCrawler
from .factory import get_crawler, get_available_brands, register_crawler

__all__ = [
    "BaseCrawler",
    "LotteriaCrawler",
    "BurgerKingCrawler",
    "NoBrandBurgerCrawler",
    "KFCCrawler",
    "get_crawler",
    "get_available_brands",
    "register_crawler",
]
