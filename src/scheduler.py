import schedule
import time
from datetime import datetime
from loguru import logger
from src.crawlers import get_crawler, CRAWLERS
from src.database import SupabaseManager
from config import settings


class CrawlerScheduler:
    def __init__(self):
        self.db_manager = SupabaseManager()
        logger.info("Crawler Scheduler initialized")

    def run_single_crawler(self, brand: str):
        """단일 브랜드 크롤링 실행"""
        try:
            logger.info(f"Starting crawl for {brand}")
            crawler = get_crawler(brand)
            burger_data = crawler.crawl()
            
            if burger_data:
                # 중복 체크 후 삽입
                new_items = []
                for item in burger_data:
                    if not self.db_manager.check_duplicate(item['name'], item['brand']):
                        new_items.append(item)
                
                if new_items:
                    success = self.db_manager.insert_bulk_burger_data(new_items)
                    if success:
                        logger.info(f"Successfully saved {len(new_items)} new items for {brand}")
                    else:
                        logger.error(f"Failed to save data for {brand}")
                else:
                    logger.info(f"No new items found for {brand}")
            else:
                logger.warning(f"No data crawled for {brand}")
                
        except Exception as e:
            logger.error(f"Error in crawling {brand}: {str(e)}")

    def run_all_crawlers(self):
        """모든 브랜드 크롤링 실행"""
        logger.info("Starting crawl for all brands")
        start_time = datetime.now()
        
        for brand in CRAWLERS.keys():
            self.run_single_crawler(brand)
            time.sleep(settings.request_delay)  # 요청 간 지연
        
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"Completed crawl for all brands in {duration}")

    def start_scheduler(self):
        """스케줄러 시작"""
        # 매 N시간마다 실행
        schedule.every(settings.crawl_interval_hours).hours.do(self.run_all_crawlers)
        
        # 매일 오전 9시에 실행
        schedule.every().day.at("09:00").do(self.run_all_crawlers)
        
        # 매일 오후 6시에 실행
        schedule.every().day.at("18:00").do(self.run_all_crawlers)
        
        logger.info("Scheduler started. Running crawlers...")
        
        # 처음 시작할 때 한 번 실행
        self.run_all_crawlers()
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 스케줄 체크


if __name__ == "__main__":
    scheduler = CrawlerScheduler()
    scheduler.start_scheduler()
