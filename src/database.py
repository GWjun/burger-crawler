from supabase import create_client, Client
from loguru import logger
from config import settings
from typing import List, Dict, Any, Optional
import json
from decimal import Decimal
from datetime import datetime


class SupabaseManager:
    def __init__(self):
        """
        Initialize the SupabaseManager with a Supabase client using configuration settings.
        """
        self.client: Client = create_client(
            settings.supabase_url, settings.supabase_key
        )
        logger.info("Supabase client initialized")

    def get_or_create_brand(self, brand_data: Dict[str, Any]) -> Optional[int]:
        """
        Retrieve the ID of a brand by name, or create a new brand entry if it does not exist.
        
        Parameters:
            brand_data (Dict[str, Any]): Dictionary containing brand information, including the brand name.
        
        Returns:
            Optional[int]: The ID of the existing or newly created brand, or None if the operation fails.
        """
        try:
            # 기존 브랜드 조회
            result = (
                self.client.table("Brand")
                .select("id")
                .eq("name", brand_data["name"])
                .execute()
            )

            if result.data:
                brand_id = result.data[0]["id"]
                logger.info(
                    f"Found existing brand: {brand_data['name']} (ID: {brand_id})"
                )
                return brand_id
            else:
                # 새 브랜드 생성
                result = self.client.table("Brand").insert(brand_data).execute()
                brand_id = result.data[0]["id"]
                logger.info(f"Created new brand: {brand_data['name']} (ID: {brand_id})")
                return brand_id

        except Exception as e:
            logger.error(f"Failed to get or create brand: {str(e)}")
            return None

    def insert_product_data(self, product_data: Dict[str, Any]) -> Optional[int]:
        """
        Insert product data into the Supabase "Product" table and return the inserted product's ID.
        
        Parameters:
            product_data (dict): Dictionary containing product information to be inserted.
        
        Returns:
            int or None: The ID of the inserted product if successful, otherwise None.
        """
        try:
            # 데이터 직렬화
            serialized_data = self._serialize_data(product_data)
            result = self.client.table("Product").insert(serialized_data).execute()
            product_id = result.data[0]["product_id"]
            logger.info(
                f"Product inserted successfully: {product_data.get('name', 'Unknown')} (ID: {product_id})"
            )
            return product_id
        except Exception as e:
            logger.error(f"Failed to insert product data: {str(e)}")
            return None

    def insert_nutrition_data(self, nutrition_data: Dict[str, Any]) -> bool:
        """
        Insert nutrition data into the Supabase "Nutrition" table.
        
        Serializes the provided nutrition data and attempts to insert it into the database.
        
        Returns:
            bool: True if the insertion succeeds, False otherwise.
        """
        try:
            # 데이터 직렬화
            serialized_data = self._serialize_data(nutrition_data)
            result = self.client.table("Nutrition").insert(serialized_data).execute()
            logger.info(
                f"Nutrition data inserted successfully for product_id: {nutrition_data.get('product_id')}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to insert nutrition data: {str(e)}")
            return False

    def insert_complete_burger_data(self, burger_data: Dict[str, Any]) -> bool:
        """
        Insert a complete burger entry, including brand, product, and optional nutrition data, into the database.
        
        Attempts to create or retrieve the brand, insert the product, and, if nutrition information is provided, insert the associated nutrition data. Returns True if all required steps succeed, otherwise False.
        """
        try:
            # 1. 브랜드 확인/생성
            brand_data = {
                "name": burger_data["brand_name"],
                "name_eng": burger_data.get(
                    "brand_name_eng", burger_data["brand_name"].lower()
                ),
                "description": burger_data.get("brand_description"),
                "logo_url": burger_data.get("brand_logo_url"),
                "website_url": burger_data.get("brand_website_url"),
            }

            brand_id = self.get_or_create_brand(brand_data)
            if not brand_id:
                return False

            # 2. 제품 데이터 준비
            product_data = {
                "name": burger_data["name"],
                "description": burger_data.get("description"),
                "description_full": burger_data.get("description_full"),
                "image_url": burger_data.get("image_url"),
                "price": burger_data["price"],
                "set_price": burger_data.get("set_price"),
                "available": burger_data.get("available", True),
                "category": burger_data.get("category", "버거"),
                "shop_url": burger_data.get("shop_url"),
                "brand_name": burger_data["brand_name"],
                "released_at": burger_data.get("released_at"),
                "patty": burger_data.get("patty", "undefined"),
            }

            # 3. 제품 삽입
            product_id = self.insert_product_data(product_data)
            if not product_id:
                return False

            # 4. 영양 정보가 있으면 삽입
            if burger_data.get("nutrition"):
                nutrition_data = {
                    "product_id": product_id,
                    "calories": (
                        Decimal(str(burger_data["nutrition"]["calories"]))
                        if burger_data["nutrition"].get("calories")
                        else None
                    ),
                    "fat": (
                        Decimal(str(burger_data["nutrition"]["fat"]))
                        if burger_data["nutrition"].get("fat")
                        else None
                    ),
                    "protein": (
                        Decimal(str(burger_data["nutrition"]["protein"]))
                        if burger_data["nutrition"].get("protein")
                        else None
                    ),
                    "sugar": (
                        Decimal(str(burger_data["nutrition"]["sugar"]))
                        if burger_data["nutrition"].get("sugar")
                        else None
                    ),
                    "sodium": (
                        Decimal(str(burger_data["nutrition"]["sodium"]))
                        if burger_data["nutrition"].get("sodium")
                        else None
                    ),
                }
                self.insert_nutrition_data(nutrition_data)

            return True

        except Exception as e:
            logger.error(f"Failed to insert complete burger data: {str(e)}")
            return False

    def insert_bulk_burger_data(self, data_list: List[Dict[str, Any]]) -> bool:
        """
        Insert multiple burger data entries in bulk.
        
        Iterates over a list of burger data dictionaries, inserting each one individually. Returns True if at least one insert succeeds; otherwise, returns False.
        """
        try:
            success_count = 0
            for burger_data in data_list:
                if self.insert_complete_burger_data(burger_data):
                    success_count += 1

            logger.info(
                f"Bulk insert completed: {success_count}/{len(data_list)} items successful"
            )
            return success_count > 0

        except Exception as e:
            logger.error(f"Failed to insert bulk data: {str(e)}")
            return False

    def check_duplicate_product(self, name: str, brand_name: str) -> bool:
        """
        Check if a product with the given name and brand already exists in the database.
        
        Parameters:
            name (str): The name of the product to check.
            brand_name (str): The name of the brand associated with the product.
        
        Returns:
            bool: True if a duplicate product exists, False otherwise or on error.
        """
        try:
            result = (
                self.client.table("Product")
                .select("product_id")
                .eq("name", name)
                .eq("brand_name", brand_name)
                .execute()
            )
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Failed to check duplicate product: {str(e)}")
            return False

    def get_latest_products(
        self, limit: int = 10, brand_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most recent products, optionally filtered by brand name.
        
        Parameters:
            limit (int): Maximum number of products to retrieve. Defaults to 10.
            brand_name (str, optional): If provided, only products from this brand are returned.
        
        Returns:
            List[Dict[str, Any]]: A list of product records, or an empty list if retrieval fails.
        """
        try:
            query = (
                self.client.table("Product")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
            )

            if brand_name:
                query = query.eq("brand_name", brand_name)

            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Failed to get latest products: {str(e)}")
            return []

    def get_product_with_nutrition(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a product by its ID along with its associated nutrition information.
        
        Parameters:
            product_id (int): The unique identifier of the product to retrieve.
        
        Returns:
            dict or None: A dictionary containing product data with an added "nutrition" key if nutrition information exists, or None if the product is not found or an error occurs.
        """
        try:
            # 제품 정보 조회
            product_result = (
                self.client.table("Product")
                .select("*")
                .eq("product_id", product_id)
                .execute()
            )
            if not product_result.data:
                return None

            product = product_result.data[0]

            # 영양정보 조회
            nutrition_result = (
                self.client.table("Nutrition")
                .select("*")
                .eq("product_id", product_id)
                .execute()
            )
            if nutrition_result.data:
                product["nutrition"] = nutrition_result.data[0]

            return product

        except Exception as e:
            logger.error(f"Failed to get product with nutrition: {str(e)}")
            return None

    def _serialize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a dictionary's values to JSON-serializable formats.
        
        Datetime objects are converted to ISO 8601 strings, Decimal objects to floats, and None values are preserved. All other types remain unchanged.
        
        Parameters:
            data (Dict[str, Any]): The input dictionary to serialize.
        
        Returns:
            Dict[str, Any]: A new dictionary with all values converted to JSON-serializable types.
        """
        serialized = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                # datetime을 ISO 형식 문자열로 변환
                serialized[key] = value.isoformat()
            elif isinstance(value, Decimal):
                # Decimal을 float로 변환
                serialized[key] = float(value)
            elif value is None:
                serialized[key] = None
            else:
                serialized[key] = value
        return serialized
