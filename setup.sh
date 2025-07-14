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
echo "Setting up environment files..."
if [ ! -f .env.development ]; then
    cp .env.example .env.development
    echo "✅ Created .env.development"
fi
if [ ! -f .env.production ]; then
    cp .env.example .env.production
    echo "✅ Created .env.production"
fi

echo "✅ Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env.development and .env.production files with your Supabase credentials"
echo "2. Run development: ./run_dev.sh"
echo "3. Run production: ./run_prod.sh"
echo "4. Test database connection: python main.py test-db"
