from typing import List, Dict, Any
import time
import re
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

            # 각 제품의 영양정보 수집
            products_with_nutrition = self._collect_nutrition_info(driver, products)

            logger.info(
                f"Finished {self.brand_name} crawling. Found {len(products_with_nutrition)} items"
            )
            return products_with_nutrition

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
            # 키워드 버튼 찾기
            keyword_button = None

            # 1차 시도: 키워드 텍스트가 있는 버튼 찾기
            try:
                keyword_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(text(), '키워드')]")
                    )
                )
            except TimeoutException:
                # 2차 시도: 모든 버튼에서 검색
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    button_text = button.text.strip().lower()
                    if "키워드" in button_text:
                        keyword_button = button
                        break

            if keyword_button:
                driver.execute_script("arguments[0].click();", keyword_button)
                time.sleep(0.8)
                logger.info("키워드 모달 열기 완료")
            else:
                raise NoSuchElementException("키워드 버튼을 찾을 수 없습니다")

        except Exception as e:
            logger.error(f"키워드 모달 열기 실패: {str(e)}")
            raise

    def _apply_new_product_filter(self, driver):
        """#신제품 태그 클릭 및 적용"""
        try:
            # #신제품 태그 찾기
            new_product_tag = None

            try:
                new_product_tag = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//*[contains(text(), '신제품')]")
                    )
                )
            except TimeoutException:
                # 다른 셀렉터들 시도
                selectors = [
                    "//button[contains(text(), '신제품')]",
                    "//span[contains(text(), '신제품')]",
                    "//*[contains(text(), '#신제품')]",
                ]

                for selector in selectors:
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
                driver.execute_script("arguments[0].click();", new_product_tag)
                self._click_apply_button_fast(driver)
                logger.info("신제품 필터 적용 완료")
            else:
                raise NoSuchElementException("#신제품 태그를 찾을 수 없습니다")

        except Exception as e:
            logger.error(f"신제품 필터 적용 실패: {str(e)}")
            raise

    def _click_apply_button_fast(self, driver):
        """적용 버튼을 빠르게 찾아서 클릭"""
        try:
            apply_button = None

            # 적용 버튼 찾기
            try:
                apply_button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(text(), '적용')]")
                    )
                )
            except TimeoutException:
                # 모든 버튼에서 검색
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    if "적용" in button.text.strip() and button.is_displayed():
                        apply_button = button
                        break

            if apply_button:
                driver.execute_script("arguments[0].click();", apply_button)
                time.sleep(1.5)
            else:
                time.sleep(1)  # 자동 적용 대기

        except Exception as e:
            logger.warning(f"적용 버튼 클릭 실패: {str(e)}")
            time.sleep(1)

    def _click_apply_button(self, driver):
        """적용 버튼 클릭 (기존 메서드 - 호환성 유지)"""
        self._click_apply_button_fast(driver)

    def _collect_new_products(self, driver):
        """신제품 데이터 수집"""
        try:
            target_categories = ["오리지널스&맥시멈", "프리미엄"]
            all_products = []

            # 메뉴 리스트 대기
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "menu_list_wrap"))
                )
            except TimeoutException:
                logger.warning("메뉴 리스트를 찾을 수 없습니다")
                return get_brand_dummy_data("burger_king", 2)

            # 각 카테고리별로 제품 수집
            for category in target_categories:
                products_in_category = self._collect_products_by_category_v2(
                    driver, category
                )
                if products_in_category:
                    logger.info(f"{category}: {len(products_in_category)}개 제품 발견")
                    all_products.extend(products_in_category)

            if all_products:
                logger.info(f"총 {len(all_products)}개 제품 발견")
                parsed_products = self._parse_product_data_with_urls(
                    driver, all_products
                )
                return parsed_products
            else:
                logger.warning("신제품을 찾을 수 없어 더미 데이터를 사용합니다")
                return get_brand_dummy_data("burger_king", 2)

        except Exception as e:
            logger.error(f"제품 수집 중 오류: {str(e)}")
            return get_brand_dummy_data("burger_king", 1)

    def _collect_products_by_category_v2(self, driver, category_name):
        """카테고리별 제품 수집"""
        try:
            category_xpath = f"//div[@class='divide_group']//h3[@class='tit01'][contains(text(), '{category_name}')]"

            try:
                category_element = driver.find_element(By.XPATH, category_xpath)
            except NoSuchElementException:
                return []

            # 해당 카테고리의 제품 리스트 찾기
            try:
                divide_group = category_element.find_element(
                    By.XPATH, "./ancestor::div[@class='divide_group']"
                )
                menu_list = divide_group.find_element(By.CLASS_NAME, "menu_list")
                product_items = menu_list.find_elements(By.TAG_NAME, "li")
                return product_items

            except NoSuchElementException:
                return []

        except Exception as e:
            logger.error(f"{category_name} 카테고리 수집 실패: {str(e)}")
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

                # description은 상세 페이지에서 추출하므로 기본값 설정
                product_data["description"] = None
                product_data["description_full"] = None

                # dev_comment는 공란으로 설정
                product_data["dev_comment"] = None

                # 상세 페이지 링크는 나중에 별도로 수집
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

    def _parse_product_data_with_urls(self, driver, product_elements):
        """제품 요소들을 파싱하고 URL도 수집"""
        # 먼저 기본 데이터 파싱
        products = self._parse_product_data(product_elements)

        # 각 제품의 URL 수집
        filtered_index = 0
        exclude_keywords = ["세트", "라지세트", "팩", "콤보", "더블", "라지", "패키지"]

        for i, product_element in enumerate(product_elements):
            try:
                # 제품명 추출
                try:
                    name_element = product_element.find_element(
                        By.CSS_SELECTOR, ".cont .tit span"
                    )
                    product_name = self.clean_text(name_element.text)
                except:
                    continue

                # 파생 제품 제외
                if any(keyword in product_name for keyword in exclude_keywords):
                    continue

                # URL 수집
                if filtered_index < len(products):
                    current_product = products[filtered_index]
                    detail_url = self._get_detail_url(driver, product_element)
                    if detail_url:
                        current_product["shop_url"] = detail_url
                        logger.info(f"{current_product['name']} URL 수집 완료")
                    filtered_index += 1

            except Exception as e:
                continue

        return products

    def _get_detail_url(self, driver, product_element):
        """제품 요소에서 상세 페이지 URL 추출"""
        try:
            detail_btn = product_element.find_element(By.CSS_SELECTOR, ".btn_detail")

            # 현재 URL 저장
            current_url = driver.current_url

            # 상세 버튼 클릭
            driver.execute_script("arguments[0].click();", detail_btn)
            time.sleep(2)  # 페이지 로딩 대기

            # 새 URL 확인
            new_url = driver.current_url
            if new_url != current_url and "/menu/detail/" in new_url:
                # 다시 원래 페이지로 돌아가기
                driver.back()
                time.sleep(1)

                # 메뉴 리스트가 다시 로드될 때까지 대기
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "menu_list_wrap"))
                )

                return new_url
            else:
                # 클릭이 작동하지 않은 경우 돌아가기
                if new_url == current_url:
                    return None
                else:
                    driver.back()
                    time.sleep(1)
                    return None

        except Exception as e:
            logger.debug(f"Error getting detail URL: {str(e)}")
            return None

    def _collect_nutrition_info(self, driver, products):
        """각 제품의 영양정보를 수집"""
        logger.info("영양정보 수집 시작...")
        products_with_nutrition = []

        for product in products:
            try:
                if product.get("shop_url") and "/menu/detail/" in product["shop_url"]:
                    result_data = self._get_product_nutrition(
                        driver, product["shop_url"]
                    )

                    if result_data:
                        if (
                            isinstance(result_data, dict)
                            and "nutrition_info" in result_data
                        ):
                            # 영양정보와 설명 정보가 분리된 경우
                            if result_data["nutrition_info"]:
                                product["nutrition"] = result_data["nutrition_info"]
                            if result_data["description_info"]:
                                product.update(result_data["description_info"])
                        else:
                            # 영양정보만 있는 경우
                            product["nutrition"] = result_data

                        logger.info(f"{product['name']} 영양정보 수집 완료")

                    time.sleep(1)
                else:
                    logger.warning(f"{product['name']} 상세 URL 없음")

                products_with_nutrition.append(product)

            except Exception as e:
                logger.error(
                    f"{product.get('name', 'Unknown')} 영양정보 수집 실패: {str(e)}"
                )
                products_with_nutrition.append(product)
                continue

        return products_with_nutrition

    def _get_product_nutrition(self, driver, detail_url):
        """제품 상세 페이지에서 영양정보와 설명 추출"""
        try:
            driver.get(detail_url)

            # 페이지 로딩 대기
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(3)

            # 상세 설명 먼저 추출
            description_data = self._extract_description_from_detail_page(driver)

            # 영양정보 버튼 찾기 및 클릭
            nutrition_button = self._find_nutrition_button(driver)
            if not nutrition_button:
                # 영양정보가 없어도 설명 데이터는 반환
                return (
                    {"description_info": description_data} if description_data else None
                )

            driver.execute_script("arguments[0].click();", nutrition_button)
            time.sleep(5)

            # 모달 대기
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "modalWrap"))
                )
            except:
                return (
                    {"description_info": description_data} if description_data else None
                )

            # 영양정보 추출
            nutrition_data = self._extract_nutrition_from_modal(driver)
            self._close_nutrition_modal(driver)

            # 결과 데이터 구성
            result = {}
            if nutrition_data:
                result["nutrition_info"] = nutrition_data
            if description_data:
                result["description_info"] = description_data

            return result if result else None

        except Exception as e:
            logger.error(f"영양정보 추출 실패 ({detail_url}): {str(e)}")
            return None

    def _find_nutrition_button(self, driver):
        """영양정보 버튼 찾기"""
        try:
            # 여러 셀렉터로 시도
            selectors = [
                "//button[contains(@class, 'btn_info_link')]",
                "//button[contains(text(), '원산지,영양성분,알레르기유발성분')]",
                ".btn_info_link",
            ]

            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        button = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                    else:
                        button = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )

                    if button.is_displayed() and button.is_enabled():
                        return button

                except Exception:
                    continue

            # 마지막 시도: 텍스트로 검색
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                try:
                    button_text = button.text.strip()
                    if any(
                        keyword in button_text
                        for keyword in ["원산지", "영양성분", "알레르기"]
                    ):
                        if button.is_displayed() and button.is_enabled():
                            return button
                except Exception:
                    continue

            return None

        except Exception as e:
            logger.error(f"영양정보 버튼 찾기 실패: {str(e)}")
            return None

    def _extract_nutrition_from_modal(self, driver):
        """모달에서 영양정보 추출"""
        try:
            # 모달 완전 로딩 대기
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "modalWrap"))
            )
            time.sleep(3)

            # 영양성분 테이블 찾기
            nutrition_table = driver.find_element(
                By.XPATH,
                "//h2[contains(text(), '영양성분')]/following-sibling::table",
            )

            tbody = nutrition_table.find_element(By.TAG_NAME, "tbody")
            data_rows = tbody.find_elements(By.TAG_NAME, "tr")

            if data_rows:
                first_row = data_rows[0]
                cells = first_row.find_elements(By.TAG_NAME, "td")

                if len(cells) >= 7:
                    nutrition_data = {}

                    # 영양정보 추출 (괄호 안 숫자 제거)
                    try:
                        nutrition_data["calories"] = self._parse_number(
                            cells[1].text.strip()
                        )
                    except:
                        nutrition_data["calories"] = None

                    try:
                        protein_text = cells[2].text.strip()
                        protein_value = (
                            protein_text.split("(")[0]
                            if "(" in protein_text
                            else protein_text
                        )
                        nutrition_data["protein"] = self._parse_number(protein_value)
                    except:
                        nutrition_data["protein"] = None

                    try:
                        sodium_text = cells[3].text.strip()
                        sodium_value = (
                            sodium_text.split("(")[0]
                            if "(" in sodium_text
                            else sodium_text
                        )
                        nutrition_data["sodium"] = self._parse_number(sodium_value)
                    except:
                        nutrition_data["sodium"] = None

                    try:
                        nutrition_data["sugar"] = self._parse_number(
                            cells[4].text.strip()
                        )
                    except:
                        nutrition_data["sugar"] = None

                    try:
                        fat_text = cells[5].text.strip()
                        fat_value = (
                            fat_text.split("(")[0] if "(" in fat_text else fat_text
                        )
                        nutrition_data["fat"] = self._parse_number(fat_value)
                    except:
                        nutrition_data["fat"] = None

                    return nutrition_data

            return None

        except Exception as e:
            logger.error(f"영양정보 추출 실패: {str(e)}")
            return None

    def _close_nutrition_modal(self, driver):
        """영양정보 모달 닫기"""
        try:
            # 확인 버튼이나 닫기 버튼 찾기
            close_selectors = [
                "//button[contains(text(), '확인')]",
                ".pop_foot button",
                ".modalWrap button",
            ]

            for selector in close_selectors:
                try:
                    if selector.startswith("//"):
                        close_btn = driver.find_element(By.XPATH, selector)
                    else:
                        close_btn = driver.find_element(By.CSS_SELECTOR, selector)

                    if close_btn.is_displayed():
                        driver.execute_script("arguments[0].click();", close_btn)
                        time.sleep(1)
                        logger.info("Closed nutrition modal")
                        return
                except:
                    continue

            # ESC 키로 모달 닫기 시도
            from selenium.webdriver.common.keys import Keys

            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(1)

        except Exception as e:
            logger.warning(f"Could not close nutrition modal: {str(e)}")

    def _extract_description_from_detail_page(self, driver):
        """상세 페이지에서 description 추출"""
        try:
            description_data = {}

            # description 추출
            try:
                description_element = driver.find_element(
                    By.CSS_SELECTOR, ".description span"
                )
                description_text = self.clean_text(description_element.text)
                if description_text:
                    description_data["description"] = description_text
                    description_data["description_full"] = description_text
                else:
                    description_data["description"] = None
                    description_data["description_full"] = None
            except Exception:
                description_data["description"] = None
                description_data["description_full"] = None

            return description_data

        except Exception as e:
            logger.error(f"설명 추출 실패: {str(e)}")
            return {"description": None, "description_full": None}

    def _parse_number(self, text):
        """텍스트에서 숫자 추출"""
        try:
            # 숫자와 소수점만 추출
            numbers = re.findall(r"\d+\.?\d*", text)
            if numbers:
                return float(numbers[0])
            return None
        except:
            return None
