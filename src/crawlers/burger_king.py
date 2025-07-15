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
        """신제품 데이터 수집 - HTML 구조에 맞춰 수정"""
        try:
            logger.info("Collecting new products from specific categories...")

            # 수집할 카테고리 목록 (HTML에 있는 정확한 이름으로 수정)
            target_categories = [
                "오리지널스&맥시멈",
                "프리미엄",
                # "와퍼&주니어", "치킨&슈림프버거" - HTML에 없어서 제외
            ]

            all_products = []

            # 먼저 .menu_list_wrap이 로드될 때까지 대기
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "menu_list_wrap"))
                )
                logger.info("Menu list container found")
            except TimeoutException:
                logger.warning("Menu list container not found")
                return get_brand_dummy_data("burger_king", 2)

            # 각 카테고리별로 제품 수집
            for category in target_categories:
                logger.info(f"Looking for category: {category}")
                products_in_category = self._collect_products_by_category_v2(
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
                # 실제 제품 데이터 파싱
                parsed_products = self._parse_product_data(all_products)
                return parsed_products
            else:
                logger.warning(
                    "No products found in target categories - using dummy data"
                )
                return get_brand_dummy_data("burger_king", 2)

        except Exception as e:
            logger.error(f"Error collecting products: {str(e)}")
            return get_brand_dummy_data("burger_king", 1)

    def _collect_products_by_category_v2(self, driver, category_name):
        """HTML 구조에 맞춘 카테고리별 제품 수집"""
        try:
            # divide_group 내의 h3.tit01에서 카테고리 찾기
            category_xpath = f"//div[@class='divide_group']//h3[@class='tit01'][contains(text(), '{category_name}')]"

            try:
                category_element = driver.find_element(By.XPATH, category_xpath)
                logger.info(f"Found category element for '{category_name}'")
            except NoSuchElementException:
                logger.warning(f"Category '{category_name}' not found")
                return []

            # 해당 카테고리의 부모 divide_group에서 menu_list 찾기
            try:
                divide_group = category_element.find_element(
                    By.XPATH, "./ancestor::div[@class='divide_group']"
                )
                menu_list = divide_group.find_element(By.CLASS_NAME, "menu_list")

                # menu_list 내의 모든 li 요소들 (각각이 제품)
                product_items = menu_list.find_elements(By.TAG_NAME, "li")

                logger.info(
                    f"Found {len(product_items)} product items in '{category_name}'"
                )
                return product_items

            except NoSuchElementException:
                logger.warning(f"Menu list not found for category '{category_name}'")
                return []

        except Exception as e:
            logger.error(
                f"Error collecting products for category {category_name}: {str(e)}"
            )
            return []

    def _parse_product_data(self, product_elements):
        """제품 요소들을 파싱해서 데이터 추출 - 파생 제품 제외"""
        products = []

        # 제외할 키워드 목록
        exclude_keywords = ["세트", "라지세트", "팩", "콤보", "더블", "라지", "패키지"]

        for product_element in product_elements:
            try:
                # 제품명을 먼저 추출해서 필터링 검사
                try:
                    name_element = product_element.find_element(
                        By.CSS_SELECTOR, ".cont .tit span"
                    )
                    product_name = self.clean_text(name_element.text)
                except:
                    product_name = "Unknown Product"

                # 파생 제품 필터링 - 제외할 키워드가 포함된 제품은 스킵
                if any(keyword in product_name for keyword in exclude_keywords):
                    logger.debug(f"Excluding derived product: {product_name}")
                    continue

                product_data = self.create_burger_data_template(
                    "", self.brand_name, self.brand_name_eng
                )

                # 제품명 설정
                product_data["name"] = product_name

                # 이미지 URL 추출
                try:
                    img_element = product_element.find_element(
                        By.CSS_SELECTOR, ".prd_image img"
                    )
                    product_data["image_url"] = img_element.get_attribute("src")
                except:
                    product_data["image_url"] = None

                # 제품 설명 추출
                try:
                    desc_element = product_element.find_element(
                        By.CSS_SELECTOR, ".set_info span"
                    )
                    product_data["description"] = self.clean_text(desc_element.text)
                except:
                    product_data["description"] = None

                # NEW 플래그 확인
                try:
                    new_flag = product_element.find_element(
                        By.CSS_SELECTOR, ".flag_menu.new_menu"
                    )
                    if new_flag:
                        product_data["dev_comment"] = "신제품"
                except:
                    pass

                # 상세 페이지 링크 추출 (나중에 영양정보용)
                try:
                    detail_btn = product_element.find_element(
                        By.CSS_SELECTOR, ".btn_detail"
                    )
                    # 클릭 이벤트에서 URL 추출하는 로직 필요
                    product_data["shop_url"] = f"{self.base_url}/menu/detail"  # 임시
                except:
                    product_data["shop_url"] = None

                # 기본값 설정
                product_data["price"] = 0  # 가격 정보가 없음
                product_data["available"] = True
                product_data["category"] = "버거"

                products.append(product_data)
                logger.info(f"Parsed product: {product_data['name']}")

            except Exception as e:
                logger.error(f"Error parsing product element: {str(e)}")
                continue

        logger.info(f"Filtered out derived products. Final count: {len(products)}")
        return products
