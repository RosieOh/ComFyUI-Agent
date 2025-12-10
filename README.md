# HyperWise Agent

ComfyUI와 Stable Diffusion WebUI를 자동으로 관리하고 통합하는 에이전트 시스템입니다.

## 주요 기능

- ✅ **자동 서비스 관리**: ComfyUI와 Stable Diffusion WebUI를 자동으로 시작/중지
- ✅ **헬스체크 및 자동 재시작**: 서비스가 다운되면 자동으로 재시작
- ✅ **통합 API**: 모든 기능을 하나의 API로 통합 관리
- ✅ **환경 변수 지원**: 설정을 환경 변수로 쉽게 변경 가능
- ✅ **설정 파일**: `app/core/config.py`를 통한 중앙 집중식 설정 관리

## 설치

### 1. 프로젝트 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. ComfyUI 및 Stable Diffusion WebUI 설치

**옵션 A: 자동 설치 스크립트 사용 (권장)**

```bash
# Linux/macOS
chmod +x install_services.sh
./install_services.sh

# Windows (PowerShell)
.\install_services.ps1
```

**옵션 B: 수동 설치**

ComfyUI와 Stable Diffusion WebUI를 별도로 설치하고 경로를 설정하세요:

```bash
# ComfyUI 설치 예시
git clone https://github.com/comfyanonymous/ComfyUI.git ~/ComfyUI
cd ~/ComfyUI
pip install -r requirements.txt

# Stable Diffusion WebUI 설치 예시
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git ~/stable-diffusion-webui
```

### 3. 환경 변수 설정

`.env` 파일을 생성하거나 환경 변수를 설정할 수 있습니다:

**방법 1: 환경 변수로 설정**

```bash
# Linux/macOS
export COMFYUI_PATH="/path/to/ComfyUI"
export WEBUI_PATH="/path/to/stable-diffusion-webui"

# Windows (PowerShell)
$env:COMFYUI_PATH = "C:\path\to\ComfyUI"
$env:WEBUI_PATH = "C:\path\to\stable-diffusion-webui"
```

**방법 2: .env 파일 사용 (권장)**

`.env.example`을 `.env`로 복사하고 경로를 설정하세요:

```bash
cp .env.example .env
# .env 파일을 편집하여 COMFYUI_PATH와 WEBUI_PATH 설정
```

# 서비스 매니저 설정
export AUTO_START_SERVICES=true
export HEALTH_CHECK_INTERVAL=10

# API 서버 설정
export API_HOST=0.0.0.0
export API_PORT=8000

# 이미지 생성 설정
export DEFAULT_MODE=high_quality  # fast, balanced, high_quality
export DOWNLOAD_DIR=./downloads
```

또는 `config.py` 파일을 직접 수정할 수 있습니다.

## 사용 방법

### 0. 사전 준비 (처음 한 번만)

```bash
# 프로젝트 루트 디렉토리로 이동
cd /Users/sirious920/Desktop/DevOps_RosieOh/Project/agent

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip3 install -r requirements.txt
```

> ⚠️ **중요**: 반드시 **프로젝트 루트 디렉토리**에서 실행하세요. `app/` 디렉토리 안에서 실행하면 안 됩니다!

### 1. 서버 시작

**macOS/Linux (권장):**
```bash
./run.sh
```

**수동 실행:**
```bash
# 가상환경 활성화 (있는 경우)
source venv/bin/activate

# 서버 시작
python3 -m app.main
# 또는
python3 app/main.py
```

서버가 시작되면 자동으로 ComfyUI와 Stable Diffusion WebUI가 시작됩니다.

**접속 정보:**
- API 문서 (Swagger): http://localhost:8000/docs
- API 문서 (ReDoc): http://localhost:8000/redoc
- API 엔드포인트: http://localhost:8000/api/v1/

### 2. API 사용

#### 이미지 생성

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "frosted glass vegan shampoo bottle product commercial",
    "mode": "high_quality"
  }'
```

#### 서비스 상태 확인

```bash
# 헬스체크
curl http://localhost:8000/api/v1/

# 서비스 상태
curl http://localhost:8000/api/v1/services/status
```

#### 서비스 제어

```bash
# ComfyUI 시작
curl -X POST http://localhost:8000/api/v1/services/comfyui/start

# ComfyUI 중지
curl -X POST http://localhost:8000/api/v1/services/comfyui/stop

# WebUI 시작
curl -X POST http://localhost:8000/api/v1/services/webui/start

# WebUI 중지
curl -X POST http://localhost:8000/api/v1/services/webui/stop
```

### 3. API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Python에서 직접 사용

