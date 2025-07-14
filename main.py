import sys
import os
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 환경 변수 로드
load_dotenv()

from src.scheduler import CrawlerScheduler
from src.crawlers import get_crawler, get_available_brands
from src.database import SupabaseManager
from src.__mock__.dummy_data import create_dummy_burger_data, get_brand_dummy_data
from config import settings


# 로거 설정
def setup_logger():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger.remove()  # 기본 핸들러 제거
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    logger.add(
        settings.log_file,
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
    )


def test_crawler(brand: str):
    """특정 브랜드 크롤러 테스트"""
    try:
        crawler = get_crawler(brand)
        data = crawler.crawl()
        logger.info(f"Test crawl for {brand} completed. Found {len(data)} items")
        for item in data[:3]:  # 처음 3개 항목만 출력
            logger.info(f"Sample item: {item}")
    except Exception as e:
        logger.error(f"Test crawl failed for {brand}: {str(e)}")


def test_database():
    """데이터베이스 연결 테스트"""
    try:
        db = SupabaseManager()

        # 테스트용 더미 데이터
        test_data = {
            "name": "Test Burger",
            "brand_name": "Test Brand",
            "brand_name_eng": "test_brand",
            "description": "Test Description",
            "description_full": "Full Test Description",
            "image_url": "https://example.com/image.jpg",
            "price": 5000,
            "set_price": 7000,
            "available": True,
            "category": "버거",
            "shop_url": "https://example.com/shop",
            "brand_website_url": "https://example.com",
            "nutrition": {
                "calories": 500,
                "fat": 25.5,
                "protein": 20.0,
                "sugar": 5.5,
                "sodium": 800,
            },
        }

        # 테스트 데이터 삽입
        success = db.insert_complete_burger_data(test_data)
        if success:
            logger.info("Database test successful - Complete burger data inserted")

            # 최신 제품 조회 테스트
            latest_products = db.get_latest_products(limit=5)
            logger.info(f"Found {len(latest_products)} latest products")

        else:
            logger.error("Database test failed")

    except Exception as e:
        logger.error(f"Database test error: {str(e)}")


def test_dummy_data():
    """더미 데이터로 DB 테스트"""
    try:
        db = SupabaseManager()

        # 더미 데이터 생성
        dummy_burgers = create_dummy_burger_data()
        logger.info(f"Generated {len(dummy_burgers)} dummy burger data")

        # 데이터 삽입
        success = db.insert_bulk_burger_data(dummy_burgers)
        if success:
            logger.info("Dummy data insertion successful")

            # 결과 확인
            latest = db.get_latest_products(limit=10)
            logger.info(f"Latest {len(latest)} products in database")
            for product in latest[:3]:  # 처음 3개만 출력
                logger.info(
                    f"- {product.get('name')} ({product.get('brand_name')}) - {product.get('price')}원"
                )
        else:
            logger.error("Dummy data insertion failed")

    except Exception as e:
        logger.error(f"Dummy data test error: {str(e)}")


def run_single_crawler(brand: str):
    """특정 브랜드 크롤러 한 번 실행 (데이터베이스 저장)"""
    try:
        logger.info(f"Starting single crawl for {brand}")

        # 크롤러 생성 및 실행
        crawler = get_crawler(brand)
        data = crawler.crawl()

        if not data:
            logger.warning(f"No data found for {brand}")
            return

        logger.info(f"Crawled {len(data)} items for {brand}")

        # 데이터베이스에 저장
        db = SupabaseManager()
        success = db.insert_bulk_burger_data(data)

        if success:
            logger.info(f"Successfully saved {len(data)} items for {brand} to database")
        else:
            logger.error(f"Failed to save data for {brand} to database")

    except Exception as e:
        logger.error(f"Single crawl failed for {brand}: {str(e)}")


def main():
    """메인 함수"""
    setup_logger()
    logger.info("Burger Crawler Started")

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "test-db":
            test_database()
        elif command == "test-crawler":
            if len(sys.argv) > 2:
                brand = sys.argv[2]
                test_crawler(brand)
            else:
                logger.info("Available brands: " + ", ".join(get_available_brands()))
        elif command == "crawl":
            if len(sys.argv) > 2:
                brand = sys.argv[2]
                run_single_crawler(brand)
            else:
                logger.error("Please specify a brand")
                logger.info("Available brands: " + ", ".join(get_available_brands()))
        elif command == "test-dummy":
            test_dummy_data()
        elif command == "run-once":
            scheduler = CrawlerScheduler()
            scheduler.run_all_crawlers()
        elif command == "scheduler":
            scheduler = CrawlerScheduler()
            scheduler.start_scheduler()
        elif command == "test-dummy":
            test_dummy_data()
        else:
            logger.error(f"Unknown command: {command}")
            print_usage()
    else:
        # 기본적으로 스케줄러 실행
        scheduler = CrawlerScheduler()
        scheduler.start_scheduler()


def print_usage():
    """사용법 출력"""
    print(
        """
Usage: python main.py [command]

Commands:
  scheduler       - Start the scheduler (default)
  run-once        - Run all crawlers once
  crawl <brand>   - Run single brand crawler once and save to DB
  test-db         - Test database connection
  test-dummy      - Test with dummy data
  test-crawler <brand>  - Test specific crawler (no DB save)
  
Available brands: """
        + ", ".join(get_available_brands())
    )


if __name__ == "__main__":
    main()
