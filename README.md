<div align="center">
  <h2>🍔 Burger Crawler</h2>
  <h3><b><i>"지식은 햄버거를 대신할 수 없어"</i></b></h3>
  <p>햄버거 신제품 정보를 자동 수집하여 Supabase에 저장</p>
</div>

## 설치

### Windows

```bash
# 저장소 클론
git clone <repository-url>
cd burger-crawler

# 설정 스크립트 실행
setup.bat
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

`.env` 파일에서 다음 설정을 편집:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_KEY=your_supabase_service_key_here

# Crawling Settings
HEADLESS_MODE=True
REQUEST_DELAY=1
CRAWL_INTERVAL_HOURS=6
```

## DB 스키마

Supabase에 다음과 같은 테이블 구조가 필요합니다:

```sql
-- 추후 DB 스키마
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

## 프로젝트 구조

```
burger-crawler/
├── src/
│   ├── crawlers.py      # 크롤러 클래스들
│   ├── database.py      # Supabase 연동
│   └── scheduler.py     # 스케줄링 로직
├── logs/                # 로그 파일들
├── config.py            # 설정 관리
├── main.py              # 메인 실행 파일
├── requirements.txt     # 의존성 패키지
├── .env.example         # 환경 변수 예시
└── README.md
```
