<div align="center">
  <h2>🍔 Burger Crawler</h2>
  <h3><b><i>"지식은 햄버거를 대신할 수 없어"</i></b></h3>
  <p>햄버거 신제품 정보를 자동 수집하여 Supabase에 저장</p>
</div>

## 드라이버 설치

#### Microsoft Edge 브라우저 및 WebDriver

본 프로젝트는 Selenium WebDriver를 사용하여 동적 웹 페이지를 크롤링합니다. Edge 브라우저와 호환되는 WebDriver가 필요합니다.

**필수 요구사항:**

- **Microsoft Edge 브라우저**: 버전 138.0.3351.83 이상
- **Edge WebDriver**: 브라우저 버전과 일치하는 msedgedriver.exe

**WebDriver 설치:**

- [Microsoft Edge WebDriver 다운로드 페이지](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)에서 브라우저 버전과 일치하는 드라이버 다운로드
- `edgedriver_win64/` 폴더에 `msedgedriver.exe` 파일 배치

```
burger-crawler/
├── edgedriver_win64/
│   └── msedgedriver.exe  # Edge WebDriver 실행 파일
└── ...
```

**버전 호환성 확인:**

```bash
# Edge 브라우저 버전 확인
edge://version/

# WebDriver 버전 확인
./edgedriver_win64/msedgedriver.exe --version
```

## 패키지 설치

### Windows

```bash
# 저장소 클론
git clone <repository-url>
cd burger-crawler

# 설정 스크립트 실행
.\setup.bat
```

### Linux/Mac

```bash
# 저장소 클론
git clone <repository-url>
cd burger-crawler

# 설정 스크립트 실행
chmod +x setup.sh
./setup.sh
```

### Manual Setup

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Linux/Mac

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집
```

## 환경 변수 설정

`.env` 파일에서 다음 필수 설정을 편집합니다:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Crawling Settings
HEADLESS_MODE=True
REQUEST_DELAY=1
CRAWL_INTERVAL_HOURS=6
```

## DB 스키마

Supabase에 다음과 같은 테이블 구조를 사용합니다

```sql
-- 브랜드 테이블
model Brand {
  id                   BigInt      @id @default(autoincrement())
  name                 String      @unique @db.VarChar
  description          String?
  logo_url             String?     @db.VarChar
  website_url          String?     @db.VarChar
  created_at           DateTime    @default(now()) @db.Timestamptz(6)
  likes_count          Int         @default(0)
  name_eng             String      @unique @db.VarChar
  background_image_url String?     @db.VarChar
  Product              Product[]
}

-- 제품 테이블
model Product {
  product_id       BigInt        @id @default(autoincrement())
  created_at       DateTime      @default(now()) @db.Timestamptz(6)
  name             String        @db.VarChar
  description      String?
  image_url        String?       @db.VarChar
  price            Int
  available        Boolean?      @default(true)
  category         String?       @db.VarChar
  shop_url         String?       @db.VarChar
  set_price        Int?
  description_full String?
  released_at      DateTime?     @db.Timestamptz(6)
  brand_name       String        @db.VarChar
  likes_count      Int           @default(0)
  dislikes_count   Int           @default(0)
  patty            Patty         @default(undefined)
  dev_comment      String?       @db.VarChar
  review_count     Int           @default(0)
  score_avg        Float         @default(0) @db.Real
  Nutrition        Nutrition?
  Brand            Brand         @relation(fields: [brand_name], references: [name])
}

-- 영양 정보 테이블
model Nutrition {
  product_id BigInt   @id @default(autoincrement())
  calories   Decimal? @db.Decimal
  fat        Decimal? @db.Decimal
  protein    Decimal? @db.Decimal
  sugar      Decimal? @db.Decimal
  sodium     Decimal? @db.Decimal
  created_at DateTime @default(now()) @db.Timestamptz(6)
  Products   Product  @relation(fields: [product_id], references: [product_id])
}
```

## 사용 방법

### 기본 실행 (스케줄러 시작)

```bash
python main.py
```

### 명령어 옵션

```bash
# 데이터베이스 연결 테스트
python main.py test-db

# 특정 브랜드 크롤러 테스트
python main.py test-crawler mcdonalds

# 모든 크롤러 한 번 실행
python main.py run-once

# 스케줄러 시작
python main.py scheduler
```

## 브랜드 출처

- **롯데리아** (Lotteria)
- **버거킹** (Burger King)
- **노브랜드 버거** (No Brand Burger)
- **KFC** (Kentucky Fried Chicken)

## 프로젝트 구조

```
burger-crawler/
├── src/
│   ├── crawlers/           # 크롤러 패키지
│   │   ├── __init__.py     # 패키지 초기화
│   │   ├── base.py         # 기본 크롤러 클래스
│   │   ├── factory.py      # 크롤러 팩토리
│   │   ├── lotteria.py     # 롯데리아 크롤러
│   │   ├── burger_king.py  # 버거킹 크롤러
│   │   ├── nobrand_burger.py # 노브랜드 버거 크롤러
│   │   └── kfc.py          # KFC 크롤러
│   ├── database.py         # Supabase 연동
│   ├── scheduler.py        # 스케줄링 로직
│   └── __mock__/           # 테스트용 더미 데이터
│       └── dummy_data.py
├── edgedriver_win64/       # Edge WebDriver
│   └── msedgedriver.exe    # Edge WebDriver 실행 파일
├── logs/                   # 로그 파일들
├── config.py               # 설정 관리
├── main.py                 # 메인 실행 파일
├── requirements.txt        # 의존성 패키지
├── .env.example            # 환경 변수 예시
└── README.md
```
