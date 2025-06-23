#!/bin/bash

echo "🧪 Burger Crawler Test Script"
echo "============================="

# 가상환경 활성화
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/Scripts/activate
else
    echo "❌ Virtual environment not found. Run setup.bat first."
    exit 1
fi

# 환경 변수 체크
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Copy .env.example to .env and configure it."
    exit 1
fi

echo "✅ Environment setup complete"
echo ""

# 테스트 실행
echo "🔍 Running tests..."
echo ""

echo "1. Testing database connection..."
python main.py test-db

echo ""
echo "2. Testing with dummy data..."
python main.py test-dummy

echo ""
echo "3. Testing crawler (lotteria)..."
python main.py test-crawler lotteria

echo ""
echo "🎉 All tests completed!"
