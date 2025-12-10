#!/bin/bash
# ComfyUI와 Stable Diffusion WebUI 설치 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICES_DIR="${SERVICES_DIR:-$HOME/.hyperwise-services}"

echo "🚀 HyperWise Agent 서비스 설치 스크립트"
echo "=========================================="
echo ""

# 서비스 디렉토리 생성
mkdir -p "$SERVICES_DIR"
cd "$SERVICES_DIR"

# ComfyUI 설치
if [ ! -d "ComfyUI" ]; then
    echo "📦 ComfyUI 설치 중..."
    git clone https://github.com/comfyanonymous/ComfyUI.git
    cd ComfyUI
    pip install -r requirements.txt
    cd ..
    echo "✅ ComfyUI 설치 완료"
else
    echo "ℹ️  ComfyUI가 이미 설치되어 있습니다: $SERVICES_DIR/ComfyUI"
fi

# Stable Diffusion WebUI 설치
if [ ! -d "stable-diffusion-webui" ]; then
    echo "📦 Stable Diffusion WebUI 설치 중..."
    git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
    cd stable-diffusion-webui
    # WebUI는 자체 설치 스크립트를 실행
    echo "✅ Stable Diffusion WebUI 설치 완료"
    cd ..
else
    echo "ℹ️  Stable Diffusion WebUI가 이미 설치되어 있습니다: $SERVICES_DIR/stable-diffusion-webui"
fi

echo ""
echo "=========================================="
echo "✅ 설치 완료!"
echo ""
echo "다음 명령으로 환경 변수를 설정하세요:"
echo ""
echo "export COMFYUI_PATH=$SERVICES_DIR/ComfyUI"
echo "export WEBUI_PATH=$SERVICES_DIR/stable-diffusion-webui"
echo ""
echo "또는 .env 파일에 추가하세요:"
echo "COMFYUI_PATH=$SERVICES_DIR/ComfyUI"
echo "WEBUI_PATH=$SERVICES_DIR/stable-diffusion-webui"

