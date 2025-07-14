import schedule
import time
from datetime import datetime
from loguru import logger
from src.crawlers import get_crawler, get_available_brands
from src.database import SupabaseManager
from config import settings


class CrawlerScheduler:
    def __init__(self):
        self.db_manager = SupabaseManager()
        logger.info("Crawler Scheduler initialized")

    def run_single_crawler(self, brand: str, auto_confirm: bool = False):
        """단일 브랜드 크롤링 실행"""
        try:
            logger.info(f"Starting crawl for {brand}")
            crawler = get_crawler(brand)
            burger_data = crawler.crawl()

            if burger_data:
                # 중복 체크 후 신제품 필터링
                new_items = []
                for item in burger_data:
                    if not self.db_manager.check_duplicate_product(
                        item["name"], item["brand_name"]
                    ):
                        new_items.append(item)

                if new_items:
                    # 신제품 정보 출력
                    logger.info(f"\n{'='*50}")
                    logger.info(f"발견된 신제품: {len(new_items)}개 ({brand})")
                    logger.info(f"{'='*50}")

                    for i, item in enumerate(new_items, 1):
                        logger.info(f"\n[{i}] {item['name']}")
                        logger.info(f"    가격: {item.get('price', 'N/A')}원")
                        logger.info(f"    설명: {item.get('description', 'N/A')}")
                        if item.get("image_url"):
                            logger.info(f"    이미지: {item['image_url']}")

                    logger.info(f"\n{'='*50}")

                    # 사용자 확인 (auto_confirm이 False인 경우에만)
                    if not auto_confirm:
                        while True:
                            user_input = (
                                input(
                                    f"\n이 {len(new_items)}개의 신제품을 데이터베이스에 추가하시겠습니까? (y/n): "
                                )
                                .strip()
                                .lower()
                            )
                            if user_input in ["y", "yes", "네", "ㅇ"]:
                                break
                            elif user_input in ["n", "no", "아니오", "ㄴ"]:
                                logger.info("사용자가 추가를 취소했습니다.")
                                return
                            else:
                                print("y(예) 또는 n(아니오)로 답해주세요.")

                    # 데이터베이스에 저장
                    success = self.db_manager.insert_bulk_burger_data(new_items)
                    if success:
                        logger.info(
                            f"Successfully saved {len(new_items)} new items for {brand}"
                        )
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

        for brand in get_available_brands():
            self.run_single_crawler(brand, auto_confirm=True)  # 자동 확인으로 실행
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
