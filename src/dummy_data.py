from typing import List, Dict, Any
from datetime import datetime
import random


def create_dummy_burger_data() -> List[Dict[str, Any]]:
    """테스트용 더미 버거 데이터 생성"""
    
    brands = [
        {'name': '롯데리아', 'name_eng': 'lotteria', 'url': 'https://www.lotteria.com'},
        {'name': '버거킹', 'name_eng': 'burger_king', 'url': 'https://www.burgerking.co.kr'},
        {'name': '노브랜드 버거', 'name_eng': 'nobrand_burger', 'url': 'https://www.nobrand.co.kr'},
        {'name': 'KFC', 'name_eng': 'kfc', 'url': 'https://www.kfc.co.kr'},
    ]
    
    burger_names = [
        '빅맥 버거', '와퍼 버거', '치킨 버거', '베이컨 버거', '치즈 버거',
        '더블 버거', '스파이시 버거', '바베큐 버거', '머쉬룸 버거', '아보카도 버거'
    ]
    
    descriptions = [
        '맛있는 패티와 신선한 야채가 들어간 버거',
        '육즙 가득한 고기와 특제 소스의 조화',
        '바삭한 치킨과 크리미한 마요네즈',
        '진한 치즈와 부드러운 빵의 완벽한 조합',
        '매콤달콤한 소스가 일품인 버거'
    ]
    
    dummy_data = []
    
    for i in range(20):  # 20개의 더미 데이터 생성
        brand = random.choice(brands)
        burger_name = f"{random.choice(burger_names)} {i+1}"
        
        burger_data = {
            'name': burger_name,
            'brand_name': brand['name'],
            'brand_name_eng': brand['name_eng'],
            'description': random.choice(descriptions),
            'description_full': f"{random.choice(descriptions)} 더 자세한 설명과 함께 맛있는 재료들이 풍부하게 들어있습니다.",
            'image_url': f"https://example.com/images/burger_{i+1}.jpg",
            'price': random.randint(4000, 12000),
            'set_price': random.randint(6000, 15000),
            'available': random.choice([True, True, True, False]),  # 대부분 available
            'category': random.choice(['버거', '치킨버거', '프리미엄버거']),
            'shop_url': f"{brand['url']}/menu/burger_{i+1}",
            'released_at': datetime.now(),
            'patty': random.choice(['beef', 'chicken', 'pork', 'undefined']),
            'brand_description': f"{brand['name']} 브랜드 설명",
            'brand_logo_url': f"{brand['url']}/logo.png",
            'brand_website_url': brand['url'],
            'nutrition': {
                'calories': random.randint(300, 800),
                'fat': round(random.uniform(10.0, 40.0), 1),
                'protein': round(random.uniform(15.0, 35.0), 1),
                'sugar': round(random.uniform(2.0, 15.0), 1),
                'sodium': random.randint(500, 1500)
            } if random.choice([True, False]) else None  # 50% 확률로 영양정보 포함
        }
        
        dummy_data.append(burger_data)
    
    return dummy_data


def get_brand_dummy_data(brand_name: str, count: int = 5) -> List[Dict[str, Any]]:
    """특정 브랜드의 더미 데이터 생성"""
    
    brand_info = {
        'lotteria': {'name': '롯데리아', 'name_eng': 'lotteria', 'url': 'https://www.lotteria.com'},
        'burger_king': {'name': '버거킹', 'name_eng': 'burger_king', 'url': 'https://www.burgerking.co.kr'},
        'nobrand_burger': {'name': '노브랜드 버거', 'name_eng': 'nobrand_burger', 'url': 'https://www.nobrand.co.kr'},
        'kfc': {'name': 'KFC', 'name_eng': 'kfc', 'url': 'https://www.kfc.co.kr'},
    }
    
    if brand_name not in brand_info:
        return []
    
    brand = brand_info[brand_name]
    
    # 브랜드별 특화 메뉴
    brand_menus = {
        'lotteria': ['새우버거', '한우버거', '불고기버거', '치킨버거', '에그버거'],
        'burger_king': ['와퍼', '치킨킹', '바베큐킹', '치즈와퍼', '더블와퍼'],
        'nobrand_burger': ['노브랜드버거', '치킨버거', '더블버거', '치즈버거', '베이컨버거'],
        'kfc': ['징거버거', '치킨필레버거', '핫크리스피버거', '타워버거', '치킨앤치즈']
    }
    
    dummy_data = []
    menus = brand_menus.get(brand_name, ['버거1', '버거2', '버거3', '버거4', '버거5'])
    
    for i in range(min(count, len(menus))):
        burger_data = {
            'name': menus[i],
            'brand_name': brand['name'],
            'brand_name_eng': brand['name_eng'],
            'description': f"{brand['name']}의 대표 메뉴 {menus[i]}",
            'description_full': f"{menus[i]}는 {brand['name']}에서 가장 인기 있는 메뉴 중 하나입니다.",
            'image_url': f"{brand['url']}/images/{menus[i].lower()}.jpg",
            'price': random.randint(4000, 12000),
            'set_price': random.randint(6000, 15000),
            'available': True,
            'category': '치킨버거' if 'kfc' in brand_name else '버거',
            'shop_url': f"{brand['url']}/menu/{menus[i].lower()}",
            'released_at': datetime.now(),
            'patty': 'chicken' if 'kfc' in brand_name else random.choice(['beef', 'chicken', 'pork']),
            'brand_description': f"{brand['name']} 브랜드",
            'brand_logo_url': f"{brand['url']}/logo.png",
            'brand_website_url': brand['url'],
            'nutrition': {
                'calories': random.randint(300, 800),
                'fat': round(random.uniform(10.0, 40.0), 1),
                'protein': round(random.uniform(15.0, 35.0), 1),
                'sugar': round(random.uniform(2.0, 15.0), 1),
                'sodium': random.randint(500, 1500)
            }
        }
        
        dummy_data.append(burger_data)
    
    return dummy_data
