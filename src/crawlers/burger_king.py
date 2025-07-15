from typing import List, Dict, Any
import time
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base import BaseCrawler
from src.__mock__.dummy_data import get_brand_dummy_data


class BurgerKingCrawler(BaseCrawler):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.burgerking.co.kr"
        self.menu_url = "https://www.burgerking.co.kr/menu/main"
        self.brand_name = "버거킹"
        self.brand_name_eng = "burger_king"

    def crawl(self) -> List[Dict[str, Any]]:
        """버거킹 신제품 크롤링"""
        logger.info(f"Starting {self.brand_name} crawling...")

        try:
            # 브라우저 드라이버 시작
            driver = self.get_selenium_driver()

            # 메뉴 페이지로 이동
            logger.info(f"Navigating to {self.menu_url}")
            driver.get(self.menu_url)

            # 페이지 로딩 대기 (시간 단축)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # 키워드 버튼 클릭하여 모달 열기
            self._open_keyword_modal(driver)

            # #신제품 태그 클릭 및 적용
            self._apply_new_product_filter(driver)

            # 신제품 데이터 수집
            products = self._collect_new_products(driver)

            logger.info(
                f"Finished {self.brand_name} crawling. Found {len(products)} items"
            )
            return products

        except Exception as e:
            logger.error(f"Error during {self.brand_name} crawling: {str(e)}")
            # 에러 발생 시 더미 데이터 반환
            logger.warning("Using dummy data due to error")
            return get_brand_dummy_data("burger_king", 3)

        finally:
            if "driver" in locals():
                driver.quit()

    def _open_keyword_modal(self, driver):
        """키워드 버튼을 클릭하여 모달창 열기"""
        try:
            logger.info("Looking for keyword button...")

            # 가장 빠른 방법: 바로 찾기 시도
            keyword_button = None

            # 1차 시도: 키워드 텍스트가 있는 버튼 바로 찾기
            try:
                keyword_button = driver.find_element(
                    By.XPATH, "//button[contains(text(), '키워드')]"
                )
                if keyword_button.is_enabled() and keyword_button.is_displayed():
                    logger.info("Keyword button found immediately")
            except:
                pass

            # 2차 시도: 짧은 대기 후 다시 찾기
            if not keyword_button:
                try:
                    keyword_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[contains(text(), '키워드')]")
                        )
                    )
                except TimeoutException:
                    # 3차 시도: 다른 셀렉터들 빠르게 시도
                    fast_selectors = [
                        "//button[contains(@class, 'filter')]",
                        "//button[contains(@class, 'keyword')]",
                    ]

                    for selector in fast_selectors:
                        try:
                            keyword_button = driver.find_element(By.XPATH, selector)
                            if (
                                keyword_button.is_enabled()
                                and keyword_button.is_displayed()
                            ):
                                break
                        except:
                            continue

            # 4차 시도: 모든 버튼에서 빠르게 검색
            if not keyword_button:
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    button_text = button.text.strip().lower()
                    if (
                        "키워드" in button_text
                        or "filter" in button.get_attribute("class").lower()
                    ):
                        keyword_button = button
                        break

            if keyword_button:
                logger.info("Clicking keyword button...")
                driver.execute_script("arguments[0].click();", keyword_button)
                time.sleep(0.8)  # 모달 로딩 대기 시간 단축
                logger.info("Keyword modal opened successfully")
            else:
                raise NoSuchElementException("Keyword button not found")

        except Exception as e:
            logger.error(f"Failed to open keyword modal: {str(e)}")
            raise

    def _apply_new_product_filter(self, driver):
        """#신제품 태그 클릭 및 적용"""
        try:
            logger.info("Looking for #신제품 tag...")

            # 가장 일반적인 셀렉터부터 빠르게 시도
            new_product_tag = None

            # 1차 시도: 가장 빠른 XPath로 신제품 텍스트 찾기
            try:
                new_product_tag = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//*[contains(text(), '신제품')]")
                    )
                )
            except TimeoutException:
                # 2차 시도: 좀 더 구체적인 셀렉터들
                fast_selectors = [
                    "//button[contains(text(), '신제품')]",
                    "//span[contains(text(), '신제품')]",
                    "//*[contains(text(), '#신제품')]",
                ]

                for selector in fast_selectors:
                    try:
                        new_product_tag = driver.find_element(By.XPATH, selector)
                        if (
                            new_product_tag.is_enabled()
                            and new_product_tag.is_displayed()
                        ):
                            break
                    except:
                        continue

            if new_product_tag:
                logger.info("Clicking #신제품 tag...")
                driver.execute_script("arguments[0].click();", new_product_tag)

                # 적용 버튼을 바로 찾아서 클릭 (대기 시간 최소화)
                self._click_apply_button_fast(driver)

                logger.info("New product filter applied successfully")
            else:
                raise NoSuchElementException("#신제품 tag not found")

        except Exception as e:
            logger.error(f"Failed to apply new product filter: {str(e)}")
            raise

    def _click_apply_button_fast(self, driver):
        """적용 버튼을 빠르게 찾아서 클릭"""
        try:
            logger.info("Looking for apply button...")

            # 가장 빠른 방법: 바로 찾기 시도
            apply_button = None

            # 1차 시도: 적용 텍스트가 있는 버튼 바로 찾기
            try:
                apply_button = driver.find_element(
                    By.XPATH, "//button[contains(text(), '적용')]"
                )
                if apply_button.is_enabled() and apply_button.is_displayed():
                    logger.info("Apply button found immediately")
            except:
                pass

            # 2차 시도: 짧은 대기 후 다시 찾기
            if not apply_button:
                try:
                    apply_button = WebDriverWait(driver, 1).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[contains(text(), '적용')]")
                        )
                    )
                except TimeoutException:
                    # 3차 시도: 모든 버튼에서 빠르게 검색
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    for button in buttons:
                        if "적용" in button.text.strip() and button.is_displayed():
                            apply_button = button
                            break

            if apply_button:
                logger.info("Clicking apply button...")
                driver.execute_script("arguments[0].click();", apply_button)

                # 필터 적용 완료까지 최소 대기
                time.sleep(1.5)
                logger.info("Apply button clicked successfully")
            else:
                logger.warning(
                    "Apply button not found, checking if filter was applied automatically..."
                )
                time.sleep(1)  # 자동 적용 대기

        except Exception as e:
            logger.warning(f"Could not click apply button: {str(e)}")
            time.sleep(1)  # 안전을 위한 최소 대기

    def _click_apply_button(self, driver):
        """적용 버튼 클릭 (기존 메서드 - 호환성 유지)"""
        self._click_apply_button_fast(driver)

    def _collect_new_products(self, driver):
        """신제품 데이터 수집 - 특정 카테고리만"""
        try:
            logger.info("Collecting new products from specific categories...")

            # 수집할 카테고리 목록
            target_categories = [
                "오리지널스&맥시멈",
                "프리미엄",
                "와퍼&주니어",
                "치킨&슈림프버거",
            ]

            all_products = []

            for category in target_categories:
                logger.info(f"Looking for category: {category}")
                products_in_category = self._collect_products_by_category(
                    driver, category
                )
                if products_in_category:
                    logger.info(
                        f"Found {len(products_in_category)} products in {category}"
                    )
                    all_products.extend(products_in_category)
                else:
                    logger.info(f"No products found in {category}")

            if all_products:
                logger.info(f"Total products found: {len(all_products)}")
                # TODO: 실제 제품 데이터 파싱 로직 구현
                logger.warning("Product parsing not implemented yet - using dummy data")
                return get_brand_dummy_data("burger_king", len(all_products))
            else:
                logger.warning(
                    "No products found in target categories - using dummy data"
                )
                return get_brand_dummy_data("burger_king", 2)

        except Exception as e:
            logger.error(f"Error collecting products: {str(e)}")
            return get_brand_dummy_data("burger_king", 1)

    def _collect_products_by_category(self, driver, category_name):
        """특정 카테고리의 제품들 수집"""
        try:
            # h3 태그에서 카테고리명 찾기
            category_selectors = [
                f"//h3[contains(text(), '{category_name}')]",
                f"//h3[contains(normalize-space(text()), '{category_name}')]",
                f"//*[self::h3 or self::h2 or self::h4][contains(text(), '{category_name}')]",
            ]

            category_element = None
            for selector in category_selectors:
                try:
                    category_elements = driver.find_elements(By.XPATH, selector)
                    if category_elements:
                        # 정확히 일치하는 카테고리 찾기
                        for elem in category_elements:
                            if category_name in elem.text.strip():
                                category_element = elem
                                break
                        if category_element:
                            break
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {str(e)}")
                    continue

            if not category_element:
                logger.warning(f"Category '{category_name}' not found")
                return []

            logger.info(f"Found category element for '{category_name}'")

            # 카테고리 하위의 제품들 찾기
            products = self._find_products_under_category(driver, category_element)

            return products

        except Exception as e:
            logger.error(
                f"Error collecting products for category {category_name}: {str(e)}"
            )
            return []

    def _find_products_under_category(self, driver, category_element):
        """카테고리 요소 하위의 제품들 찾기"""
        try:
            # 카테고리 요소의 부모 또는 다음 형제 요소에서 제품들 찾기
            product_containers = []

            # 방법 1: 카테고리의 부모 요소에서 제품 찾기
            try:
                parent = category_element.find_element(By.XPATH, "./..")
                products_in_parent = parent.find_elements(
                    By.XPATH,
                    ".//*[contains(@class, 'menu') or contains(@class, 'product') or contains(@class, 'item')]",
                )
                if products_in_parent:
                    product_containers.extend(products_in_parent)
            except:
                pass

            # 방법 2: 카테고리 다음의 형제 요소들에서 제품 찾기
            try:
                # 다음 h3까지의 모든 요소들 중에서 제품 찾기
                following_elements = driver.find_elements(
                    By.XPATH,
                    f"//h3[contains(text(), '{category_element.text}')]/following-sibling::*[following-sibling::h3 or position()=last()]",
                )

                for elem in following_elements:
                    # 제품으로 보이는 요소들 찾기
                    products_in_elem = elem.find_elements(
                        By.XPATH,
                        ".//*[contains(@class, 'menu') or contains(@class, 'product') or contains(@class, 'item')]",
                    )
                    product_containers.extend(products_in_elem)

            except Exception as e:
                logger.debug(f"Error finding following elements: {str(e)}")

            # 방법 3: 카테고리 요소 다음에 오는 div들에서 제품 찾기
            try:
                next_divs = driver.find_elements(
                    By.XPATH,
                    f"//h3[contains(text(), '{category_element.text}')]/following-sibling::div",
                )

                for div in next_divs[:5]:  # 처음 몇 개의 div만 확인
                    products_in_div = div.find_elements(
                        By.XPATH,
                        ".//*[contains(@class, 'menu') or contains(@class, 'product') or contains(@class, 'item')]",
                    )
                    if products_in_div:
                        product_containers.extend(products_in_div)

            except Exception as e:
                logger.debug(f"Error finding next divs: {str(e)}")

            # 중복 제거
            unique_products = []
            seen_elements = set()

            for product in product_containers:
                try:
                    # 요소의 위치를 기준으로 중복 체크
                    location = (product.location["x"], product.location["y"])
                    if location not in seen_elements and product.is_displayed():
                        unique_products.append(product)
                        seen_elements.add(location)
                except:
                    continue

            logger.info(f"Found {len(unique_products)} unique products under category")
            return unique_products

        except Exception as e:
            logger.error(f"Error finding products under category: {str(e)}")
            return []
