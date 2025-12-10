# 프로젝트 아키텍처

## 디렉토리 구조

```
agent/
├── app/                          # 애플리케이션 메인 디렉토리
│   ├── __init__.py
│   ├── main.py                   # FastAPI 앱 진입점
│   │
│   ├── api/                      # API 라우터
│   │   └── v1/                   # API 버전 1
│   │       └── routes/            # 라우터 모듈
│   │           ├── __init__.py   # 라우터 통합
│   │           ├── generation.py  # 이미지 생성 API
│   │           ├── services.py   # 서비스 제어 API
│   │           └── health.py     # 헬스체크 API
│   │
│   ├── core/                     # 핵심 설정
│   │   ├── __init__.py
│   │   └── config.py            # 설정 관리
│   │
│   ├── models/                   # Pydantic 모델
│   │   ├── __init__.py
│   │   ├── requests.py           # 요청 모델
│   │   └── responses.py          # 응답 모델
│   │
│   ├── services/                 # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── image_generation.py    # 이미지 생성 서비스
│   │   └── service_control.py    # 서비스 제어 서비스
│   │
│   └── dependencies/            # 의존성 주입
│       ├── __init__.py
│       └── service_manager.py    # 서비스 매니저 의존성
│
├── service_manager.py            # 서비스 매니저
└── requirements.txt
```

## 아키텍처 패턴

### 1. 계층화 아키텍처 (Layered Architecture)

```
┌─────────────────────────────────┐
│      API Layer (Routes)         │  ← HTTP 요청/응답 처리
├─────────────────────────────────┤
│      Service Layer              │  ← 비즈니스 로직
├─────────────────────────────────┤
│      Model Layer                │  ← 데이터 모델
├─────────────────────────────────┤
│      Dependency Layer           │  ← 의존성 주입
└─────────────────────────────────┘
```

### 2. 의존성 주입 (Dependency Injection)

FastAPI의 `Depends`를 사용하여 의존성을 주입합니다:

```python
from app.dependencies.service_manager import ServiceManagerDep

@router.post("/generate")
def generate_image(
    request: PromptRequest,
    service_manager: ServiceManagerDep  # 의존성 주입
):
    ...
```

### 3. 서비스 레이어 패턴

비즈니스 로직을 서비스 클래스로 분리:

- `ImageGenerationService`: 이미지 생성 로직
- `ServiceControlService`: 서비스 제어 로직

## API 구조

### 엔드포인트

- `GET /api/v1/` - 헬스체크
- `POST /api/v1/generate` - 이미지 생성
- `GET /api/v1/services/status` - 서비스 상태 조회
- `POST /api/v1/services/comfyui/start` - ComfyUI 시작
- `POST /api/v1/services/comfyui/stop` - ComfyUI 중지
- `POST /api/v1/services/webui/start` - WebUI 시작
- `POST /api/v1/services/webui/stop` - WebUI 중지

### 응답 모델

모든 API는 Pydantic 모델을 사용하여 타입 안정성을 보장합니다:

- `PromptRequest`: 이미지 생성 요청
- `ImageGenerationResponse`: 이미지 생성 응답
- `ServiceStatusResponse`: 서비스 상태 응답
- `ServiceControlResponse`: 서비스 제어 응답
- `HealthResponse`: 헬스체크 응답

## 데이터 흐름

```
1. 클라이언트 요청
   ↓
2. API Router (routes/)
   ↓
3. Service Layer (services/)
   ↓
4. External Services (ComfyUI, WebUI)
   ↓
5. Service Layer (응답 처리)
   ↓
6. API Router (응답 반환)
   ↓
7. 클라이언트 응답
```

## 확장성

### 새로운 API 추가

1. `app/api/v1/routes/`에 새 라우터 파일 생성
2. `app/api/v1/routes/__init__.py`에 라우터 등록
3. 필요시 `app/services/`에 서비스 추가

### 새로운 서비스 추가

1. `app/services/`에 새 서비스 클래스 생성
2. 필요한 의존성을 `app/dependencies/`에 추가
3. 라우터에서 서비스 사용

## 모범 사례

1. **관심사 분리**: 각 레이어는 명확한 책임을 가짐
2. **의존성 주입**: 테스트 가능성과 유연성 향상
3. **타입 안정성**: Pydantic 모델로 런타임 검증
4. **에러 처리**: 적절한 HTTP 상태 코드 반환
5. **문서화**: OpenAPI/Swagger 자동 생성

