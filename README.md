<div align="center">
  <h2>🍔 Burger Crawler</h2>
  <h3><b><i>"지식은 햄버거를 대신할 수 없어"</i></b></h3>
  <p>햄버거 신제품 정보를 자동 수집하여 Supabase에 저장</p>
</div>

## 🚀 Features

- 🕷️ **멀티 브랜드 크롤링**: 맥도날드, 버거킹, 롯데리아 등 주요 브랜드
- 📅 **자동 스케줄링**: 정기적으로 신제품 정보 수집
- 🗄️ **Supabase 연동**: 수집된 데이터를 클라우드 DB에 안전하게 저장
- 🔄 **중복 제거**: 이미 수집된 제품은 자동으로 필터링
- 📝 **상세 로깅**: 크롤링 과정과 결과를 상세하게 기록

## 🛠️ Tech Stack

- **Language**: Python 3.8+
- **Database**: Supabase (PostgreSQL)
- **Web Scraping**: Requests, BeautifulSoup4, Selenium
- **Scheduling**: Schedule, APScheduler
- **Logging**: Loguru
- **Environment**: python-dotenv

## 📦 Installation

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

## ⚙️ Configuration

`.env` 파일에서 다음 설정을 편집하세요:

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

## 🗃️ Database Schema

Supabase에 다음과 같은 테이블 구조가 필요합니다:

```sql
-- 추후 DB 스키마를 알려주시면 여기에 추가
```

## 🚀 Usage

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

## 🕷️ Supported Brands

- 🟡 **맥도날드** (McDonald's)
- 🔴 **버거킹** (Burger King)
- 🟠 **롯데리아** (Lotteria)
- 🔵 **KFC** (추가 예정)
- 🟢 **맘스터치** (추가 예정)

## 📂 Project Structure

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

## 📋 TODO

- [ ] 실제 브랜드 사이트 크롤링 로직 구현
- [ ] 이미지 다운로드 및 저장 기능
- [ ] 가격 변동 추적 기능
- [ ] 웹 대시보드 추가
- [ ] API 엔드포인트 제공
- [ ] 알림 기능 (Discord, Slack 등)

## 🤝 Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 📞 Contact

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.
