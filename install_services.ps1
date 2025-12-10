# ComfyUI와 Stable Diffusion WebUI 설치 스크립트 (PowerShell)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ServicesDir = if ($env:SERVICES_DIR) { $env:SERVICES_DIR } else { "$env:USERPROFILE\.hyperwise-services" }

Write-Host "🚀 HyperWise Agent 서비스 설치 스크립트" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 서비스 디렉토리 생성
if (-not (Test-Path $ServicesDir)) {
    New-Item -ItemType Directory -Path $ServicesDir | Out-Null
}
Set-Location $ServicesDir

# ComfyUI 설치
if (-not (Test-Path "ComfyUI")) {
    Write-Host "📦 ComfyUI 설치 중..." -ForegroundColor Yellow
    git clone https://github.com/comfyanonymous/ComfyUI.git
    Set-Location ComfyUI
    pip install -r requirements.txt
    Set-Location ..
    Write-Host "✅ ComfyUI 설치 완료" -ForegroundColor Green
} else {
    Write-Host "ℹ️  ComfyUI가 이미 설치되어 있습니다: $ServicesDir\ComfyUI" -ForegroundColor Gray
}

# Stable Diffusion WebUI 설치
if (-not (Test-Path "stable-diffusion-webui")) {
    Write-Host "📦 Stable Diffusion WebUI 설치 중..." -ForegroundColor Yellow
    git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
    Write-Host "✅ Stable Diffusion WebUI 설치 완료" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Stable Diffusion WebUI가 이미 설치되어 있습니다: $ServicesDir\stable-diffusion-webui" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ 설치 완료!" -ForegroundColor Green
Write-Host ""
Write-Host "다음 명령으로 환경 변수를 설정하세요:" -ForegroundColor Yellow
Write-Host ""
Write-Host "`$env:COMFYUI_PATH = `"$ServicesDir\ComfyUI`"" -ForegroundColor White
Write-Host "`$env:WEBUI_PATH = `"$ServicesDir\stable-diffusion-webui`"" -ForegroundColor White
Write-Host ""
Write-Host "또는 .env 파일에 추가하세요:" -ForegroundColor Yellow
Write-Host "COMFYUI_PATH=$ServicesDir\ComfyUI" -ForegroundColor White
Write-Host "WEBUI_PATH=$ServicesDir\stable-diffusion-webui" -ForegroundColor White

