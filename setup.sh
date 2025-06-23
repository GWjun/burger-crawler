#!/bin/bash

echo "🍔 Burger Crawler Setup Script"
echo "================================"

# Python 가상환경 생성
echo "Creating virtual environment..."
python -m venv venv

# 가상환경 활성화 (Windows)
echo "Activating virtual environment..."
source venv/Scripts/activate

# 패키지 설치
echo "Installing packages..."
pip install --upgrade pip
pip install -r requirements.txt

# 로그 디렉토리 생성
echo "Creating logs directory..."
mkdir -p logs

# 환경 변수 파일 복사
echo "Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please edit .env file with your Supabase credentials"
fi

echo "✅ Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Supabase credentials"
echo "2. Test database connection: python main.py test-db"
echo "3. Test crawler: python main.py test-crawler mcdonalds"
echo "4. Run once: python main.py run-once"
echo "5. Start scheduler: python main.py scheduler"
