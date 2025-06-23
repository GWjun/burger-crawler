from supabase import create_client, Client
from loguru import logger
from config import settings
from typing import List, Dict, Any


class SupabaseManager:
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
        logger.info("Supabase client initialized")

    def insert_burger_data(self, data: Dict[str, Any]) -> bool:
        """
        햄버거 데이터를 Supabase에 삽입
        """
        try:
            result = self.client.table('burgers').insert(data).execute()
            logger.info(f"Data inserted successfully: {data.get('name', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert data: {str(e)}")
            return False

    def insert_bulk_burger_data(self, data_list: List[Dict[str, Any]]) -> bool:
        """
        여러 햄버거 데이터를 일괄 삽입
        """
        try:
            result = self.client.table('burgers').insert(data_list).execute()
            logger.info(f"Bulk data inserted successfully: {len(data_list)} items")
            return True
        except Exception as e:
            logger.error(f"Failed to insert bulk data: {str(e)}")
            return False

    def check_duplicate(self, name: str, brand: str) -> bool:
        """
        중복 데이터 확인
        """
        try:
            result = self.client.table('burgers').select("id").eq("name", name).eq("brand", brand).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Failed to check duplicate: {str(e)}")
            return False

    def get_latest_burgers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        최신 햄버거 데이터 조회
        """
        try:
            result = self.client.table('burgers').select("*").order("created_at", desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Failed to get latest burgers: {str(e)}")
            return []
