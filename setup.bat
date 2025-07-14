@echo off
echo 🍔 Burger Crawler Setup Script
echo ================================

REM Python 가상환경 생성
echo Creating virtual environment...
python -m venv venv

REM 가상환경 활성화 (Windows)
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM 패키지 설치
echo Installing packages...
pip install --upgrade pip
pip install -r requirements.txt

REM 로그 디렉토리 생성
echo Creating logs directory...
if not exist "logs" mkdir logs

REM 환경 변수 파일 복사
echo Setting up environment files...
if not exist ".env.development" (
    copy .env.example .env.development
    echo ✅ Created .env.development
)
if not exist ".env.production" (
    copy .env.example .env.production
    echo ✅ Created .env.production
)

echo ✅ Setup completed!
echo.
echo Next steps:
echo 1. Edit .env.development and .env.production files with your Supabase credentials
echo 2. Run development: run_dev.bat
echo 3. Run production: run_prod.bat
echo 4. Test database connection: python main.py test-db

pause
