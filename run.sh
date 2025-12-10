#!/bin/bash
# HyperWise Agent 실행 스크립트 (macOS/Linux)

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 HyperWise Agent 시작 중...${NC}"

# 가상환경 확인 및 활성화
if [ -d "venv" ]; then
    echo -e "${YELLOW}📦 가상환경 활성화 중...${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${YELLOW}📦 가상환경 활성화 중...${NC}"
    source .venv/bin/activate
else
    echo -e "${YELLOW}⚠️  가상환경을 찾을 수 없습니다. 시스템 Python을 사용합니다.${NC}"
fi

# Python 버전 확인 및 선택
echo -e "${YELLOW}🐍 Python 버전 확인 중...${NC}"
# Python 3.11 우선 사용 (패키지가 3.11에 설치되어 있음)
if command -v python3.11 &> /dev/null; then
    python3.11 --version
    PYTHON_CMD="python3.11"
    PIP_CMD="pip3.11"
elif [ -f "venv/bin/python3" ]; then
    ./venv/bin/python3 --version
    PYTHON_CMD="./venv/bin/python3"
    PIP_CMD="./venv/bin/pip3"
elif [ -f ".venv/bin/python3" ]; then
    .venv/bin/python3 --version
    PYTHON_CMD=".venv/bin/python3"
    PIP_CMD=".venv/bin/pip3"
else
    python3 --version
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
fi

# 의존성 확인 및 설치
echo -e "${YELLOW}📋 의존성 확인 중...${NC}"
if ! $PYTHON_CMD -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}📥 의존성 설치 중...${NC}"
    $PIP_CMD install -r requirements.txt
else
    echo -e "${GREEN}✅ 의존성이 이미 설치되어 있습니다${NC}"
fi

# 환경 변수 확인
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 파일이 없습니다. .env.example을 참조하여 생성하세요.${NC}"
fi

# 서버 시작
echo -e "${GREEN}✅ 서버 시작 중...${NC}"
echo -e "${GREEN}📍 API 문서: http://localhost:8000/docs${NC}"
echo -e "${GREEN}📍 API 엔드포인트: http://localhost:8000/api/v1/${NC}"
echo ""

$PYTHON_CMD -m app.main