```python
from service_manager import ServiceManager

# 서비스 매니저 사용
with ServiceManager() as manager:
    # 서비스 상태 확인
    status = manager.get_status()
    print(status)
    
    # 이미지 생성 등 작업 수행
    # ...
```

## API 엔드포인트

### `GET /api/v1/`
헬스체크

**응답:**
```json
{
  "status": "HyperWise Llama Agent running",
  "services": {
    "comfyui": {
      "running": true,
      "port": 8188,
      "url": "http://127.0.0.1:8188"
    },
    "webui": {
      "running": true,
      "port": 7860,
      "url": "http://127.0.0.1:7860"
    }
  }
}
```

### `POST /api/v1/generate`
이미지 생성 요청

**요청 본문:**
```json
{
  "prompt": "이미지 생성 프롬프트",
  "mode": "high_quality"  // fast, balanced, high_quality
}
```

**응답:**
```json
{
  "success": true,
  "images": ["path/to/image1.png", "path/to/image2.png"],
  "message": "2개의 이미지가 생성되었습니다"
}
```

### `GET /api/v1/services/status`
서비스 상태 조회

**응답:**
```json
{
  "services": {
    "comfyui": {
      "running": true,
      "port": 8188,
      "url": "http://127.0.0.1:8188"
    },
    "webui": {
      "running": true,
      "port": 7860,
      "url": "http://127.0.0.1:7860"
    }
  },
  "health_check": true
}
```

### `POST /api/v1/services/{service}/start`
서비스 시작 (`{service}`: `comfyui` 또는 `webui`)

### `POST /api/v1/services/{service}/stop`
서비스 중지 (`{service}`: `comfyui` 또는 `webui`)

## 프로젝트 구조

```
agent/
├── app/                          # 애플리케이션 메인 디렉토리
│   ├── main.py                   # FastAPI 앱 진입점
│   │
│   ├── api/                      # API 라우터
│   │   └── v1/
│   │       └── routes/           # 라우터 모듈
│   │           ├── generation.py # 이미지 생성 API
│   │           ├── services.py   # 서비스 제어 API
│   │           └── health.py     # 헬스체크 API
│   │
│   ├── core/                     # 핵심 설정
│   │   └── config.py            # 설정 관리
│   │
│   ├── models/                   # Pydantic 모델
│   │   ├── requests.py           # 요청 모델
│   │   └── responses.py          # 응답 모델
│   │
│   ├── services/                 # 비즈니스 로직
│   │   ├── image_generation.py   # 이미지 생성 서비스
│   │   └── service_control.py   # 서비스 제어 서비스
│   │
│   └── dependencies/             # 의존성 주입
│       └── service_manager.py   # 서비스 매니저 의존성
│
├── service_manager.py            # 서비스 관리 클래스
├── requirements.txt              # Python 의존성
├── .env.example                  # 환경 변수 예제 파일
├── install_services.sh           # 서비스 자동 설치 스크립트 (Linux/macOS)
├── install_services.ps1          # 서비스 자동 설치 스크립트 (Windows)
├── ARCHITECTURE.md               # 아키텍처 문서
└── downloads/                    # 생성된 이미지 저장 디렉토리

# 참고: ComfyUI와 Stable Diffusion WebUI는 프로젝트 외부에 설치됩니다
# 환경 변수 COMFYUI_PATH와 WEBUI_PATH로 경로를 지정하세요
```

자세한 아키텍처 설명은 [ARCHITECTURE.md](ARCHITECTURE.md)를 참조하세요.

## 문제 해결

### 서비스가 시작되지 않는 경우

1. **경로 설정 확인**:
   ```bash
   python config.py
   ```
   환경 변수 `COMFYUI_PATH`와 `WEBUI_PATH`가 올바르게 설정되어 있는지 확인하세요.

2. **포트 충돌 확인**:
   ```bash
   # Linux/macOS
   lsof -i :8188  # ComfyUI
   lsof -i :7860  # WebUI
   
   # Windows
   netstat -ano | findstr :8188
   netstat -ano | findstr :7860
   ```

3. **서비스 설치 확인**:
   - ComfyUI와 WebUI가 올바른 경로에 설치되어 있는지 확인
   - `install_services.sh` 또는 `install_services.ps1`을 실행하여 자동 설치

4. **로그 확인**:
   - 서버 콘솔 출력 확인
   - ComfyUI/WebUI의 가상환경이 올바르게 설정되어 있는지 확인

### 서비스가 자동으로 재시작되지 않는 경우

- `AUTO_START_SERVICES` 환경 변수가 `true`로 설정되어 있는지 확인
- 헬스체크 간격을 조정: `HEALTH_CHECK_INTERVAL=10` (초)

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

