"""
FastAPI 애플리케이션 메인 진입점
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import (
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    validate_config
)
from app.api.v1.routes import api_router
from service_manager import get_service_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 설정 검증 (경고만 출력, 에러는 발생시키지 않음)
    try:
        validate_config(strict=False)
    except ValueError as e:
        print(f"⚠️ 설정 오류: {e}")
        print("일부 기능이 작동하지 않을 수 있습니다.")
    
    # 시작 시 서비스 매니저 초기화 및 서비스 시작
    print("🚀 서비스 매니저 초기화 중...")
    service_manager = get_service_manager()
    
    # 서비스 시작 (WebUI는 선택사항이므로 실패해도 계속 진행)
    results = service_manager.start_all()
    
    if results.get("comfyui"):
        print("✅ ComfyUI가 시작되었습니다")
    else:
        print("⚠️ ComfyUI 시작 실패 (이미지 생성 기능이 작동하지 않을 수 있습니다)")
    
    if results.get("webui"):
        print("✅ Stable Diffusion WebUI가 시작되었습니다")
    else:
        print("ℹ️ Stable Diffusion WebUI 시작 실패 (선택사항이므로 계속 진행합니다)")
    
    service_manager.start_health_check()
    print("✅ 서비스 매니저가 준비되었습니다")
    
    yield
    
    # 종료 시 서비스 정리
    print("🛑 서비스 종료 중...")
    if service_manager:
        service_manager.stop_health_check()
        service_manager.stop_all()
    print("✅ 모든 서비스가 종료되었습니다")


def create_application() -> FastAPI:
    """
    FastAPI 애플리케이션 생성
    
    Returns:
        FastAPI 인스턴스
    """
    app = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION,
        lifespan=lifespan
    )
    
    # CORS 미들웨어 추가
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # API 라우터 등록
    app.include_router(api_router, prefix="/api/v1")
    
    return app


# 애플리케이션 인스턴스 생성
app = create_application()


if __name__ == "__main__":
    import uvicorn
    from app.core.config import API_HOST, API_PORT
    
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=False,
        log_level="info"
    )

