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
from src.crawlers import get_crawler, CRAWLERS
from src.database import SupabaseManager
from config import settings

# 로거 설정
def setup_logger():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.remove()  # 기본 핸들러 제거
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    logger.add(
        settings.log_file,
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days"
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
        test_data = {
            'name': 'Test Burger',
            'brand': 'Test Brand',
            'price': '5000원',
            'description': 'Test Description',
            'image_url': 'https://example.com/image.jpg',
            'is_new': True,
            'source_url': 'https://example.com'
        }
        
        # 테스트 데이터 삽입
        success = db.insert_burger_data(test_data)
        if success:
            logger.info("Database test successful")
        else:
            logger.error("Database test failed")
            
    except Exception as e:
        logger.error(f"Database test error: {str(e)}")


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
                logger.info("Available brands: " + ", ".join(CRAWLERS.keys()))
        elif command == "run-once":
            scheduler = CrawlerScheduler()
            scheduler.run_all_crawlers()
        elif command == "scheduler":
            scheduler = CrawlerScheduler()
            scheduler.start_scheduler()
        else:
            logger.error(f"Unknown command: {command}")
            print_usage()
    else:
        # 기본적으로 스케줄러 실행
        scheduler = CrawlerScheduler()
        scheduler.start_scheduler()


def print_usage():
    """사용법 출력"""
    print("""
Usage: python main.py [command]

Commands:
  scheduler     - Start the scheduler (default)
  run-once      - Run all crawlers once
  test-db       - Test database connection
  test-crawler <brand>  - Test specific crawler
  
Available brands: """ + ", ".join(CRAWLERS.keys()))


if __name__ == "__main__":
    main()
