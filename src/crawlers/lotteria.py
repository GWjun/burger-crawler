from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from loguru import logger
import time
import re
import json

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .base import BaseCrawler


class LotteriaCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.lotteeatz.com"
        self.brand_name = "롯데리아"
        self.brand_name_eng = "lotteria"

    def crawl(self) -> List[Dict[str, Any]]:
        """롯데리아 신제품 크롤링 (최적화된 버전)"""
        logger.info(f"Starting {self.brand_name} crawling...")
        burgers = []
        driver = None

        menu_url = f"{self.base_url}/brand/ria"

        try:
            response = self.session.get(menu_url)
            response.raise_for_status()
            html_content = response.text

            # pList 데이터를 정규식으로 추출
            match = re.search(r"var pList = (.*?);", html_content, re.DOTALL)
            if match:
                json_str = match.group(1)
                product_list = json.loads(json_str)

                # 버거 제품들만 필터링
                burger_items = [
                    item
                    for item in product_list
                    if item.get("displayCategoryNm") == "버거"
                ]
                logger.info(f"Found {len(burger_items)} burger items to process")

                # 드라이버 한 번만 생성
                if burger_items:
                    driver = self.get_selenium_driver()
                    logger.info(
                        "Created single driver instance for all nutrition crawling"
                    )

                for i, item in enumerate(burger_items):
                    logger.info(
                        f"Processing burger {i+1}/{len(burger_items)}: {item.get('presPrdNm')}"
                    )

                    burger_data = self.create_burger_data_template(
                        name=item.get("presPrdNm"),
                        brand_name=self.brand_name,
                        brand_name_eng=self.brand_name_eng,
                    )
                    burger_data["price"] = self.extract_price(
                        str(item.get("sellPrice"))
                    )
                    burger_data["image_url"] = (
                        f"https://img.lotteeatz.com{item.get('imgPath')}{item.get('imgSystemFileNm')}.{item.get('imgExtsn')}"
                    )
                    burger_data["description"] = item.get("dispNm")
                    burger_data["shop_url"] = (
                        f"{self.base_url}/products/introductions/{item.get('presPrdId')}"
                    )

                    # 영양 정보 크롤링 (기존 드라이버 재사용)
                    if driver:
                        nutrition_info = self._get_nutrition_info_with_driver(
                            driver, burger_data["shop_url"]
                        )
                        if nutrition_info:
                            burger_data["nutrition"] = nutrition_info

                    burgers.append(burger_data)
            else:
                logger.warning("Could not find pList data in the HTML.")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error during crawling {self.brand_name}: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from pList: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        finally:
            # 드라이버 정리
            if driver:
                try:
                    driver.quit()
                    logger.info("Driver closed successfully")
                except:
                    pass

        logger.info(f"Finished {self.brand_name} crawling. Found {len(burgers)} items")
        return burgers

    def _get_nutrition_info_with_driver(
        self, driver, product_url: str
    ) -> Optional[Dict[str, Any]]:
        """기존 드라이버를 재사용하여 영양 정보 크롤링 (성능 최적화)"""
        logger.info(f"Crawling nutrition info for: {product_url}")
        try:
            driver.get(product_url)

            # 영양 정보 테이블이 로드될 때까지 대기 (타임아웃 단축)
            try:
                WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "table.tbl-row-info")
                    )
                )
            except:
                logger.warning(f"Nutrition table not found for: {product_url}")
                return None

            soup = BeautifulSoup(driver.page_source, "html.parser")
            nutrition_table = soup.select_one("table.tbl-row-info")

            nutrition_data = {}
            if nutrition_table:
                rows = nutrition_table.find_all("tr")

                for row in rows:
                    th = row.find("th")
                    td = row.find("td")

                    if th and td:
                        key = th.get_text(strip=True)
                        value = td.get_text(strip=True)

                        if "열량" in key:
                            nutrition_data["calories"] = self._parse_nutrition_value(
                                value
                            )
                        elif "포화지방" in key:
                            nutrition_data["fat"] = self._parse_nutrition_value(value)
                        elif "단백질" in key:
                            nutrition_data["protein"] = self._parse_nutrition_value(
                                value
                            )
                        elif "당류" in key:
                            nutrition_data["sugar"] = self._parse_nutrition_value(value)
                        elif "나트륨" in key:
                            nutrition_data["sodium"] = self._parse_nutrition_value(
                                value
                            )

                logger.debug(f"Parsed nutrition data: {nutrition_data}")

            return nutrition_data if nutrition_data else None

        except Exception as e:
            logger.error(f"Error crawling nutrition info from {product_url}: {e}")
            return None

    def _get_nutrition_info(self, product_url: str) -> Optional[Dict[str, Any]]:
        """개별 제품 상세 페이지에서 영양 정보 크롤링 (단일 사용용)"""
        logger.info(f"Crawling nutrition info for: {product_url}")
        driver = None
        try:
            driver = self.get_selenium_driver()
            driver.get(product_url)

            # 페이지 로드 대기 시간 단축
            time.sleep(2)  # 5초 -> 2초로 단축

            # 영양 정보 테이블이 로드될 때까지 대기 (타임아웃 단축)
            try:
                WebDriverWait(driver, 8).until(  # 15초 -> 8초로 단축
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "table.tbl-row-info")
                    )
                )
                logger.info("Found nutrition table with correct selector")
            except:
                logger.warning(f"Nutrition table not found for: {product_url}")
                return None

            soup = BeautifulSoup(driver.page_source, "html.parser")
            nutrition_table = soup.select_one("table.tbl-row-info")

            nutrition_data = {}
            if nutrition_table:
                logger.info("Found nutrition table, parsing data...")
                rows = nutrition_table.find_all("tr")

                for row in rows:
                    # 각 행에서 th와 td 요소 찾기
                    th = row.find("th")
                    td = row.find("td")

                    if th and td:
                        key = th.get_text(strip=True)
                        value = td.get_text(strip=True)

                        if "열량" in key:
                            nutrition_data["calories"] = self._parse_nutrition_value(
                                value
                            )
                        elif "포화지방" in key:
                            nutrition_data["fat"] = self._parse_nutrition_value(value)
                        elif "단백질" in key:
                            nutrition_data["protein"] = self._parse_nutrition_value(
                                value
                            )
                        elif "당류" in key:
                            nutrition_data["sugar"] = self._parse_nutrition_value(value)
                        elif "나트륨" in key:
                            nutrition_data["sodium"] = self._parse_nutrition_value(
                                value
                            )

                logger.info(f"Parsed nutrition data: {nutrition_data}")
            else:
                logger.warning("No nutrition table found in page")

            return nutrition_data if nutrition_data else None

        except Exception as e:
            logger.error(f"Error crawling nutrition info from {product_url}: {e}")
            import traceback

            logger.error(f"Full traceback: {traceback.format_exc()}")
            return None
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    def _parse_nutrition_value(self, text: str) -> Optional[float]:
        """영양 정보 텍스트에서 숫자(float) 추출"""
        match = re.search(r"([\d.]+)", text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None
