@echo off
echo 🧪 Burger Crawler Test Script
echo =============================

REM 가상환경 활성화
if exist "venv" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ❌ Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

REM 환경 변수 체크
if not exist ".env" (
    echo ❌ .env file not found. Copy .env.example to .env and configure it.
    pause
    exit /b 1
)

echo ✅ Environment setup complete
echo.

REM 테스트 실행
echo 🔍 Running tests...
echo.

echo 1. Testing database connection...
python main.py test-db

echo.
echo 2. Testing with dummy data...
python main.py test-dummy

echo.
echo 3. Testing crawler (lotteria)...
python main.py test-crawler lotteria

echo.
echo 🎉 All tests completed!
pause
