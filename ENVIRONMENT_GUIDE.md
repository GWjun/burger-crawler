# 환경 설정 가이드

## 환경별 설정

프로젝트는 개발과 프로덕션 환경을 간단하게 분리할 수 있습니다.

### 설정 파일들

- `.env.development` - 개발 환경 설정
- `.env.production` - 프로덕션 환경 설정
- `.env.example` - 설정 예시 파일

### 환경별 실행 방법

#### Windows에서:

```bash
# 개발 환경으로 실행
run_dev.bat

# 프로덕션 환경으로 실행
run_prod.bat
```

#### Linux/Mac에서:

```bash
# 개발 환경으로 실행
chmod +x run_dev.sh
./run_dev.sh

# 프로덕션 환경으로 실행
chmod +x run_prod.sh
./run_prod.sh
```

#### 직접 환경변수 설정:

```bash
# 개발 환경
set ENVIRONMENT=development  # Windows
export ENVIRONMENT=development  # Linux/Mac
python main.py

# 프로덕션 환경
set ENVIRONMENT=production  # Windows
export ENVIRONMENT=production  # Linux/Mac
python main.py
```

### 주요 차이점

#### 개발 환경:

- `HEADLESS_MODE=false` (브라우저가 보임)
- `LOG_LEVEL=DEBUG` (상세한 로그)
- `REQUEST_DELAY=2` (더 긴 지연)
- `CRAWL_INTERVAL_HOURS=1` (1시간마다 크롤링)

#### 프로덕션 환경:

- `HEADLESS_MODE=true` (브라우저가 숨겨짐)
- `LOG_LEVEL=INFO` (기본 로그)
- `REQUEST_DELAY=1` (짧은 지연)
- `CRAWL_INTERVAL_HOURS=6` (6시간마다 크롤링)

### 설정 순서

1. `.env.example`을 복사하여 `.env.development` 및 `.env.production` 생성
2. 각 파일에서 실제 Supabase URL과 키 설정
3. 필요에 따라 다른 설정값들 조정
4. 해당 환경 스크립트로 실행

환경변수 `ENVIRONMENT`가 설정되지 않으면 기본적으로 `development` 환경으로 실행됩니다.
